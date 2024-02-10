import cv2
import imageio 
import time
from lipnet.lipreading.videos import Video
import os, fnmatch, sys, errno  
from skimage import io
import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from datetime import datetime
from PIL import ImageFont, ImageDraw, Image
from lip_read import LipRead

from pythonosc import udp_client, osc_server
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio


is_wait_mode = 0 # 1: True / 0: False 
is_rec_mode = 0


# OSC receive handler
def mode_handler(address, *args):
    global is_wait_mode
    is_wait_mode = args[0]
    print(f"{address}: {args}")

# OSC Server(Async) setup
dispatcher = Dispatcher()
dispatcher.map("/is_wait_mode", mode_handler) # Address pattern, handler function
ip = "127.0.0.1" # receiving ip
port = 1337 # receiving port



async def countdown(width, height, frame):
    
    for countdown in range(3, 0, -1):
        text = f'{countdown}'
        print(f'countdown(): {text}')
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        font_thickness = 2
        text_position = (int(width / 2), int(height / 2 - 50))
        text_color = (0, 0, 255)  # BGR format
        frame_with_countdown = frame.copy()
        cv2.putText(frame_with_countdown, text, text_position, font, font_scale, text_color, font_thickness)
        cv2.imshow('Camera Feed', cv2.resize(frame_with_countdown, (2 * width, 2 * height)))
        await asyncio.sleep(1)  # 1초 대기


def putTextKor(src, text, pos=(10, 200), font_size=20, font_color=(255, 255, 255)) :

    FONT_PATH = './IBM_Plex_Sans_KR/IBMPlexSansKR-Regular.ttf'
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 3

    print(f'text: {text}')
    # text = "안녕하세요"

    # 텍스트 크기 얻기
    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
    # print(f'text_size: {text_size}')

    # 이미지 중앙에 텍스트를 출력할 위치 계산
    # print(f'0: {src.shape[0]}') # height
    # print(f'1: {src.shape[1]}') # width
    text_x = (src.shape[1] - text_size[0]//3) // 2 # 왠지 모르겠지만 text_size를 3으로 나누어야 화면의 가운데가 된다
    text_y = src.shape[0] - 40 # 40 from bottom 

    img_pil = Image.fromarray(src)
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype(FONT_PATH, font_size)
    draw.text((text_x, text_y), text, font=font, fill=(263, 20, 216))
    return np.array(img_pil)


# 대기모드시 영상파일 재생을 위한 함수
async def play_video_in_existing_window(file_path, window_name, loop=True):
    global is_wait_mode, is_rec_mode, recording
    is_key_pressed = False
    cap_mov = cv2.VideoCapture(file_path)

    if not cap_mov.isOpened():
        print("Error: Couldn't open video file.")
        return

    while True:
        ret, frame = cap_mov.read()

        if not ret:
            if loop:
                cap_mov.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            else:
                break

        cv2.imshow(window_name, frame)

        # print(f'is_wait_mode in function: {is_wait_mode}')
        if is_wait_mode == 0 and is_key_pressed == False:
            is_rec_mode = 0
            recording = False
            break

        # 'm' 키를 누르면 종료합니다.
        key = cv2.waitKey(25)
        if key == ord('m'):
            is_key_pressed = True
            is_wait_mode = 0
            is_rec_mode = 0
            recording = False
            break

        await asyncio.sleep(0.01)

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


# 영상 촬영 중 일정 간격 이미지 저장할 폴더 생성
# captured_frames_YYMMDD_HHMMSS 의 형태
def create_output_directory():

    # 현재 날짜와 시간을 이용하여 디렉토리 이름 생성
    timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
    output_directory = os.path.join('archive', f'captured_frames_{timestamp}')

    # 디렉토리 생성
    os.makedirs(output_directory, exist_ok=True)

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

# def display_text(frame_on, text="text..", px=10, py=20, r=255, g=0, b=0):
#     font = cv2.FONT_HERSHEY_SIMPLEX
#     font_scale = 0.8 
#     font_thickness = 2
#     text_position = (px, py)
#     text_color = (b, g, r)  # BGR format
#     cv2.putText(frame_on, text, text_position, font, font_scale, text_color, font_thickness)


def load_frames_from_video(filepath:str):
    print(f'load_frames_from_video() path: {filepath}')

    fc = count_frames(filepath)
    print(f'load_frames_from_video frame count of input video: {fc}')

    # print ("Processing: {}".format(filepath))

    FACE_PREDICTOR_PATH = './predictors/shape_predictor_68_face_landmarks.dat'
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




# ---------------------- MAIN -----------------------
async def loop():

    elapsed_frame = 0

    SUBTITLE_DUR = 5  # 자막이 표시될 시간 (초)
    predict_rslt = ""
    start_time = None
    REC_FRAME = 75

    OSC_ADDR = "127.0.0.1"
    OSC_PORT = 30000

    # 대기 화면에서 재생될 영상
    WAIT_MOVIE = './waiting.mov'

    frame_count = 0
    save_interval = 5
    REC_SEC = 3
    REC_FILE = './camout/output.mp4'


    lipRead = LipRead()


    # lip read
    lipRead.init()

    # 카메라를 연결합니다.
    cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

    # 새로운 해상도 설정
    width = 360
    height = 288
    fps = 25
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # 창을 생성합니다.
    cv2.namedWindow('Camera Feed', cv2.WINDOW_NORMAL)

    # 항상 화면 맨 위에 표시되도록 설정합니다.
    cv2.setWindowProperty('Camera Feed', cv2.WND_PROP_TOPMOST, 1)

    # 비디오 라이터 생성
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')

    # 녹화 상태를 나타내는 변수
    recording = False
    is_prediction_done = False



    global is_wait_mode, is_rec_mode
    while True:
        
        # print(f'is_wait_mode: {is_wait_mode}')

        # 프레임을 읽어옵니다.
        ret, frame = cap.read()

        # 읽어온 프레임이 없으면 종료합니다.
        if not ret:
            break

        # 읽어온 프레임을 360 x 288로 리사이징합니다.
        frame = cv2.resize(frame, (width, height))

        # 좌우 반전 적용
        frame = cv2.flip(frame, 1)

        # 'r' 키를 누르면 녹화 시작 또는 종료
        key = cv2.waitKey(1) & 0xFF
        # if key == ord('r') or is_wait_mode == 0:
        if key == ord('r'):
            print(f'check is_rec_mode: {is_rec_mode}')
            if not recording and is_rec_mode == 0:
                is_rec_mode = 1

                # 이전에 녹화된 파일 삭제
                # try:
                #     os.remove(REC_FILE)
                #     print(f'{REC_FILE} 파일이 삭제되었습니다.')
                # except OSError as e:
                #     print(f'파일 삭제 오류: {e.filename} - {e.strerror}')


                # async
                # await countdown(width, height, frame)

                # sync
                # frame_count 초기화
                frame_count = 0

                # 3초 카운트 다운 표시
                cv2.waitKey(1000)  # 1초 대기, PRE_COUNTDOWN
                for countdown in range(3, 0, -1):
                    text = f'{countdown}'
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 1
                    font_thickness = 2
                    text_position = (int(width / 2), int(height / 2 - 50))
                    text_color = (0, 0, 255)  # BGR format
                    frame_with_countdown = frame.copy()
                    cv2.putText(frame_with_countdown, text, text_position, font, font_scale, text_color, font_thickness)
                    print(f'countdown text : {countdown}')
                    cv2.imshow('Camera Feed', cv2.resize(frame_with_countdown, (2 * width, 2 * height)))
                    cv2.waitKey(1000)  # 1초 대기
                    # await asyncio.sleep(1) # 비동기로 처리하면  camera feed 에 글자가 표시되지 않는다

                await asyncio.sleep(0.1) # 카운트 다운 도중 관객 이탈 감지를 위한 코드
                if is_wait_mode == 1:
                    continue

                print("녹화 시작")
                recording = True
                is_prediction_done = False
                out = cv2.VideoWriter(REC_FILE, fourcc, fps, (width, height))
                start_time = cv2.getTickCount()

                # 프레임 이미지 저장할 폴더 생성
                output_directory = create_output_directory()
                send_osc_message(OSC_ADDR, OSC_PORT, "/current_directory", output_directory)
                # print(output_directory)

            # else:
            #     print("녹화 종료") # 녹화 도중 다시 'r'을 눌렀을 때
            #     recording = False

        # 녹화 중일 때
        if recording:
            if frame_count < REC_FRAME:
                if is_wait_mode == 1:
                    print('녹화 중단!!')

                    # record가 끝나면 현재 시간을 OSC로 전송
                    timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
                    send_osc_message(OSC_ADDR, OSC_PORT, "/record_end", timestamp)

                    out.release() # 파일 저장
                    out = None
                    recording = False
                    is_prediction_done = False


            # 75frame이 채워지면 녹화 종료
            elif frame_count >= REC_FRAME: # 저장은 frame_count가 74일 때까지만 되어야 한다

                print(f'{frame_count} frame 녹화 완료')

                # record가 끝나면 현재 시간을 OSC로 전송
                timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
                send_osc_message(OSC_ADDR, OSC_PORT, "/record_end", timestamp)

                out.release() # 파일 저장
                out = None
                recording = False

                if os.path.exists(REC_FILE): # 영상 파일 저장된 것이 확인 되면
                    calc_frames = []
                    print(f'load_frames_from_video: {REC_FILE}')
                    calc_frames, error_face, error_mouth = load_frames_from_video(REC_FILE)
                    # print(f'error_f: {error_face} / error_m: {error_mouth}')
                    print(f'shape of calc_frames: {calc_frames.shape}')

                    predict_rslt = lipRead.predict(calc_frames)
                    print(predict_rslt)
                    # predict_rslt = lipRead.translate(rslt)
                    

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

                        # print(calc_frames.shape)
                        imageio.mimsave('./camout/animation.gif', (calc_frames * 255).numpy().astype('uint8').squeeze(), fps=fps)

                    is_prediction_done = True
                    start_time = time.time()

                

            # 영상 저장
            if out != None: # 영상이 저장되고 있다면

                # 일정 간격마다 이미지 저장
                if frame_count % save_interval == 0:

                    # 이미지 파일 경로 설정
                    formatted_number = f"{frame_count:03d}"
                    image_path = os.path.join(output_directory, f'mouth_{formatted_number}.png')

                    # 이미지 저장
                    cv2.imwrite(image_path, frame)
                    # print(f'Frame {frame_count} saved at {image_path}')

                out.write(frame)
                frame_count += 1
                # print(f'Recorded frame count: {frame_count}')


            # 영상에 녹화 안되는 부분
            # 텍스트 추가 (현재 녹화 중임을 알려주는 메시지)
            text = 'Recording...'
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8 
            font_thickness = 2
            text_position = (10, 25)
            text_color = (0, 0, 255)  # BGR format
            cv2.putText(frame, text, text_position, font, font_scale, text_color, font_thickness)

            # 화면 왼쪽에서 오른쪽으로 '.' 문자 채우기
            font_scale = 1 
            elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
            MAX_DOT_NUM = 36
            # dots = min(int(elapsed_time * MAX_DOT_NUM / REC_SEC), MAX_DOT_NUM)
            dots = min(int(frame_count * MAX_DOT_NUM / 75), MAX_DOT_NUM)
            progress_text = '.' * dots
            cv2.putText(frame, progress_text, (0, 40), font, font_scale, text_color, font_thickness)

            # Draw a rectangle on the screen (not included in recording)
            rect_start_point = (50, 50)
            rect_end_point = (300, 250)
            rect_color = (0, 255, 0)  # BGR format (green)
            rect_thickness = 2
            cv2.rectangle(frame, rect_start_point, rect_end_point, rect_color, rect_thickness)


        # 영상 재생
        if is_wait_mode == 0:
            cv2.imshow('Camera Feed', cv2.resize(frame, (width * 2, height * 2))) # 화면이 보이는 비율, 녹화와 관계 없음

            # 일정 시간 동안만 자막 표시
            if start_time != None and is_prediction_done == True and recording == False:
                elapsed_time = time.time() - start_time
                # print(f'start_time: {start_time}')
                # print(f'elapsed_time: {elapsed_time}')
                if elapsed_time < SUBTITLE_DUR:
                    # print(f"subtitle: {elapsed_time}")
                    img = putTextKor(frame, predict_rslt)
                    cv2.imshow('Camera Feed', img)

                else:
                    is_rec_mode = 0
                



        # 'm' 키를 누르면 대기모드로 전환
        if key == ord('m'):
            is_wait_mode = 1

        # 대기모드일 때 동영상 재생
        if is_wait_mode == 1:
            await play_video_in_existing_window(WAIT_MOVIE, 'Camera Feed')

        # 'esc' 키를 누르면 종료합니다.
        if key == 27:
            break

        await asyncio.sleep(0.01)

    # 사용이 끝났을 때, 카메라를 해제하고 창을 닫습니다.
    cap.release()
    cv2.destroyAllWindows()


async def init_main():
    # OSC Server
    server = AsyncIOOSCUDPServer((ip, port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving

    await loop()  # Enter main loop of program

    transport.close()  # Clean up serve endpoint

asyncio.run(init_main())



# 단축키
'''
영상모드 <-> 대기모드 : m

녹화 시작 : r

종료 : esc

'''