import cv2
import imageio 
import time
from lipnet.lipreading.videos import Video
import os, fnmatch, sys, errno  
from skimage import io
import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt



frame_count = 0
REC_SEC = 3
REC_FILE = './camout/output.mp4'
FACE_PREDICTOR_PATH = './predictors/shape_predictor_68_face_landmarks.dat'

def count_frames(video_path):
    # VideoCapture 객체 생성
    cap = cv2.VideoCapture(video_path)

    # 프레임 수 확인
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # VideoCapture 객체 해제
    cap.release()

    return frame_count

def display_text(frame_on, text="text..", px=10, py=20, r=255, g=0, b=0):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8 
    font_thickness = 2
    text_position = (px, py)
    text_color = (b, g, r)  # BGR format
    cv2.putText(frame_on, text, text_position, font, font_scale, text_color, font_thickness)


def load_frames_from_video(filepath:str):
    print(f'load_frames_from_video() path: {filepath}')

    fc = count_frames(filepath)
    print(f'load_frames_from_video frame count of input video: {fc}')

    # print ("Processing: {}".format(filepath))
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
# 카메라를 연결합니다.
cap = cv2.VideoCapture(0)

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

while True:
    # 프레임을 읽어옵니다.
    ret, frame = cap.read()

    # 읽어온 프레임이 없으면 종료합니다.
    if not ret:
        break

    # 읽어온 프레임을 360 x 288로 리사이징합니다.
    frame = cv2.resize(frame, (width, height))

    # 'r' 키를 누르면 녹화 시작 또는 종료
    key = cv2.waitKey(1) & 0xFF
    if key == ord('r'):
        if not recording:
            # 이전에 녹화된 파일 삭제
            # try:
            #     os.remove(REC_FILE)
            #     print(f'{REC_FILE} 파일이 삭제되었습니다.')
            # except OSError as e:
            #     print(f'파일 삭제 오류: {e.filename} - {e.strerror}')

            # 3초 카운트 다운 표시
            for countdown in range(3, 0, -1):
                text = f'{countdown}'
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1
                font_thickness = 2
                text_position = (int(width / 2), int(height / 2 - 50))
                text_color = (0, 0, 255)  # BGR format
                frame_with_countdown = frame.copy()
                cv2.putText(frame_with_countdown, text, text_position, font, font_scale, text_color, font_thickness)
                cv2.imshow('Camera Feed', cv2.resize(frame_with_countdown, (2 * width, 2 * height)))
                cv2.waitKey(1000)  # 1초 대기
            print("녹화 시작")
            recording = True
            out = cv2.VideoWriter(REC_FILE, fourcc, fps, (width, height))
            start_time = cv2.getTickCount()
        else:
            print("녹화 종료")
            recording = False

    # 녹화 중일 때
    if recording:
        # 75frame이 채워지면 녹화 종료
        if frame_count >= 75:

            print(f'{frame_count} frame 녹화 완료')
            out.release()
            out = None
            frame_count = 0
            recording = False

            if os.path.exists(REC_FILE):
                calc_frames = []
                print(f'load_frames_from_video: {REC_FILE}')
                calc_frames, error_face, error_mouth = load_frames_from_video(REC_FILE)
                # print(f'error_f: {error_face} / error_m: {error_mouth}')

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

                    # imageio.mimsave('./camout/animation.gif', (frames * 255).numpy().astype('uint8').squeeze(), fps=fps)

            

        # 영상 저장
        if out != None:
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
    cv2.imshow('Camera Feed', cv2.resize(frame, (width * 2, height * 2))) # 화면이 보이는 비율, 녹화와 관계 없음

    # 'esc' 키를 누르면 종료합니다.
    if key == 27:
    # if key == ord('q'):
        break

# 사용이 끝났을 때, 카메라를 해제하고 창을 닫습니다.
cap.release()
cv2.destroyAllWindows()
