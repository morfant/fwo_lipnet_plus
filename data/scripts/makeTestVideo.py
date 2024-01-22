import cv2

def cut_and_save_video(input_path, output_path, frame_length, target_fps):
    cap = cv2.VideoCapture(input_path)
    
    # 동영상 속성 가져오기
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    original_fps = cap.get(5)  # 원본 동영상 프레임 속도

    # 동영상 저장을 위한 VideoWriter 설정
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 또는 다른 적절한 코덱
    out = cv2.VideoWriter(output_path, fourcc, target_fps, (frame_width, frame_height))

    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(total_frames)

    while True:
        ret, frame = cap.read()
        
        if not ret:
            break

        # 프레임 저장
        out.write(frame)

        frame_count += 1

        # 특정 프레임 길이 단위로 자르기
        if frame_count % frame_length == 0:
            break

            # 저장된 프레임 수가 동영상 전체 프레임 수를 넘어가면 종료
            # if frame_count >= total_frames:
                # break

            # 새로운 비디오 파일 생성
            # out.release()
            # new_output_path = output_path.replace('.mp4', f'_{frame_count//frame_length}.mp4')
            # out = cv2.VideoWriter(new_output_path, fourcc, target_fps, (frame_width, frame_height))

    # 리소스 해제
    cap.release()
    out.release()

# 사용 예시
input_video_path = './test/a_4.mov'
output_video_path = './test/a_4_75.mp4'
cut_frame_length = 75  # 원하는 프레임 길이
target_fps = 25  # 목표 프레임 속도

cut_and_save_video(input_video_path, output_video_path, cut_frame_length, target_fps)
