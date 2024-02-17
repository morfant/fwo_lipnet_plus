import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv3D, LSTM, Dense, Dropout, Bidirectional, MaxPool3D, Activation, Reshape, SpatialDropout3D, BatchNormalization, TimeDistributed, Flatten
from tensorflow.keras.optimizers import Adam #`tf.keras.optimizers.Adam` runs slowly on M1/M2 Macs, please use the legacy Keras optimizer instead, located at `tf.keras.optimizers.legacy.Adam`
# from tensorflow.keras.optimizers.legacy import Adam # for m1/m2 mac
from tensorflow.keras.callbacks import ModelCheckpoint, LearningRateScheduler, EarlyStopping

from chatgpt import ask_chatGPT

MODEL_PATH = '/Users/baggeunsu/fwo_lipnet_plus/models/kor_56/checkpoint'


class LipRead:
    def __init__(self):
        self.model = None
        self.predict_string = None

    def setModel(self):
        self.model = Sequential()
        # model.add(Conv3D(128, 3, input_shape=(75,46,140,1), padding='same'))
        self.model.add(Conv3D(128, 3, input_shape=(75,50,100,1), padding='same'))
        self.model.add(Activation('relu'))
        self.model.add(MaxPool3D((1,2,2)))

        self.model.add(Conv3D(256, 3, padding='same'))
        self.model.add(Activation('relu'))
        self.model.add(MaxPool3D((1,2,2)))

        self.model.add(Conv3D(75, 3, padding='same'))
        self.model.add(Activation('relu'))
        self.model.add(MaxPool3D((1,2,2)))

        self.model.add(TimeDistributed(Flatten()))

        self.model.add(Bidirectional(LSTM(128, kernel_initializer='Orthogonal', return_sequences=True)))
        self.model.add(Dropout(.5))

        self.model.add(Bidirectional(LSTM(128, kernel_initializer='Orthogonal', return_sequences=True)))
        self.model.add(Dropout(.5))

        self.model.add(Dense(self.char_to_num.vocabulary_size()+1, kernel_initializer='he_normal', activation='softmax'))

    def prepare(self):

        # eng
        # self.vocab = [x for x in "abcdefghijklmnopqrstuvwxyz'?!123456789 "]

        # kor
        # start_unicode = ord('가')  # '가'의 유니코드 값
        # end_unicode = ord('힣')    # '힣'의 유니코드 값
        # self.vocab = [chr(code) for code in range(start_unicode, end_unicode + 1)]
        
        self.vocab = ['', '빈', '약', '한', '대', '화', '일', '반', '된', '영', '최', '초', '의', '단', '어', '게', '임', '세', '련', '잡', '담', '자', '신', '을', '위', '해', '창', '조', '언', '읽', '기', '와', '쓰', '능', '력', '쌀', '유', '사', '번', '역', '장', '애', '라', '는', '마', '이', '너', '스', '요', '인', '오', '돌', '토', '솟', '은', '끌', '올', '려', '진', '밧', '줄', '불', '가', '로', '움', '짢', '운', '흘', '렀', '다', '수', '날', '씨', '완', '벽', '하', '네', '바', '람', '처', '럼', '엽', '렵', '정', '교', '듬', '지', '배', '적', '치', '엑', '셀', '러', '레', '터', '연', '범', '주', '들', '상', '발', '달', '편', '웰', '메', '드', '를', '있', '습', '니', '프', '티', '더', '말', '선', '천', '후', '곱', '씹', '뚝', '끊', '느', '낌', '미', '래', '향', '심', '증', '여', '겹', '보', '강', '재', '엉', '성', '구', '현', '분', '별', '으', '론', '결', '제', '준', '감', '각', '흔', '히', '종', '산', '필', '충', '건', '빨', '간', '케', '디', '잘', '입', '양', '내', '겠', '추', '블', '랙', '아', '금', '나', '갔', '원', '시', '문', '도', '뒷', '넘', '겨', '생', '비', '견', '될', '온', '전', '못', '남', '알', '록', '난', '폭', '리', '꽂', '았', '공', '벌', '고', '회', '면', '우', '윤', '허', '파', '동', '물', '에', '서', '방', '객', '팬', '낙', '웃', '며', '함', '존', '손', '험', '것', '체', '핵', '과', '관', '계', '명', '형', '용', '뿌', '렬', '격', '차', '패', '턴', '근', '본', '할', '행', '락', '했', '야', '찬', '식', '빠', '짐', '잔', '껍', '데', '깨', '실', '때', '갉', '먹', '음', '틀', '림', '없', '술', '부', '극', '법', '볼', '멘', '소', '닥', '직', '경', '센', '노', '탤', '릭', '외', '열', '버', '링', '났', '좌', '안', '석', '글', '순', '청', '채', '책', '찰', '옥', '포', '옢', '키', '얇', '폰', '밟', '었', '학', '잠', '깐', '그', '졌', '릿', '쇠', '냄', '새', '코', '잊', '않', '통', '당', '꽁', '훌', '륭', '득', '특', '태', '귀', '모', '빙', '괄', '힘', '르', '앙', '맞', '무', '슨', '좋', '광', '묻', '왜', '곡', '친', '밀', '높', '만', '붉', '섬', '점', '검', '및', '중', '매', '개']

        self.char_to_num = tf.keras.layers.StringLookup(vocabulary=self.vocab, oov_token="")
        self.num_to_char = tf.keras.layers.StringLookup(vocabulary=self.char_to_num.get_vocabulary(), oov_token="", invert=True)

        print(
            f"The vocabulary is: {self.char_to_num.get_vocabulary()}\n"
            f"(size ={self.char_to_num.vocabulary_size()})"
        )



    def load_model(self):
        self.model.load_weights(MODEL_PATH)
        self.model.summary()


    def init(self):
        self.prepare()
        self.setModel()
        self.load_model()
        

    def predict(self, data):
        data = tf.expand_dims(data, axis=0)
        print(f'predic() data shape: {data.shape}')
        yhat = self.model.predict(data)
        decoded = tf.keras.backend.ctc_decode(yhat, input_length=[75], greedy=True)[0][0].numpy()
        print('~'*100, 'PREDICTIONS BEGIN')
        rslt = [tf.strings.reduce_join([self.num_to_char(word) for word in sentence]) for sentence in decoded]

        # TensorFlow 텐서에서 문자열 값 추출
        self.predict_string = rslt[0].numpy().decode('utf-8')
        print(f'prediction: {self.predict_string}')
        print('~'*100, 'PREDICTION END')

        return self.predict_string


        # 문자열 list 형태
        # string_list = self.predict_string.split(' ')  # 두 번째부터 끌까지의 단어만 추출
        # print(string_list)

    def translate(self, foreign_string):
        if foreign_string != None:

            # ChatGPT에게 요청할 텍스트
            user_input = "\"{}\"의 한국어 발음 결과를 'kor_result: 한국어 발음 결과' 의 형식을 지켜서 표현해줘".format(foreign_string)

            # ChatGPT에게 요청 전달
            # print("User: " +  user_input)
            chat_response = ask_chatGPT(user_input)
            # print(chat_response)

            # ChatGPT의 응답 출력
            content = chat_response.choices[0].message.content
            # print("GPT: " + content)
            result = content.split("kor_result: ")[1]
            # print(result)

            return result 

