from moviepy.video.io.VideoFileClip import VideoFileClip
import json

def get_data_by_key_from_file(json_file_path, target_key):
    result_list = []

    with open(json_file_path, 'r') as json_file:
        json_data = json.load(json_file)

        # JSON 파일이 배열을 담고 있는 경우
        if isinstance(json_data, list):
            for item in json_data:
                if target_key in item:
                    result_list.append(item[target_key])
        else:
            print("JSON 파일이 배열을 포함하지 않습니다.")

    return result_list


def split_video(input_video, output_folder, json_file):
    # 비디오 클립 로드
    video_clip = VideoFileClip(input_video)

    # JSON 파일에서 시작 지점과 끝 지점 읽기
    with open(json_file, 'r') as json_file:
        data = json.load(json_file)

    # 비디오를 나누기 위한 정보 추출
    infos = []
    infos = get_data_by_key_from_file(json_file_path, "Sentence_info")

    # for item in infos:
    #     if target_key in item:
    #         result_list.append(item[target_key])

    # return result_list

    print(infos[0])

    for idx, split in enumerate(infos[0]):
        start_time = split.get('start_time', 0)
        end_time = split.get('end_time', video_clip.duration)

        print("--------------------------------")
        print(split.get('ID'))
        print(split.get('sentence_text'))
        print(str(start_time) + " / " + str(end_time))

        # 비디오 클립에서 일부 추출
        sub_clip = video_clip.subclip(start_time, end_time)

        # 나눠진 비디오를 파일로 저장
        output_path = f"{output_folder}/split_{idx + 1}.mp4"
        sub_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

    # 원본 비디오 클립을 닫음
    video_clip.close()

if __name__ == "__main__":
    file_name = "lip_J_1_F_02_C032_A_010"
    input_video_path = "./data/video/" + file_name + ".mp4"  # 입력 비디오 파일 경로
    json_file_path = "./data/json/" + file_name + ".json"  # JSON 파일 경로
    output_folder_path = "./data/splited_videos"  # 출력 폴더 경로

    split_video(input_video_path, output_folder_path, json_file_path)
