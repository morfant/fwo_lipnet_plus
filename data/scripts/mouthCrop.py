import cv2
import dlib

# 얼굴 감지기 초기화
detector = dlib.get_frontal_face_detector()

print(cv2.getBuildInformation())

# 비디오 파일 경로 설정
video_path = '/Users/giy/Projects/fwo_lipnet_plus/data/s22/bbad4s.mpg'

# 출력 동영상 파일 경로 설정
# output_path = '/Users/giy/Projects/fwo_lipnet_plus/data/s28/bbac5n_crop.mpg'
output_path = '/Users/giy/Projects/fwo_lipnet_plus/data/s22/bbad4s_crop.mpg'

# 동영상 열기
cap = cv2.VideoCapture(video_path)

# 동영상 속성 가져오기
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

# 동영상 저장을 위한 VideoWriter 설정
# fourcc = cv2.VideoWriter_fourcc('M', 'P', 'G', '1')  # 수정 전: fourcc = cv2.VideoWriter_fourcc(*'MPG1')
fourcc = cv2.VideoWriter_fourcc('A', 'V', 'C', '1')  # 수정 전: fourcc = cv2.VideoWriter_fourcc(*'MPG1')
# fourcc = cv2.VideoWriter_fourcc('H','2','6','4')  # 수정 전: fourcc = cv2.VideoWriter_fourcc(*'MPG1')
# fourcc = cv2.VideoWriter_fourcc('M', 'P', '4', 'V')  # 수정 전: fourcc = cv2.VideoWriter_fourcc(*'MPG1')
# fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')  # 수정 전: fourcc = cv2.VideoWriter_fourcc(*'MPG1')
# fourcc = cv2.VideoWriter_fourcc(*'X264')  # 수정 전: fourcc = cv2.VideoWriter_fourcc(*'MPG1')
out = cv2.VideoWriter(output_path, fourcc, 20.0, (frame_width, frame_height))

while True:
    # 프레임 읽기
    ret, frame = cap.read()

    if not ret:
        break

    # 흑백으로 변환 (얼굴 감지기는 흑백 영상을 사용합니다)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 얼굴 감지
    faces = detector(gray)

    # 얼굴이 감지되면 입 주변을 크롭하여 출력 동영상에 저장
    for face in faces:
        x, y, w, h = face.left(), face.top(), face.width(), face.height()
        margin = 20  # 입 주변 크롭을 위한 여유 공간
        cropped_face = frame[y-margin:y+h+margin, x-margin:x+w+margin]

        # 크롭된 영상 저장
        out.write(cropped_face)

        # 얼굴 주변에 사각형 표시 (테스트용)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # 화면에 출력 (테스트용)
    cv2.imshow('Frame', frame)

    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 종료 시 리소스 해제
cap.release()
out.release()
cv2.destroyAllWindows()
