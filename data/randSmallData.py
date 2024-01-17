import os
import random
import shutil

def create_aligned_folder(original_folder_path, align_folder_path, new_folder_path):
    # 만약 목적 폴더가 없으면 생성
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

    # .mpg 파일 가져오기
    mpg_files = [file for file in os.listdir(original_folder_path) if file.endswith('.mpg')]

    for mpg_file in mpg_files:
        # .mpg 파일과 이름이 일치하는 .align 파일 경로 가져오기
        align_file_name = os.path.splitext(mpg_file)[0] + '.align'
        align_file_path = os.path.join(align_folder_path, align_file_name)

        # .align 파일이 존재하면 .mpg 파일과 .align 파일을 목적 폴더로 복사
        if os.path.exists(align_file_path):
            # mpg_file_path = os.path.join(original_folder_path, mpg_file)
            # destination_path = os.path.join(new_folder_path, mpg_file)
            # shutil.copy(mpg_file_path, destination_path)

            align_file_destination_path = os.path.join(new_folder_path, align_file_name)
            shutil.copy(align_file_path, align_file_destination_path)


def copy_random_files(original_folder_path, new_folder_path, num_files=150, file_extension='.mpg'):
    # 만약 새로운 폴더가 없으면 생성
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

    # 폴더 내 모든 .mpg 파일 가져오기
    all_files = [file for file in os.listdir(original_folder_path) if file.endswith(file_extension)]

    # 만약 파일 개수가 num_files 이하이면 모든 파일을 복사
    if len(all_files) <= num_files:
        for file in all_files:
            file_path = os.path.join(original_folder_path, file)
            shutil.copy(file_path, new_folder_path)
    else:
        # 랜덤하게 num_files 개 선택
        selected_files = random.sample(all_files, num_files)
        
        # 선택된 파일들을 새로운 폴더로 복사
        for file in selected_files:
            file_path = os.path.join(original_folder_path, file)
            shutil.copy(file_path, new_folder_path)


def rename_folders(base_folder_path, suffix='_150'):
    # 기존 폴더 목록 가져오기
    folders = [folder for folder in os.listdir(base_folder_path) if os.path.isdir(os.path.join(base_folder_path, folder))]

    for folder in folders:
        # 폴더 이름이 s로 시작하는 경우에만 변경
        if folder.startswith('s'):
            # 새로운 이름 생성 (예: s1 -> s1_150)
            new_folder_name = f"{folder}{suffix}"

            # 폴더 경로 및 새로운 폴더 경로 생성
            old_folder_path = os.path.join(base_folder_path, folder)
            new_folder_path = os.path.join(base_folder_path, new_folder_name)

            # 폴더 이름 변경
            os.rename(old_folder_path, new_folder_path)
            print(f"폴더 이름 변경: {folder} -> {new_folder_name}")



# 여러 폴더에 대해 작업을 반복
num_data = 150
folders_to_process = ['./s1', './s2', './s3', './s4', './s5', './s6', './s7', './s9', './s10', './s11']
for folder_path in folders_to_process:
    folder_name = folder_path.split('/')[1]
    new_folder_path = './150/' + folder_name
    print(f'from {folder_path}')
    print(f'copying randomly selected {num_data} files to {new_folder_path}')
    copy_random_files(folder_path, new_folder_path, num_files=num_data)
    print(f'done.')

    print("making matching alignments folder ")
    create_aligned_folder(new_folder_path, './alignments/' + folder_name, './150/alignments/' + folder_name)
    print(f'done.')

    # 함수 호출로 폴더 이름 변경
    rename_folders('./150', '_')
    rename_folders('./150/alignments', '_')


