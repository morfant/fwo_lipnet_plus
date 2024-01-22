''' 
extract_mouth_batch.py
    This script will extract mouth crop of every single video inside source directory
    while preserving the overall structure of the source directory content.

Usage:
    python extract_mouth_batch.py [source directory] [pattern] [face predictor path]

    pattern: *.avi, *.mpg, etc 

Example:
    python scripts/extract_mouth_batch.py evaluation/samples/GRID/ *.mpg common/predictors/shape_predictor_68_face_landmarks.dat

    Will make directory TARGET and process everything inside evaluation/samples/GRID/ that match pattern *.mpg.
'''

from lipnet.lipreading.videos import Video
import os, fnmatch, sys, errno  
from skimage import io
import numpy as np

SOURCE_PATH = sys.argv[1]
SOURCE_EXTS = sys.argv[2]
# TARGET_PATH = sys.argv[3]

FACE_PREDICTOR_PATH = sys.argv[3]

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def find_file_num(directory, pattern):
    file_count = 0
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                file_count += 1
    return file_count


def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename


file_num = find_file_num(SOURCE_PATH, SOURCE_EXTS)
cur_file_count = 1

for filepath in find_files(SOURCE_PATH, SOURCE_EXTS):
    print("=" * 40)
    print ("{} of {} file(s)".format(cur_file_count, file_num))
    print ("Processing: {}".format(filepath))
    video = Video(vtype='face', face_predictor_path=FACE_PREDICTOR_PATH).from_video(filepath)

    filepath_wo_ext = os.path.splitext(filepath)[0]
    filename = filepath_wo_ext.split('/')[-1]
    # print(filename)
    target_dir = os.path.join(SOURCE_PATH, 'cropped', filename)
    # print(target_dir)
    mkdir_p(target_dir)

    i = 0
    for frame in video.mouth:
        frame = (frame * 255).astype(np.uint8)
        # print(frame)
        io.imsave(os.path.join(target_dir, "mouth_{0:03d}.png".format(i)), frame)
        i += 1
    print ("Saved at: {}".format(target_dir))
    cur_file_count += 1
