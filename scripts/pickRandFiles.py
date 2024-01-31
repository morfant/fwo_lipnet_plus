import os
import random
import shutil

def move_random_files_in_subfolders(root_folder, destination_folder, num_files=100):
    # root_folder 내의 모든 하위 폴더를 찾기
    for foldername, subfolders, filenames in os.walk(root_folder):
        # 현재 폴더의 파일 목록 가져오기
        file_list = [os.path.join(foldername, filename) for filename in filenames]

        # 랜덤하게 파일 선택 (중복 없이)
        selected_files = random.sample(file_list, min(num_files, len(file_list)))

        # 목적지 폴더가 없다면 생성
        relative_folder_path = os.path.relpath(foldername, root_folder)
        destination_folder_path = os.path.join(destination_folder, relative_folder_path)

        if not os.path.exists(destination_folder_path):
            os.makedirs(destination_folder_path)

        # 파일을 목적지 폴더로 이동
        for file_path in selected_files:
            file_name = os.path.basename(file_path)
            destination_path = os.path.join(destination_folder_path, file_name)

            shutil.move(file_path, destination_path)
            print(f"Moved: {file_name} to {destination_path}")

# 사용 예시
root_folder = "../data/150_lip_videos/"
destination_folder = root_folder + '100/'
move_random_files_in_subfolders(root_folder, destination_folder, num_files=100)
