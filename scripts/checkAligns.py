import os
import re

def get_file_line_count(file_path, expected_line_count):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    return len(lines)


def check_file_format(file_path):
    # 정규 표현식을 사용하여 주어진 형식과 일치하는지 확인
    pattern = re.compile(r'^(\d+) (\d+) (\w+)$')

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            match = pattern.match(line)
            if not match:
                return False

    return True


def detect_align_with_wrong_line_count(folder_path, expected_line_count=8):
    # Iterate through all files and subdirectories in the specified folder
    for root, dirs, files in os.walk(folder_path):
        # print(dirs)
        # Filter out only video files
        align_files = [file for file in files if file.lower().endswith(('.align'))]
        
        # Check frame count for each video file
        for align_file in align_files:
            # print(video_file)
            align_path = os.path.join(root, align_file)
            line_count = get_file_line_count(align_path, expected_line_count)
            is_format_match = check_file_format(align_path)
            
            # print(f"Align file '{align_file}' in '{root}' has {is_format_match} format!!")

            if line_count is not None and line_count != expected_line_count:
                print(f"Align file '{align_file}' in '{root}' has {line_count} lines, which is not the expected {expected_line_count} lines.")

                # Print the content of the file
                with open(align_path, 'r') as file:
                    file_content = file.read()
                    print(f"File content:\n{file_content}")

            if is_format_match is not None and is_format_match == False:
                print(f"Align file '{align_file}' in '{root}' has wrong format!!")
                

                # try:
                #     # Remove the file
                #     os.remove(align_path)
                #     print(f"File '{align_file}' deleted successfully.")
                # except Exception as e:
                #     print(f"Error deleting file '{align_file}': {e}")


# 테스트할 폴더 경로
folder_path = './150/alignments/'

# 기대하는 줄 수
expected_line_count = 8  # 예시로 주어진 형식에는 8줄이 있습니다.
detect_align_with_wrong_line_count(folder_path)
