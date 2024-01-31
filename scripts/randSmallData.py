# 전체 데이터 셋에서 최대한 중복 없이 정해진 개수 만큼의 데이터를 선별
import os
import random
import shutil


def parse_align_file(align_path):
    with open(align_path, 'r') as align_file:
        lines = align_file.readlines()

    align_data = [line.strip().split()[2] for line in lines if 'sil' not in line]
    return set(align_data)

def select_non_overlapping_videos(video_folder, align_folder, num_videos):
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.mpg')]
    # random.shuffle(video_files)
    align_files = [f for f in os.listdir(align_folder) if f.endswith('.align')]

    selected_videos = []
    selected_words = set()
    max_overlap = 1

    while len(selected_videos) < num_videos:
        for align_file in align_files:
            align_path = os.path.join(align_folder, align_file)
            align_words = parse_align_file(align_path)

            overlap_count = len(align_words.intersection(selected_words))
            if overlap_count <= max_overlap:
                video_name = align_file.replace('.align', '')
                # video_path = os.path.join(video_folder, f"{video_name}.mpg")
                video_path = f"{video_name}.mpg"

                # 중복된 파일 이름이 아니라면 추가
                if video_path not in selected_videos:
                    selected_videos.append(video_path)
                    selected_words.update(align_words)

                    if len(selected_videos) == num_videos:
                        break

        max_overlap += 1

    return selected_videos


# 비디오 폴더안의 파일 이름과 동일한 align 파일들을 alignments/sn 폴더에 복사한다.
def create_aligned_folder(video_folder_path, align_folder_path, new_folder_path):
    # 만약 목적 폴더가 없으면 생성
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)

    # .mpg 파일 가져오기
    mpg_files = [file for file in os.listdir(video_folder_path) if file.endswith('.mpg')]

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


# 리스트에 있는 파일들을 destinatino_folder로 복사
def copy_files_to_folder(file_names, source_folder, destination_folder):

    os.makedirs(destination_folder, exist_ok=True)  # 대상 폴더가 없으면 생성

    for file_name in file_names:
        source_path = os.path.join(source_folder, file_name)
        destination_path = os.path.join(destination_folder, file_name)

        # print(f'source_path: {source_path}')
        # print(f'dest_path: {destination_path}')

        try:
            shutil.copy2(source_path, destination_path)
            print(f"File '{file_name}' copied successfully.")
        except FileNotFoundError:
            print(f"File '{file_name}' not found in the source folder.")
        except shutil.SameFileError:
            print(f"File '{file_name}' already exists in the destination folder.")


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
num_data = 100
folders_to_process = [
    # 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's9', 's10',
    # 's11', 's12', 's13', 's14', 's15', 's16', 's17', 's19', 's20',
    # 's22', 's23', 's24', 's25', 's26', 's27', 's29', 's30', 
    # 's31', 's32', 's33', 's34'
    's18', 's28'
    ] 
for folder_name in folders_to_process:
    video_folder = '../data/' + folder_name
    align_folder = '../data/alignments/'
    new_folder_path = '../data/100_each/'

    selected_videos = select_non_overlapping_videos(video_folder, align_folder + folder_name, num_data)

    print("-" * 50)
    print(f'{len(selected_videos)} videos selected from {video_folder}.')

    print("copy selected video files.")
    copy_files_to_folder(selected_videos, video_folder, new_folder_path + folder_name)
    print(f'done.')

    print("making matching alignments folder ")
    create_aligned_folder(new_folder_path + folder_name, align_folder + folder_name, new_folder_path + 'alignments/' + folder_name)
    print(f'done.')