import cv2
import os
from pathlib import Path


FPS = 25
def makeFramesToVideo(folder_path):

    # 각 subfolder에 대한 반복
    for subfolder in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder)

        # subfolder가 폴더가 아닌 경우 건너뛰기
        if not os.path.isdir(subfolder_path):
            continue

        # subfolder 내의 모든 .png 파일 가져오기 및 정렬
        image_files = sorted([f for f in os.listdir(subfolder_path) if f.endswith(".png")])

        if len(image_files) == 0:
            continue  # .png 파일이 없는 경우 건너뛰기

        # 첫 번째 이미지를 기준으로 영상 크기 가져오기
        first_image = cv2.imread(os.path.join(subfolder_path, image_files[0]))
        height, width, _ = first_image.shape

        # 비디오 파일 생성
        # video_path = os.path.join(folder_path, f"{subfolder}.mpg")
        # video_writer = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MPG4'), 1, (width, height))

        # 비디오 파일 생성
        parent_video_path = os.path.abspath(os.path.join(folder_path, '..'))
        video_path = os.path.join(parent_video_path, f"{subfolder}.mp4")
        video_writer = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MP4V'), FPS, (width, height))

        # 각 이미지를 비디오에 추가
        for image_file in image_files:
            image_path = os.path.join(subfolder_path, image_file)
            frame = cv2.imread(image_path)
            video_writer.write(frame)

        # 비디오 파일 닫기
        video_writer.release()

    print(f'{video_path} 파일 생성이 완료되었습니다.')




# folder_path = "../data/100_each_frames/s13/cropped/"
root_folder = "../data/100_each_frames/"
# makeFramesToVideo(folder_path)

dirs = os.listdir(root_folder)
for subdir in dirs:
    if os.path.isdir(os.path.join(root_folder, subdir)):
        if subdir.startswith('s'):
            folder_path = os.path.join(root_folder, subdir, 'cropped')
            # print(folder_path)
            makeFramesToVideo(folder_path)

# for subdir in Path(root_folder).rglob("*"):
#     if subdir.is_dir():
#         print(subdir)
    
