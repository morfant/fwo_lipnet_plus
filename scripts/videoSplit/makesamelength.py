import os
import cv2

def get_files_in_folder(folder_path):
    # 폴더 내 모든 파일의 리스트를 가져옴
    files = os.listdir(folder_path)

    # 파일만 추려내어 리스트에 저장
    file_list = [file for file in files if os.path.isfile(os.path.join(folder_path, file))]

    return file_list

def get_frame_count(video_path):
    # 비디오 파일 열기
    cap = cv2.VideoCapture(video_path)

    # 비디오 파일이 정상적으로 열리는지 확인
    if not cap.isOpened():
        print(f"Error: Couldn't open the video file {video_path}.")
        return None

    # 프레임 수 확인
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # 비디오 파일 닫기
    cap.release()

    return frame_count

def find_shorter_videos(folder_path, threshold_frame_length):
    short_videos = []

    # 지정된 폴더에서 모든 비디오 파일 가져오기
    video_files = [f for f in os.listdir(folder_path) if f.endswith(('.mp4'))]

    # 비디오 파일들에 대한 프레임 수 확인 및 출력
    for video_file in video_files:
        video_path = os.path.join(folder_path, video_file)
        frame_count = get_frame_count(video_path)

        if frame_count is not None:
            print(f"Video: {video_file}, Frame Count: {frame_count}")

            if frame_count < threshold_frame_length:
                short_videos.append((video_file, frame_count, threshold_frame_length - frame_count))

    return short_videos 


def append_frame(video_path, src_frame, nframe, output_path):

    # 비디오 파일 열기
    cap = cv2.VideoCapture(video_path)

    # 비디오 파일이 정상적으로 열리는지 확인
    if not cap.isOpened():
        print("Error: Couldn't open the video file.")
        return

    # 비디오 정보 가져오기
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    frames_per_second = cap.get(5)
    print("=========================")
    print(str(frame_width) + " x " + str(frame_height) + "(fps " + str(int(frames_per_second)) +")")

    # VideoWriter 객체 생성
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, frames_per_second, (frame_width, frame_height))

    # 앞쪽에 프레임 덧붙이기
    nf = int(nframe / 2)
    for _ in range(nf):
        out.write(src_frame)

    # 비디오 끝까지 읽기
    while True:
        ret, frame = cap.read()

        # 비디오가 끝나면 종료
        if not ret:
            break

        # 프레임을 VideoWriter를 사용하여 쓰기
        out.write(frame)

    # 뒤쪽에 프레임 덧붙이기
    for _ in range(nframe - nf):
        out.write(src_frame)

    # 비디오 파일과 VideoWriter 객체 닫기
    cap.release()
    out.release()

    print(f"Frames appended and new video saved to {output_path}.")


def read_specific_frame(video_path, frame_number):
    # 비디오 파일 열기
    cap = cv2.VideoCapture(video_path)

    # 비디오 파일이 정상적으로 열리는지 확인
    if not cap.isOpened():
        print("Error: Couldn't open the video file.")
        return None

    # 프레임 번호로 이동
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)

    # 프레임 읽기
    ret, frame = cap.read()

    # 프레임이 정상적으로 읽혔는지 확인
    if not ret:
        print(f"Error: Couldn't read frame {frame_number}.")
        return None

    # 비디오 파일 닫기
    cap.release()

    return frame


if __name__ == "__main__":

    TARGET_PATH = './data/splited_videos/'
    file_name = "lip_J_1_F_02_C032_A_010"

    # 프레임 길이 임계값 설정 (frames)
    threshold_frame_length = 100 

    # 특정 프레임 길이보다 짧은 비디오 찾기
    short_videos = find_shorter_videos(TARGET_PATH, threshold_frame_length)

    if short_videos:
        print(f"프레임 길이가 {threshold_frame_length}보다 짧은 비디오:")
        for video, frame_length, diff in short_videos:
            print(f"{video}: {frame_length} 프레임({diff})")
    else:
        print(f"프레임 길이가 {threshold_frame_length}보다 짧은 비디오가 없습니다.")

    # 비디오파일 경로 및 가져올 프레임 번호 지정
    long_video_path = "./data/video/" + file_name + ".mp4"
    frame_number_to_read = 1  # 가져올 프레임 번호

    # 프레임 읽기 함수 호출 : silence 프레임을 구한다
    silent_frame = read_specific_frame(long_video_path, frame_number_to_read)

    # 가져온 프레임 확인 
    # if silent_frame is not None:
    #     # 여기에서 frame 변수를 사용하여 필요한 작업을 수행합니다.
    #     cv2.imshow("Frame", silent_frame)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()

    # 프레임 추가 함수 호출
    for video, frame_length, diff in short_videos:
        id = video.split('_')[1].split('.')[0]
        append_frame(TARGET_PATH + video, silent_frame, diff, f"./data/adjusted_videos/sample_{id}.mp4")

