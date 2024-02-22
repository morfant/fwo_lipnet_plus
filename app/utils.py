import tensorflow as tf
from typing import List
import cv2
import os 

vocab = [x for x in "abcdefghijklmnopqrstuvwxyz'?!123456789 "]
char_to_num = tf.keras.layers.StringLookup(vocabulary=vocab, oov_token="")
# Mapping integers back to original characters
num_to_char = tf.keras.layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), oov_token="", invert=True
)

def load_video(path:str) -> List[float]: 
    print("load_video()")
    print(path)
    cap = cv2.VideoCapture(path)
    frames = []
    print(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    n = min(75, n)
    # for _ in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))): 
    for _ in range(n): 
        ret, frame = cap.read()
        frame = tf.image.rgb_to_grayscale(frame)
        # frames.append(frame[190:236,80:220,:]) # for s1, 236 - 190 = 46 / 220 - 80 = 140 --> 데이터 shape 을 결정
        # frames.append(frame[190:236,100:240,:]) # s2
        # frames.append(frame[165:211,120:260,:])
        # frames.append(frame[265:311,250:390,:])
        frames.append(frame[385:431,270:410,:])
    cap.release()
    
    mean = tf.math.reduce_mean(frames)
    std = tf.math.reduce_std(tf.cast(frames, tf.float32))
    return tf.cast((frames - mean), tf.float32) / std
    
def load_alignments(path:str) -> List[str]: 
    # print("load_aligments()")
    # print(path)
    with open(path, 'r') as f: 
        lines = f.readlines() 
    tokens = []
    for line in lines:
        line = line.split()
        if line[2] != 'sil': 
            tokens = [*tokens,' ',line[2]]
    return char_to_num(tf.reshape(tf.strings.unicode_split(tokens, input_encoding='UTF-8'), (-1)))[1:]

def load_data(path: str): 
    print("load_data()")
    path = bytes.decode(path.numpy())
    # file_name = path.split('/')[-1].split('.')[0]
    file_name = path.split('/')[-1]
    print(file_name)

    # File name splitting for windows
    # file_name = path.split('\\')[-1].split('.')[0]

    # video_path = os.path.join('..','data','s1',f'{file_name}.mpg')
    video_path = os.path.join('..','data','test',f'{file_name}')

    # alignment_path = os.path.join('..','data','alignments','s1',f'{file_name}.align')
    frames = load_video(video_path) 
    # alignments = load_alignments(alignment_path)
    
    # return frames, alignments
    return frames