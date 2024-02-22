import cv2
import os
import subprocess
import re


def get_video_frame_count(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video file is opened successfully
    if not cap.isOpened():
        print(f"Error: Couldn't open video file '{video_path}'")
        return None
    
    # Get the total number of frames in the video
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Release the video capture object
    cap.release()
    
    return frame_count


def get_video_resolution(video_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    # Check if the video file is opened successfully
    if not cap.isOpened():
        print(f"Error: Couldn't open video file '{video_path}'")
        return None
    
    # Get the width and height of the video frames
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Release the video capture object
    cap.release()
    
    return width, height


def detect_videos_with_wrong_frame_count(folder_path, expected_frame_count=75):

    # Iterate through all files and subdirectories in the specified folder
    for root, dirs, files in os.walk(folder_path):
        # print(dirs)
        # Filter out only video files
        video_files = [file for file in files if file.lower().endswith(('.mpg'))]
        
        # Check frame count for each video file
        for video_file in video_files:
            # print(video_file)
            video_path = os.path.join(root, video_file)
            frame_count = get_video_frame_count(video_path)
            
            if frame_count is not None and frame_count != expected_frame_count:
                print(f"Video '{video_file}' in '{root}' has {frame_count} frames, which is not the expected {expected_frame_count} frames.")
                try:
                    # Remove the file
                    os.remove(video_path)
                    print(f"File '{video_file}' deleted successfully.")
                except Exception as e:
                    print(f"Error deleting file '{video_file}': {e}")


def detect_videos_with_wrong_resolution(folder_path, expected_resolution=(360, 288)):
    # Iterate through all files and subdirectories in the specified folder
    for root, dirs, files in os.walk(folder_path):
        # print(dirs)
        # Filter out only video files
        video_files = [file for file in files if file.lower().endswith(('.mpg'))]
        
        # Check frame count for each video file
        for video_file in video_files:
            # print(video_file)
            video_path = os.path.join(root, video_file)
            resolution = get_video_resolution(video_path)
            
            if resolution is not None and resolution != expected_resolution:
                print(f"Video '{video_file}' in '{root}' has resolution {resolution}, which is not the expected {expected_resolution} resolution.")

                try:
                    # Remove the file
                    os.remove(video_path)
                    print(f"File '{video_file}' deleted successfully.")
                except Exception as e:
                    print(f"Error deleting file '{video_file}': {e}")


def check_video_problems(folder_path):

    # Iterate through all files and subdirectories in the specified folder
    for root, dirs, files in os.walk(folder_path):
        # print(dirs)
        # Filter out only video files
        video_files = [file for file in files if file.lower().endswith(('.mpg'))]
        
        # Check frame count for each video file
        for video_file in video_files:
            video_path = os.path.join(root, video_file)

            command = [
                'ffmpeg',
                '-v', 'error',           # 로그 출력을 최소화
                '-i', video_path,        # 입력 비디오 파일
                '-f', 'null',            # 출력 형식
                '-'
            ]

            try:
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                output = result.stderr

                # Check for specific warning messages
                ac_tex_damaged = re.search(r'\[mpeg1video @ .*\] ac-tex damaged', output)
                warning_mvs_not_available = re.search(r'\[mpeg1video @ .*\] Warning MVs not available', output)

                if ac_tex_damaged:
                    print(f'Warning: ac-tex damaged in {video_path}')

                if warning_mvs_not_available:
                    print(f'Warning: MVs not available in {video_path}')

            except subprocess.CalledProcessError as e:
                print(f'Error checking {video_path}: {e}')


# Example usage:
folder_path = '../'
detect_videos_with_wrong_frame_count(folder_path)
detect_videos_with_wrong_resolution(folder_path)
# check_video_problems(folder_path)

# # 특정 폴더에서 모든 비디오 파일에 대해 체크
# folder_path = '/path/to/videos'
# for filename in os.listdir(folder_path):
#     if filename.endswith(('.mp4', '.avi', '.mkv', '.mpg')):  # 지원하는 비디오 확장자 추가
#         video_path = os.path.join(folder_path, filename)
#         check_video_problems(video_path)

