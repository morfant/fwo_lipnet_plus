import os, cv2, sys

def change_fps_(input_video_path, target_fps):
    # 영상을 읽기 위해 VideoCapture 객체 생성
    cap = cv2.VideoCapture(input_video_path)

    # 원본 영상의 프레임 레이트 가져오기
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f'original_fps: {original_fps}')

    # 파일 경로를 구분
    folder_path, file_name_with_extension = os.path.split(input_video_path)
    file_name, file_extension = os.path.splitext(os.path.basename(file_name_with_extension))
    output_video_path = os.path.join(folder_path, f'{file_name}_{target_fps}_temp.mp4')

    # 출력 비디오의 VideoWriter 객체 생성
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')  # 사용할 코덱 지정
    out = cv2.VideoWriter(output_video_path, fourcc, target_fps, (int(cap.get(3)), int(cap.get(4))))

    # 프레임 레이트 변경을 위한 비율 계산
    frame_rate_ratio = target_fps / original_fps

    while True:
        # 영상에서 프레임 읽기
        ret, frame = cap.read()

        # 더 이상 프레임이 없으면 종료
        if not ret:
            break

        # 현재 프레임을 여러 번 반복해서 사용하여 새로운 프레임 생성
        for _ in range(max(1, int(frame_rate_ratio))):
            out.write(frame)

    # 사용한 자원 해제
    cap.release()
    out.release()

    print(f"FPS changed. Video saved to {output_video_path}")
    return output_video_path


def adjust_video_length(input_video_path, target_frame_count=75, target_width=360):


    # 입력 비디오 열기
    cap = cv2.VideoCapture(change_fps_(input_video_path, 25))

    # 원본 비디오의 프레임 수 및 해상도 가져오기
    original_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    original_aspect_ratio = original_width / original_height
    original_fps = cap.get(cv2.CAP_PROP_FPS)

    print(f'original_fps: {original_fps}')

    # 새로운 높이 계산
    target_height = int(target_width / original_aspect_ratio)

    # 파일 경로를 구분
    folder_path, file_name_with_extension = os.path.split(input_video_path)
    file_name, file_extension = os.path.splitext(os.path.basename(file_name_with_extension))
    output_video_path = os.path.join(folder_path, f'{file_name}_{target_frame_count}.mp4')

    # 출력 비디오 설정
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')  # MP4 코덱 사용
    out = cv2.VideoWriter(output_video_path, fourcc, 25, (target_width, target_height))

    # 비디오 길이를 조정
    for _ in range(target_frame_count):
        ret, frame = cap.read()

        if not ret:
            if original_frame_count < target_frame_count:
                # 비디오의 끝에 도달하면 original 비디오의 마지막 프레임으로 이동
                cap.set(cv2.CAP_PROP_POS_FRAMES, original_frame_count - 1)
            ret, frame = cap.read()

        # 새로운 해상도로 프레임 크기 조정
        frame_resized = cv2.resize(frame, (target_width, target_height))
        out.write(frame_resized)

    # 비디오 캡쳐 및 라이터 객체 해제
    cap.release()
    out.release()

    print(f"Video length adjusted and saved to: {output_video_path}")
    return output_video_path



# def change_frame_rate_and_resolution(input_video_path, target_fps=25, target_frame_count=75, target_width=640):
#     """
#     영상의 프레임 속도를 변경하고 해상도를 특정 너비를 기준으로 조정하여 다시 저장하는 함수

#     Parameters:
#     - input_video_path (str): 입력 비디오 파일 경로
#     - target_fps (int): 변경하고자 하는 프레임 속도
#     - target_frame_count (int): 변경하고자 하는 총 프레임 수
#     - target_width (int): 변경하고자 하는 해상도의 너비
#     """
#     # 입력 비디오 열기
#     cap = cv2.VideoCapture(input_video_path)

#     # 원본 비디오의 프레임 속도 및 프레임 수 가져오기
#     original_fps = int(cap.get(cv2.CAP_PROP_FPS))
#     original_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#     original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#     original_aspect_ratio = original_width / original_height

#     # 만약 입력된 비디오가 이미 목표 값과 동일하다면 처리하지 않음
#     if original_fps == target_fps and original_frame_count == target_frame_count:
#         print(f"Video already has the target frame rate and frame count. No processing needed.")
#         return

#     # 새로운 높이 계산
#     target_height = int(target_width / original_aspect_ratio)

#     # 파일 경로를 구분
#     folder_path, file_name_with_extension = os.path.split(input_video_path)
#     file_name, file_extension = os.path.splitext(os.path.basename(file_name_with_extension))
#     output_video_path = os.path.join(folder_path, f'{file_name}_{target_fps}_{target_frame_count}_{target_width}w.mp4')
    
#     # 출력 비디오 설정
#     fourcc = cv2.VideoWriter_fourcc(*'MP4V')  # MP4 코덱 사용
#     out = cv2.VideoWriter(output_video_path, fourcc, target_fps, (target_width, target_height))

#     count = 0 

#     # 비디오 프레임 속도 및 해상도 변경
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         print(f'count: {count}')
#         count += 1
#         cf = target_frame_count / original_frame_count
#         c = target_frame_count // original_frame_count
#         print(f'cf: {cf} / c: {c}')

#         # 프레임 속도 변경을 위해 원본 프레임을 반복해서 추가
#         for _ in range(c + 1):
#             # 새로운 해상도로 프레임 크기 조정
#             print(f'inner for loop')
#             frame_resized = cv2.resize(frame, (target_width, target_height))
#             out.write(frame_resized)

#     # 비디오 캡쳐 및 라이터 객체 해제
#     cap.release()
#     out.release()
#     print(f"Video frame rate and resolution changed and saved to: {output_video_path}")
#     return output_video_path


def change_fps(input_video_path, target_fps):
    # 영상을 읽기 위해 VideoCapture 객체 생성
    cap = cv2.VideoCapture(input_video_path)

    # 파일 경로를 구분
    folder_path, file_name_with_extension = os.path.split(input_video_path)
    file_name, file_extension = os.path.splitext(os.path.basename(file_name_with_extension))
    output_video_path = os.path.join(folder_path, f'{file_name}_{target_fps}_temp.mp4')

    # 출력 비디오의 VideoWriter 객체 생성
    fourcc = cv2.VideoWriter_fourcc(*'MP4V')  # 사용할 코덱 지정
    out = cv2.VideoWriter(output_video_path, fourcc, target_fps, (int(cap.get(3)), int(cap.get(4))))

    while True:
        # 영상에서 프레임 읽기
        ret, frame = cap.read()

        # 더 이상 프레임이 없으면 종료
        if not ret:
            break

        # 프레임 레이트 변경
        out.write(frame)

    # 사용한 자원 해제
    cap.release()
    out.release()

    print(f"FPS changed. Video saved to {output_video_path}")
    return output_video_path


path = sys.argv[1]
adjust_video_length(path)

# change_fps(path, 25)
# change_frame_rate_and_resolution(path, target_fps=25, target_frame_count=75, target_width=640)