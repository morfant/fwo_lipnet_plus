# fwo_lipnet_plus

환경
python3.11.7
Apple silicon M1


## libndi.dylib, NDIlib.cpython-311-darwin.so
python3.11을 위해 빌드한 python NDI wrapper

# ffmpeg.py
deprecate 된 np.float, np.int 를 수정한 버전

# preProcess.ipynb
데이터 전처리를 위한 과정들을 담은 파일

# LipNet.ipynb
모델 학습을 위한 코드들이 들어있는 파일

# scripts 폴더
데이터 전처리를 위해 사용했던 여러가지 스크립트들

# run.sh
네트워크 드라이브 마운트, 레솔룸 실행, 맥스 패치 실행, 파이썬 앱 실행을 동시에 처리하는 쉘 스크립트

# run2.app
automator를 이용해 응용프로그램 형식으로 만든, run.sh를 실행하는 프로그램 - 컴퓨터가 켜질 때 자동 실행을 구성하기 위해서

# max_patch
com1과 com2 에 사용된 max patch 들