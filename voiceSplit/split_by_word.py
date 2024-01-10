import os
from google.cloud import speech_v1p1beta1 as speech
from pydub import AudioSegment

api_key_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')

def convert_to_supported_format(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="wav")


def transcribe_audio_with_timing(api_key_path, audio_file_path):

    # API 키 파일 경로 설정
    client = speech.SpeechClient.from_service_account_file(api_key_path)

    # 음성 파일 로드
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code="ko-KR",
        enable_word_time_offsets=True,
    )

    # 음성을 텍스트로 변환
    response = client.recognize(config=config, audio=audio)

    # 각 단어의 시작 및 종료 시간 출력
    for result in response.results:
        print(result)
        for word_info in result.alternatives[0].words:
            # print(word_info)
            word = word_info.word
            start_time = word_info.start_time.total_seconds()
            end_time = word_info.end_time.total_seconds()
            print(f"단어: {word}, 시작 시간: {start_time}, 종료 시간: {end_time}")

if __name__ == "__main__":

    # API 키 파일 경로 및 음성 파일 경로 설정
    output_wav_path = "./output_file.wav"
    audio_file_path = './data/lip_K_5_M_06_C920_A_001_mono.wav'
    convert_to_supported_format(audio_file_path, output_wav_path)
    transcribe_audio_with_timing(api_key_path, output_wav_path)
