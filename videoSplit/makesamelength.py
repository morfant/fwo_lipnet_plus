import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips

def get_files_in_folder(folder_path):
    # 폴더 내 모든 파일의 리스트를 가져옴
    files = os.listdir(folder_path)

    # 파일만 추려내어 리스트에 저장
    file_list = [file for file in files if os.path.isfile(os.path.join(folder_path, file))]

    return file_list

def adjust_video_length(input_video, target_duration):
    # 비디오 클립 로드
    video_clip = VideoFileClip('./data/splited_videos/' + input_video)

    # 현재 비디오의 길이
    current_duration = video_clip.duration
    print(current_duration)

    # 타겟 길이까지 확장하거나 잘라냄
    if current_duration > target_duration:
        # 길이가 긴 경우 자르기
        video_clip = video_clip.subclip(0, target_duration)
    elif current_duration < target_duration:
        # 길이가 짧은 경우 확장하기
        repetitions = int(target_duration / current_duration)
        video_clip = concatenate_videoclips([video_clip] * repetitions)

    return video_clip

def find_longest_video(folder_path):
    # 폴더 내 모든 파일의 리스트를 가져옴
    files = os.listdir(folder_path)

    # 비디오 파일만 추려내어 리스트에 저장
    video_files = [file for file in files if file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]

    if not video_files:
        print("폴더에 비디오 파일이 없습니다.")
        return None

    longest_duration = 0
    longest_video = None

    for video_file in video_files:
        video_path = os.path.join(folder_path, video_file)
        video_clip = VideoFileClip(video_path)
        video_duration = video_clip.duration

        if video_duration > longest_duration:
            longest_duration = video_duration
            longest_video = video_file

        video_clip.close()

    return longest_video, longest_duration


def find_short_videos(folder_path, threshold_frame_length):
    short_videos = []

    # 폴더 내 모든 파일의 리스트를 가져옴
    files = os.listdir(folder_path)

    # 비디오 파일만 추려내어 리스트에 저장
    video_files = [file for file in files if file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov'))]

    for video_file in video_files:
        video_path = os.path.join(folder_path, video_file)
        video_clip = VideoFileClip(video_path)

        # 현재 영상의 프레임 길이
        current_frame_length = video_clip.fps * video_clip.duration

        if current_frame_length < threshold_frame_length:
            short_videos.append((video_file, current_frame_length))

        video_clip.close()

    return short_videos


if __name__ == "__main__":

    TARGET_PATH = './data/splited_videos'
    # 입력 비디오 파일들
    # input_videos = get_files_in_folder(TARGET_PATH)

    # for file_name in input_videos:
    #     print(file_name)

    # 가장 긴 비디오 파일 찾기
    # longest_video, duration = find_longest_video(TARGET_PATH)

    # if longest_video:
    #     print(f"가장 긴 비디오 파일: {longest_video}")
    #     print(f"길이: {duration} 초")
    # else:
    #     print("폴더에 비디오 파일이 없습니다.")

    # 프레임 길이 임계값 설정 (예: 120 프레임, 4초)
    threshold_frame_length = 100 

    # 특정 프레임 길이보다 짧은 비디오 찾기
    short_videos = find_short_videos(TARGET_PATH, threshold_frame_length)

    if short_videos:
        print(f"프레임 길이가 {threshold_frame_length}보다 짧은 비디오:")
        for video, frame_length in short_videos:
            print(f"{video}: {frame_length} 프레임")
    else:
        print(f"프레임 길이가 {threshold_frame_length}보다 짧은 비디오가 없습니다.")




    # 타겟 길이 설정 (예: 5초)
    target_duration = 5

    # 각 비디오를 타겟 길이로 조절하여 새로운 비디오 파일로 저장
    # for input_video in input_videos:
    #     output_video = f"adjusted_{target_duration}s_{input_video}"
    #     adjusted_clip = adjust_video_length(input_video, target_duration)
    #     adjusted_clip.write_videofile(output_video, codec='libx264', audio_codec='aac')
    #     adjusted_clip.close()
