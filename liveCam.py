import asyncio
import os, re, time, shutil
from datetime import datetime
import cv2, pygame

# ML
import numpy as np
import tensorflow as tf

# Image
import imageio
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont

# OSC
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer

# NDI
import NDIlib as ndi
from lip_read import LipRead
from lipnet.lipreading.videos import Video

# BASE_PATH = "/Users/baggeunsu/fwo_lipnet_plus" # 맥미니에서 실행할 때
BASE_PATH = "/Users/giy/Projects/fwo_lipnet_plus" # 노트북에서 실행할 때
STORAGE_PATH = '/Users/NetworkFolder/image_server'
AUDIO_STORAGE_PATH = '/Users/NetworkFolder/audio_files'

GUIDE_MOVIE = BASE_PATH + '/videofiles/guide_new.mp4'
# GUIDE_AUDIO = BASE_PATH + '/videofiles/guide_44.mp3'
# GUIDE_AUDIO = BASE_PATH + '/videofiles/guide_43.mp3'
GUIDE_AUDIO = BASE_PATH + '/videofiles/guide_new.mp3'

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load(GUIDE_AUDIO)

VIEW_SCALE = 1
ASYNC_AWAIT = 0.00001

ARCHIVE_MAX_NUM = 120 

# 상태를 나타내는 global 변수들
is_wait_mode = True # 1: True / 0: False 
is_guide_mode = True # 녹화 시작 전 안내 영상 송출
is_count_mode = False 
is_rec_mode = False 
is_play_mode = False # 녹화된 사진과 오디오가 재생되고 있는지
audio_play = False
is_prediction_done = False

start_time = None
mov_writer = None
current_directory_path  = ""
current_audiofile_path  = ""

# OSC
# Receive
# RECVIVING_IP = "127.0.0.1" # receiving ip
RECVIVING_IP = "192.168.50.152" # receiving ip
RECVIVING_PORT = 1337 # receiving port

# Send
OSC_ADDR_LOCAL = "127.0.0.1"
OSC_ADDR = "192.168.50.153"
OSC_PORT = 30000
OSC_ADDR_2 = "192.168.50.152"
OSC_PORT_2 = 30002


# NDI
send_settings = ndi.SendCreate()
send_settings.ndi_name = 'ndi-python'
ndi_send = ndi.send_create(send_settings)
video_frame = ndi.VideoFrameV2()


# Ui
text_left = 60
text_top = 70
text_size_ = 45



def delete_folder(path):
    try:
        # 지정된 경로의 폴더를 삭제
        shutil.rmtree(path)
        print(f"{path} 폴더를 삭제했습니다.")
        
    except Exception as e:
        print(f"오류 발생: {e}")


def delete_file(file_path):
    try:
        # 파일 삭제
        os.remove(file_path)
        print(f"{file_path}을(를) 삭제했습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")


# opencv를 이용해 Round rect를 그리는 함수
# For Details Reference Link:
# http://stackoverflow.com/questions/46036477/drawing-fancy-rectangle-around-face
def draw_border(img, pt1, pt2, color, thickness, r, d):
    x1,y1 = pt1
    x2,y2 = pt2

    # Top left
    cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
    cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)

    # Top right
    cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
    cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)

    # Bottom left
    cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
    cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)

    # Bottom right
    cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
    cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)


def sort_folders_by_datetime(folder_names):
    # 날짜와 시간을 기준으로 폴더 이름들을 정렬
    sorted_folders = sorted(folder_names, key=lambda x: datetime.strptime(x, '%y_%m_%d_%H_%M_%S'))
    # sorted_folders = sorted(folder_names, key=lambda x: datetime.strptime(x, '%y %m %d %H %M %S'))
    # sorted_folders = sorted(folder_names, key=lambda x: datetime.strptime(x, '%y년_%m월_%d일_%H시_%M분_%S초'))

    return sorted_folders
    

def sort_audio_files_by_datetime(folder_names):
    # 날짜와 시간을 기준으로 폴더 이름들을 정렬
    sorted_folders = sorted(folder_names, key=lambda x: datetime.strptime(x, '%y%m%d%H%M%S'))
    # sorted_folders = sorted(folder_names, key=lambda x: datetime.strptime(x, '%y %m %d %H %M %S'))
    # sorted_folders = sorted(folder_names, key=lambda x: datetime.strptime(x, '%y년_%m월_%d일_%H시_%M분_%S초'))

    return sorted_folders


# OSC receive handler
def wait_mode_handler(address, *args):
    global is_wait_mode
    print(f"wait_mode_handler: {address}: {args}")
    is_wait_mode = bool(args[0])
    # print(is_wait_mode)

def play_mode_handler(address, *args):
    global is_play_mode, is_count_mode, start_time
    print(f"play_mode_handler: {address}: {args}")
    is_play_mode = bool(args[0])
    if is_play_mode == False:
        is_count_mode = True
        start_time = cv2.getTickCount()
    # print(is_play_mode)

def audio_play_handler(address, *args):
    global audio_play 
    print(f"audio_play: {address}: {args}")
    audio_play = bool(args[0])


# OSC Server(Async) setup
dispatcher = Dispatcher()
dispatcher.map("/is_wait_mode", wait_mode_handler) # Address pattern, handler function
dispatcher.map("/is_play_mode", play_mode_handler) # Address pattern, handler function
dispatcher.map("/audio_play", audio_play_handler) # Address pattern, handler function


# cv를 이용해 한글을 표시하는 함수
def putTextKor(src, text, pos=(10, 140), font_size=80, font_color=(263, 20, 216), font_thickness=3) :
    global VIEW_SCALE

    # FONT_PATH = BASE_PATH + '/IBM_Plex_Sans_KR/IBMPlexSansKR-Regular.ttf'
    FONT_PATH = BASE_PATH + '/IBM_Plex_Sans_KR/IBMPlexSansKR-Bold.ttf'
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = VIEW_SCALE * 3 

    # text = "안녕하세요"

    if pos == None:
        # 텍스트 크기 얻기
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        # print(f'text_size: {text_size}')

        # 이미지 중앙에 텍스트를 출력할 위치 계산
        # print(f'0: {src.shape[0]}') # height
        # print(f'1: {src.shape[1]}') # width
        text_x = (src.shape[1] - text_size[0]//3) // 2 - 20 # 왠지 모르겠지만 text_size를 3으로 나누어야 화면의 가운데가 된다
        text_y = src.shape[0] - 600  # 150 from bottom 

    else:
        text_x = pos[0]
        text_y = pos[1]

    img_pil = Image.fromarray(src)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(FONT_PATH, font_size)
    draw.text((text_x, text_y), text, font=font, fill=font_color, font_thickness=font_thickness)
    return np.array(img_pil)


# 안내 영상 파일 재생을 위한 함수
async def play_guide_video_in_existing_window(file_path, window_name, loop=False):
    global is_wait_mode, is_guide_mode, is_rec_mode, is_count_mode, is_prediction_done
    # is_key_pressed = False

    # 오디오 재생
    # pygame.mixer.music.play()
    send_osc_message(OSC_ADDR_2, OSC_PORT, "/guide_play", 1) # vib speaker


    cap_mov = cv2.VideoCapture(file_path)

    if not cap_mov.isOpened():
        print("Error: Couldn't open video file.")
        return

    while True:
        
        ret, frame = cap_mov.read()

        if ret:
            # NDI send
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            video_frame.data = img
            video_frame.FourCC = ndi.FOURCC_VIDEO_TYPE_BGRX
            ndi.send_send_video_v2(ndi_send, video_frame)

        if not ret:
            is_guide_mode = False
            is_count_mode = True
            break

        cv2.imshow(window_name, frame)

        # TEST
        # 'g' 키를 통해 대기모드가 종료될 때
        key = cv2.waitKey(1) # 영상 재생의 fps 에 결정적 영향을 준다. 영상과 소리 사이의 싱크를 맞추려면 최소화 해야 한다
        if key == 27:
            # pygame.mixer.music.stop()
            send_osc_message(OSC_ADDR_LOCAL, OSC_PORT, "/guide_stop", 1)
            # is_key_pressed = True
            is_wait_mode = False 
            is_rec_mode = False
            is_count_mode = False
            is_guide_mode = False
            is_prediction_done = False
            break

        await asyncio.sleep(ASYNC_AWAIT)

    cap_mov.release()



# 대기모드시 영상파일 재생을 위한 함수
async def play_wait_video_in_existing_window(file_path, window_name, loop=True):
    global is_wait_mode, is_guide_mode, is_rec_mode, is_count_mode, is_prediction_done
    is_key_pressed = False
    cap_mov = cv2.VideoCapture(file_path)

    if not cap_mov.isOpened():
        print("Error: Couldn't open video file.")
        return

    while True:
        ret, frame = cap_mov.read()

        if ret:
            # NDI send
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            video_frame.data = img
            video_frame.FourCC = ndi.FOURCC_VIDEO_TYPE_BGRX
            ndi.send_send_video_v2(ndi_send, video_frame)

        if not ret:
            if loop:
                cap_mov.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                break

        cv2.imshow(window_name, frame)

        # OSC를 통해 대기모드가 종료될 때
        if is_wait_mode == False and is_key_pressed == False:
            is_wait_mode = False 
            is_rec_mode = False
            is_count_mode = False
            is_prediction_done = False
            is_guide_mode = True
            break

        # 'm' 키를 통해 대기모드가 종료될 때
        key = cv2.waitKey(1)
        if key == 27:
            is_key_pressed = True
            is_wait_mode = False 
            is_rec_mode = False
            is_count_mode = False
            is_prediction_done = False
            is_guide_mode = True
            break

        await asyncio.sleep(ASYNC_AWAIT)

    cap_mov.release()



# OSC
def send_osc_message(osc_server_ip, osc_server_port, osc_address, osc_message):
    """
    OSC 메시지를 보내는 함수

    Parameters:
    - osc_server_ip (str): OSC 서버의 IP 주소
    - osc_server_port (int): OSC 서버의 포트 번호
    - osc_address (str): OSC 메시지의 주소
    - osc_message: 전송할 메시지

    Returns:
    None
    """
    # OSC 클라이언트 생성
    client = udp_client.SimpleUDPClient(osc_server_ip, osc_server_port)

    # OSC 메시지 보내기
    client.send_message(osc_address, osc_message)



# 촬영 중 audio 파일 저장할 폴더 생성
def create_audio_output_directory():
    global current_audiofile_path 

    # 현재 날짜와 시간을 이용하여 디렉토리 이름 생성
    # timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
    current_datetime = datetime.now()


    # 년, 월, 일, 시간, 분, 초를 변수로 추출
    year = current_datetime.strftime('%y')
    month = current_datetime.strftime('%m')
    day = current_datetime.strftime('%d')
    hour = current_datetime.strftime('%H')
    minute = current_datetime.strftime('%M')
    second = current_datetime.strftime('%S')

    # kor_name = f'{year}년_{month}월_{day}일_{hour}시_{minute}분_{second}초'
    # kor_name = f'{year}_{month}_{day}_{hour}_{minute}_{second}'
    kor_name = f'{year}{month}{day}{hour}{minute}{second}'
    # print(kor_name)

    output_directory = AUDIO_STORAGE_PATH + '/' + f'{kor_name}' + '.wav'
    current_audiofile_path = output_directory
    # print(output_directory)

    # try:
    #     # 디렉토리 생성
    #     os.makedirs(output_directory, exist_ok=True)
    # except PermissionError as e:
    #     print(f"Error creating directory: {e}")
    #     # 여기에 추가적인 에러 처리 로직을 작성할 수 있음

    return output_directory



# 영상 촬영 중 일정 간격 이미지 저장할 폴더 생성
# captured_frames_YYMMDD_HHMMSS 의 형태
def create_output_directory():
    global current_directory_path 

    # 현재 날짜와 시간을 이용하여 디렉토리 이름 생성
    # timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
    current_datetime = datetime.now()


    # 년, 월, 일, 시간, 분, 초를 변수로 추출
    year = current_datetime.strftime('%y')
    month = current_datetime.strftime('%m')
    day = current_datetime.strftime('%d')
    hour = current_datetime.strftime('%H')
    minute = current_datetime.strftime('%M')
    second = current_datetime.strftime('%S')

    # kor_name = f'{year}년_{month}월_{day}일_{hour}시_{minute}분_{second}초'
    # kor_name = f'{year}_{month}_{day}_{hour}_{minute}_{second}'
    kor_name = f'{year}_{month}_{day}_{hour}_{minute}_{second}'
    # print(kor_name)

    output_directory = os.path.join(STORAGE_PATH, f'{kor_name}')
    current_directory_path = output_directory

    try:
        # 디렉토리 생성
        os.makedirs(output_directory, exist_ok=True)
    except PermissionError as e:
        print(f"Error creating directory: {e}")
        # 여기에 추가적인 에러 처리 로직을 작성할 수 있음

    return output_directory


# 영상 파일의 frame count 세는 함수
def count_frames(video_path):
    # VideoCapture 객체 생성
    cap = cv2.VideoCapture(video_path)

    # 프레임 수 확인
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # VideoCapture 객체 해제
    cap.release()

    return frame_count


# 비디오 파일에서 입모양 추출, ML에 전달할 데이터로 만드는 함수
def load_frames_from_video(filepath:str):
    print(f'load_frames_from_video() path: {filepath}')

    fc = count_frames(filepath)
    print(f'load_frames_from_video frame count of input video: {fc}')
    # print ("Processing: {}".format(filepath))
    FACE_PREDICTOR_PATH = BASE_PATH + '/predictors/shape_predictor_68_face_landmarks.dat'
    video = Video(vtype='face', face_predictor_path=FACE_PREDICTOR_PATH).from_video(filepath)    
    video_i = ((video.mouth - np.min(video.mouth)) / (np.max(video.mouth) - np.min(video.mouth)) * 255).astype(np.uint8)
    # video_i = (video.mouth * 255).astype(np.uint8)    
    frames = []
    for frame in video_i:
        # print(frame)
        # print(frame.shape) # (50, 100, 3)
        if frame is not None:
            frame = frame[0:50,0:100,:]
            frame = tf.image.rgb_to_grayscale(frame)
            # print(frame.dtype)
            # print(frame)
            # print(frame.shape)
            frames.append(frame)
        else:
            print("load_frames_from_video() path" + path)

    mean = tf.math.reduce_mean(frames)
    std = tf.math.reduce_std(tf.cast(frames, tf.float32))
    # print(f'mean: {mean} - std: {std}')
    rslt = tf.cast((frames - mean), tf.float32) / std
    error_face = video.face_detect_failed
    error_mouth = video.mouth_detection_chopped
    return rslt, error_face, error_mouth # 각 데이터에서 평균을 뺀 다음, 표준편차로 나눈다 --> 데이터 정규화


# 폴더 안에 .wav 파일들의 이름 가져오는 함수
def get_wav_files_in_folder(folder_path):
    wav_files = []
    pattern = re.compile(r"\d{12}\.wav")  # 12자리 숫자 다음에 .wav가 있는지 확인하는 정규표현식

    for file in os.listdir(folder_path):
        if pattern.match(file):
            wav_files.append(file.split('.')[-2])
    return wav_files



# ---------------------- MAIN -----------------------
async def loop():

    # countdown 시 진동을 만들기 위한 변수
    next_count_down = 3

    # 입모양 인식시 에러 종류 별 상태 저장 변수
    error_face = False
    error_mouth = False

    # 입술 인식 에러 표시를 위한 타이머
    err_start_time = 0
    err_elapsed_time = 0  

    # 결과 자막 표시를 위한 타이머
    sub_start_time = 0 
    sub_elapsed_time = 0
    
    COUNT_DOWN_START = 3 # 카운트 다운 시작 값

    REC_FRAME = 75 # 녹화할 총 frame 수
    SUBTITLE_DUR = 5  # 자막이 표시될 시간 (초)
    ERR_WARN_DUR = 3  # 자막이 표시될 시간 (초)

    # 대기 화면에서 재생될 영상
    WAIT_MOVIE = BASE_PATH + '/videofiles/waiting_960.mp4'
    REC_FILE = BASE_PATH + '/camout/output.mp4' # 영상 파일 저장 경로
    SAVE_INTERVAL = 5 # frame 이미지 저장 사이 간격

    frame_count = 0
    predict_rslt = ""

    # lip read
    lipRead = LipRead()
    lipRead.init()

    # 카메라를 연결합니다.
    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

    # 새로운 해상도 설정
    width = 1280 
    height = 1280 
    # height = 320 
    fps = 25

    # 웹캠의 입력 해상도 조정
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # NDI Sending Res
    video_frame.xres = 1280
    video_frame.yres = 1280
    
    # 창을 생성합니다.
    cv2.namedWindow('Camera Feed', cv2.WINDOW_GUI_NORMAL)
    # cv2.moveWindow('Camera Feed', 500, 0) # for test 
    cv2.moveWindow('Camera Feed', 2000, 1400) # for real

    # 항상 화면 맨 위에 표시되도록 설정합니다.
    cv2.setWindowProperty('Camera Feed', cv2.WND_PROP_TOPMOST, 1)

    # 비디오 라이터 생성
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')

    # 바탕 이미지 불러오기
    # background_image = cv2.imread(BASE_PATH + '/background_image.png')

    global is_wait_mode, is_guide_mode, is_rec_mode, is_play_mode, is_count_mode, is_prediction_done, mov_writer, start_time
    global current_directory_path, current_audiofile_path
    while True:
        
        # print(f'is_wait_mode: {is_wait_mode}')

        # 프레임을 읽어옵니다.
        ret, frame = cap.read()
        # print("new frame!")

        # 읽어온 프레임이 없으면 종료합니다.
        if not ret:
            break

        # # 카메라 프레임 width / height 확인
        # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # # 가져온 너비와 높이 출력
        # print("Width:", width)
        # print("Height:", height)


        # 카메라 영상 비율 조정 --> 윈도우의 비율도 결정됨
        # 영상의 가로와 세로 중 작은 값을 구함
        min_dimension = min(frame.shape[0], frame.shape[1])
        # print(f'dimension: {min_dimension}') # width, height 중 작은 것

        # 중앙 부분을 잘라내어 1:1 비율로 만듦
        start_x = (frame.shape[1] - min_dimension) // 2
        start_y = (frame.shape[0] - min_dimension) // 2
        end_x = start_x + min_dimension
        end_y = start_y + min_dimension

        # print(f'sx: {start_x} / sy: {start_y} / ex: {end_x} / ey: {end_y}')
        frame = frame[start_y:end_y, start_x:end_x]
        width = height = frame.shape[1]
        frame = cv2.resize(frame, (width, height)) # 영상 크기 조절
        frame = cv2.flip(frame, 1) # 좌우 반전 적용


        key = cv2.waitKey(1) & 0xFF # key 입력 받기

        # countdown 전에 안내 영상 내보내기        
        if is_guide_mode == True and is_play_mode == False and is_wait_mode == False:
            await play_guide_video_in_existing_window(GUIDE_MOVIE, 'Camera Feed')
            is_guide_mode = False
            is_count_mode = True
            start_time = cv2.getTickCount()
            print(f'start_time!!: {start_time}')
            

        # 'c' 키를 누르면 count 모드로 전환
        if key == ord('c'):
            if is_count_mode == True:
                is_count_mode = False 
            else:
                is_count_mode = True 
                # print(f'is_count_mode: {is_count_mode}')
                start_time = cv2.getTickCount()


        # 카운트 모드일 때 count down 숫자 표시
        if is_count_mode == True and is_play_mode == False and is_prediction_done == False:
            send_osc_message(OSC_ADDR_2, OSC_PORT, "/make_vib_long", 0)
            frame_count = 0 # frame_count 초기화
            is_prediction_done = False
            elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
            count_down = COUNT_DOWN_START - int(elapsed_time)

            # 카운트다운에 맞춰 진동 만들어 내기
            if count_down == 3 and next_count_down == 3:
                send_osc_message(OSC_ADDR_2, OSC_PORT, "/make_vib", 1)
                next_count_down = 2

            elif count_down == 2 and next_count_down == 2:
                send_osc_message(OSC_ADDR_2, OSC_PORT, "/make_vib", 1)
                next_count_down = 1

            elif count_down == 1 and next_count_down == 1:
                send_osc_message(OSC_ADDR_2, OSC_PORT, "/make_vib", 1)
                next_count_down = 0

            elif count_down == 0 and next_count_down == 0:
                send_osc_message(OSC_ADDR_2, OSC_PORT, "/make_vib", 1)
                next_count_down = -1 


            # 카운트 다운이 끝났을 때
            if count_down < 0:
                next_count_down = 3

                print("녹화 시작")
                mov_writer = cv2.VideoWriter(REC_FILE, fourcc, fps, (width, height))
                # print(mov_writer)

                start_time = cv2.getTickCount()

                # 프레임 이미지 저장할 폴더 생성
                output_directory = create_output_directory()
                audio_output_directory = create_audio_output_directory()
                send_osc_message(OSC_ADDR, OSC_PORT, "/current_directory", output_directory + '/')
                send_osc_message(OSC_ADDR_2, OSC_PORT, "/current_directory", output_directory.split('/')[-1] + '/')

                if audio_play == False:
                    send_osc_message(OSC_ADDR_LOCAL, OSC_PORT, "/audio_directory", audio_output_directory)
                # print(output_directory)

                # 다음 프레임 부터 rec_mode로 넘어감
                is_count_mode = False 
                is_rec_mode = True 
                
                timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
                send_osc_message(OSC_ADDR, OSC_PORT, "/record_start", timestamp)
                send_osc_message(OSC_ADDR_2, OSC_PORT_2, "/record_start", timestamp)
                send_osc_message(OSC_ADDR_LOCAL, OSC_PORT, "/record_start", timestamp)
                



            # 카운트다운이 진행 중일 때
            if count_down >= 0: # 3, 2, 1, 0 까지 표시

                # 카운트 다운 숫자 표시하기
                text = str(count_down)
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = VIEW_SCALE * 5.5
                font_thickness = 10 * VIEW_SCALE
                text_color = (0, 0, 255)  # BGR format

                # 텍스트 크기 얻기
                text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
                # print(f'text_size: {text_size}')

                # 화면의 가운데 위치에서 글자의 가로 크기의 절반 만큼을 뺀다(글자가 표시되는 기준이 글자의 왼쪽 하단 모서리)
                text_position = ((width // 2) - (text_size[0] // 2), int(height / 2 + 50))
                cv2.putText(frame, text, text_position, font, font_scale, text_color, font_thickness, cv2.LINE_AA)


                # 화면의 가운데 사각형 그리기
                # 중심 좌표와 크기
                center = (frame.shape[1] // 2, frame.shape[0] // 2)  # 이미지 중심 좌표

                # pt1과 pt2 계산
                r_width = width * 2 // 3
                r_height = height * 2 // 3

                pt1 = (center[0] - r_width // 2, center[1] - r_height // 2)
                pt2 = (center[0] + r_width // 2, center[1] + r_height // 2)
                # print(f'pt1: {pt1} / pt2: {pt2}')

                rect_color = (0, 255, 0)  # BGR format (green)
                rect_thickness = 1 * VIEW_SCALE
                cv2.rectangle(frame, pt1, pt2, rect_color, rect_thickness)

                # rounded corners, yellow
                draw_border(frame, pt1, pt2, (127,255,255), 4, 5, 10)





        # 녹화 중일 때
        if is_rec_mode:

            # 75 frame 채워지는 동안
            if frame_count < REC_FRAME - 1:
                send_osc_message(OSC_ADDR_2, OSC_PORT, "/make_vib_long", 0)

                # if frame_count % 5 == 0:
                    # send_osc_message(OSC_ADDR_2, OSC_PORT, "/make_vib", 1) 

                if is_wait_mode == True: # 관객이 사라지면
                    print('녹화 중단!!')

                    # record가 중단되면 시간을 OSC로 전송 --> 이 때는 영상 및 소리 재생 없음
                    timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
                    send_osc_message(OSC_ADDR, OSC_PORT, "/record_interrupt", timestamp)
                    send_osc_message(OSC_ADDR_2, OSC_PORT_2, "/record_interrupt", timestamp)
                    send_osc_message(OSC_ADDR_LOCAL, OSC_PORT, "/record_interrupt", timestamp)

                    mov_writer.release() # 파일 저장

                    
                    # remove interrupted image folder & audio file                    
                    print(current_directory_path)
                    print(current_audiofile_path)

                    delete_folder(current_directory_path)
                    delete_file(current_audiofile_path)
                    

                    mov_writer = None
                    is_rec_mode = False 
                    is_prediction_done = False


            # 녹화 끝나기 직전 프레임
            elif frame_count == REC_FRAME - 1:
                send_osc_message(OSC_ADDR_2, OSC_PORT, "/make_vib_long", 1)
                print(f'{frame_count} frame 녹화 완료')

            # 75frame이 채워지면 녹화 종료
            elif frame_count >= REC_FRAME: # 저장은 frame_count가 74일 때까지만 되어야 한다

                print(f'{frame_count} frame 녹화 완료')

                # record가 끝나면 현재 시간을 OSC로 전송
                timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
                send_osc_message(OSC_ADDR_LOCAL, OSC_PORT, "/record_end", timestamp)
                # to mac mini 2 and 3
                send_osc_message(OSC_ADDR, OSC_PORT, "/record_end", timestamp)
                send_osc_message(OSC_ADDR_2, OSC_PORT_2, "/record_end", timestamp)




                mov_writer.release() # 파일 저장
                mov_writer = None
                is_rec_mode = False 

                if os.path.exists(REC_FILE): # 영상 파일 저장된 것이 확인 되면
                    calc_frames = []
                    print(f'load_frames_from_video: {REC_FILE}')
                    calc_frames, error_face, error_mouth = load_frames_from_video(REC_FILE)
                    print(f'error_f: {error_face} / error_m: {error_mouth}')
                    print(f'shape of calc_frames: {calc_frames.shape}')

                    send_osc_message(OSC_ADDR_2, OSC_PORT, "/make_vib_long", 0)

                    if error_face == True or error_mouth == True:
                        print('입술 인식 에러! 다시 한 번 인식을 시도해 주세요.')

                        timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
                        send_osc_message(OSC_ADDR, OSC_PORT, "/record_interrupt", timestamp)
                        send_osc_message(OSC_ADDR_2, OSC_PORT_2, "/record_interrupt", timestamp)
                        send_osc_message(OSC_ADDR_LOCAL, OSC_PORT, "/record_interrupt", timestamp)

                        err_start_time = time.time()

                    else:
                        # 주어진 폴더 경로에서 하위 폴더들의 이름을 가져옴
                        wav_files = get_wav_files_in_folder(AUDIO_STORAGE_PATH)
                        # print(wav_files)

                        sorted_audio_list = sort_audio_files_by_datetime(wav_files)
                        # print(sorted_audio_list)
                        three_same = []
                        # 맨 마지막 녹음된 오디오 파일의 이름만 담긴 리스트를 만들어 전달
                        three_same.append(sorted_audio_list[-1])
                        three_same.append(sorted_audio_list[-1])
                        three_same.append(sorted_audio_list[-1])
                        # print(three_same)
                        
                        send_osc_message(OSC_ADDR_2, 30001, "/audio_files", three_same)

                        
 
                        # 주어진 폴더 경로에서 하위 폴더들의 이름을 가져옴
                        subdirectories = [name for name in os.listdir(STORAGE_PATH)
                        if os.path.isdir(os.path.join(STORAGE_PATH, name))]
                            # return subdirectories
                        sorted_dir_list = sort_folders_by_datetime(subdirectories)

                        # 아카이브에 표시될 리스트 개수 제한
                        if len(sorted_dir_list) > ARCHIVE_MAX_NUM:
                            added = ARCHIVE_MAX_NUM - 56

                            combined_list = sorted_dir_list[:56] + sorted_dir_list[-added:]
                            sorted_dir_list = combined_list
                            print(combined_list)

                        # print(subdirectories)
                        # print(sorted_dir_list)
                        # output_string = input_string.replace('_', ' ')
                        no_underbar_list = [name.replace('_', ' ') for name in sorted_dir_list]
                        send_osc_message(OSC_ADDR, OSC_PORT, "/folder_names", no_underbar_list)



                        # 입술 인식 결과 예측
                        predict_rslt = lipRead.predict(calc_frames)
                        # print(predict_rslt)
                        # predict_rslt = lipRead.translate(rslt)

                        is_prediction_done = True
                        is_play_mode = True # 녹화된 영상과 음성이 재생중이다 --> 새로운 녹화를 시작하지 않는다 *important*

                        sub_start_time = time.time()

                
                    '''
                    # TEST
                    # 인식된 입모양 plot 
                    if len(calc_frames) == 75:

                        # 3 x 2 배열 
                        fig, axes = plt.subplots(3, 2, figsize=(5, 3))

                        # 각 프레임을 순회하며 표시
                        for i in range(3):
                            for j in range(2):
                                idx = i * 2 + j
                                axes[i, j].imshow(calc_frames[idx * 12, :, :, 0])  # cmap은 흑백 이미지의 경우 'gray'를 사용
                                axes[i, j].axis('on')  # 이미지의 축을 숨김
                                axes[i, j].set_title(f'Frame {idx * 12 + 1}')

                        plt.pause(0.5)
                        plt.draw()

                        # gif 애니메이션 저장
                        imageio.mimsave('./camout/animation.gif', (calc_frames * 255).numpy().astype('uint8').squeeze(), fps=fps)
                    '''



            # 영상 저장
            if mov_writer != None: # 영상이 저장되고 있다면

                # 일정 간격마다 이미지 저장
                if frame_count % SAVE_INTERVAL == 0:

                    # 이미지 파일 경로 설정
                    formatted_number = f"{frame_count:03d}"
                    index_number = frame_count // SAVE_INTERVAL + 1
                    image_path = os.path.join(output_directory, f'{index_number:02d}.jpg')

                    # 이미지 저장
                    cv2.imwrite(image_path, frame)
                    # print(f'Frame {frame_count} saved at {image_path}')

                # print('writing frame..')
                mov_writer.write(frame)
                frame_count += 1
                # print(f'Recorded frame count: {frame_count}')


            if frame_count < REC_FRAME - 1:
                # 영상에 녹화 안되는 부분
                # 텍스트 추가 (현재 녹화 중임을 알려주는 메시지)
                text = "녹화중 입니다…"
                text_color = (0, 0, 255)  # BGR format

                # 화면의 가운데 위치에서 글자의 가로 크기의 절반 만큼을 뺀다(글자가 표시되는 기준이 글자의 왼쪽 하단 모서리)
                text_position = ((width // 2) - (text_size[0] // 2), int(height / 2 + 50))
                # cv2.putText(frame, text, text_position, font, font_scale, text_color, font_thickness, cv2.LINE_AA)
                # top 
                frame = putTextKor(frame, text, pos=(text_position[0] - 50, text_position[1] + 20), font_color=text_color, font_size=text_size_)
                # frame = putTextKor(frame, text, pos=(text_left, text_top), font_color=text_color, font_size=text_size_)

                # bottom
                # frame = putTextKor(frame, text, pos=(text_left, text_top + 750), font_color=text_color, font_size=text_size_)


                # 화면 중앙 사각형
                # 중심 좌표와 크기
                center = (frame.shape[1] // 2, frame.shape[0] // 2)  # 이미지 중심 좌표

                # pt1과 pt2 계산
                r_width = width * 2 // 3
                r_height = height * 2 // 3

                pt1 = (center[0] - r_width // 2, center[1] - r_height // 2)
                pt2 = (center[0] + r_width // 2, center[1] + r_height // 2)
                # print(f'pt1: {pt1} / pt2: {pt2}')

                rect_color = (0, 255, 0)  # BGR format (green)
                rect_thickness = 6 * VIEW_SCALE
                cv2.rectangle(frame, pt1, pt2, rect_color, rect_thickness)

                # 화면 왼쪽에서 오른쪽으로 '.' 문자 채우기
                MAX_DOT_NUM = 36
                dots = min(int(frame_count * MAX_DOT_NUM / 75), MAX_DOT_NUM)
                progress_text = '.' * dots 
                font_thickness = 3 * VIEW_SCALE
                font_scale = 3 
                cv2.putText(frame, progress_text, (-5, text_position[1]), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
                # cv2.putText(frame, progress_text, (-5, 130), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
                # cv2.putText(frame, progress_text, (-5, 820), font, font_scale, text_color, font_thickness, cv2.LINE_AA)



            elif frame_count >= REC_FRAME - 1:
                # 녹화 완료시 안내 메시지
                text = "녹화가 완료 되었습니다. 잠시 기다려 주세요..."
                # text_color = (0, 255, 0)  # BGR format
                text_color = (240, 31, 229)  # Pink
                # text_color = (255, 255, 255)  # White

                frame = putTextKor(frame, text, pos=(text_left, text_top), font_color=text_color, font_size=text_size_)
                frame = putTextKor(frame, text, pos=(text_left, text_top + 750), font_color=text_color, font_size=text_size_)
                # frame = putTextKor(frame, text, pos=(80, 100), font_color=text_color, font_size=30)



        # 영상 재생
        if is_wait_mode == False:
            # print('show frame!')
            # cv2.imshow('Camera Feed', cv2.resize(frame, (width * 2, height * 2))) # 화면이 보이는 비율, 녹화와 관계 없음

            
            # 바탕 이미지 
            # 카메라 영상 크기와 일치하도록 바탕 이미지 크기 조절
            # background_image_resized = cv2.resize(background_image, (width, height))

            # 바탕 이미지에 카메라 영상을 삽입할 위치 지정
            # on_width = width // 2
            # on_height = height // 2
            # start_x = (width - on_width) // 2
            # start_y = (height - on_height) // 2 
            # end_x = start_x + on_width
            # end_y = start_y + on_height

            # 영상 크기 조절 - 아래 코드에서 삽입되는 크기와 일치해야 함
            # frame_on_image = cv2.resize(frame, (on_width, on_height))

            # 바탕 이미지에 카메라 영상을 삽입
            # background_image_resized[start_y:end_y, start_x:end_x] = frame_on_image
            # frame_with_image = background_image_resized
            # frame_with_image_and_subtitle = None
            frame_with_image = cv2.resize(frame, (width * VIEW_SCALE, height * VIEW_SCALE)) 
            cv2.imshow('Camera Feed', frame_with_image) # 화면이 보이는 비율, 녹화와 관계 없음

            # cv2.setWindowProperty('Camera Feed', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


            # 일정 시간 동안만 error 표시
            if sub_start_time != None and is_rec_mode == False:
                if error_face == True or error_mouth == True:
                    err_elapsed_time = time.time() - err_start_time
                    # print(f'start_time: {start_time}')
                    # print(f'elapsed_time: {elapsed_time}')
                    if err_elapsed_time < ERR_WARN_DUR:
                        # print(f'error_warn..')
                        err_text = '입술 인식 에러! 다시 한 번 인식을 시도해 주세요.'
                        # frame_with_image = putTextKor(frame_with_image, err_text, pos=(30, 100), font_size=30)
                        text_color = (0, 0, 255)  # BGR format, Yellow
                        frame_with_image = putTextKor(frame_with_image, err_text, pos=(text_left, text_top), font_color=text_color, font_size=text_size_)
                        frame_with_image = putTextKor(frame_with_image, err_text, pos=(text_left, text_top + 750), font_color=text_color, font_size=text_size_)
                        cv2.imshow('Camera Feed', frame_with_image)
                    else:
                        error_mouth = False
                        error_face = False
                        is_rec_mode = False
                        is_count_mode = True
                        is_prediction_done = False
                        is_rec_mode = False
                        is_count_mode = True
                        start_time = cv2.getTickCount()


            # 일정 시간 동안만 자막 표시
            if sub_start_time != None and is_prediction_done == True and is_rec_mode == False:
                sub_elapsed_time = time.time() - sub_start_time
                # print(f'start_time: {start_time}')
                # print(f'elapsed_time: {elapsed_time}')
                print(f'predict_rslt: {predict_rslt}')
                if sub_elapsed_time < SUBTITLE_DUR:
                    # print(f"subtitle: {elapsed_time}")
                    frame_with_image = putTextKor(frame_with_image, predict_rslt, pos=None)
                    cv2.imshow('Camera Feed', frame_with_image)

                else:
                    is_prediction_done = False
                    is_rec_mode = False
                    is_count_mode = True
                    start_time = cv2.getTickCount()

            
            
            # NDI send
            img = cv2.cvtColor(frame_with_image, cv2.COLOR_BGR2BGRA)

            video_frame.data = img
            video_frame.FourCC = ndi.FOURCC_VIDEO_TYPE_BGRX

            ndi.send_send_video_v2(ndi_send, video_frame)
                



        # 'm' 키를 누르면 대기모드로 전환
        if key == ord('m'):
            is_wait_mode = True 

        # 대기모드일 때 동영상 재생
        if is_wait_mode == True:
            await play_wait_video_in_existing_window(WAIT_MOVIE, 'Camera Feed')

        # 'esc' 키를 누르면 프로그램 종료합니다.
        if key == 27:
            send_osc_message(OSC_ADDR_2, OSC_PORT, "/make_vib_long", 0)
            send_osc_message(OSC_ADDR_2, OSC_PORT, "/make_vib", 0)
            send_osc_message(OSC_ADDR_2, OSC_PORT, "/guide_stop", 1)
            break

        await asyncio.sleep(ASYNC_AWAIT)


    # 사용이 끝났을 때, 카메라를 해제하고 창을 닫습니다.
    pygame.mixer.quit()
    pygame.quit()
    ndi.send_destroy(ndi_send)
    ndi.destroy()
    cap.release()
    cv2.destroyAllWindows()


async def init_main():
    # OSC Server
    server = AsyncIOOSCUDPServer(("0.0.0.0", RECVIVING_PORT), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    await loop()  # Enter main loop of program

    transport.close()  # Clean up serve endpoint

asyncio.run(init_main())



# 단축키
'''
영상모드 -> 대기모드 : m
대기모드 -> 영상모드 : ESC
안내모드 -> 대기/영상 모드 : ESC

녹화 시작 : c

종료 : ESC 
'''