# extract_mouth_batch.py를 이용하여 root_folder 아래의 모든 폴더의 영상들 각각에 대한 입모양 이미지들을 만들어낸다.
import os
from pathlib import Path

def process_folders(root_folder, script_path, pattern, face_landmarks):
    for subdir in Path(root_folder).rglob("*"):
        if subdir.is_dir():
            command = f"python {script_path} '{subdir}' '{pattern}' '{face_landmarks}'"
            os.system(command)

# 사용 예시:
root_folder = '../data/500_each/atemp8'
script_path = 'extract_mouth_batch.py'
pattern = '*.mpg'
face_landmarks = '../predictors/shape_predictor_68_face_landmarks.dat'

process_folders(root_folder, script_path, pattern, face_landmarks)
