import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv3D, LSTM, Dense, Dropout, Bidirectional, MaxPool3D, Activation, Reshape, SpatialDropout3D, BatchNormalization, TimeDistributed, Flatten
from tensorflow.keras.optimizers import Adam #`tf.keras.optimizers.Adam` runs slowly on M1/M2 Macs, please use the legacy Keras optimizer instead, located at `tf.keras.optimizers.legacy.Adam`
# from tensorflow.keras.optimizers.legacy import Adam # for m1/m2 mac
from tensorflow.keras.callbacks import ModelCheckpoint, LearningRateScheduler, EarlyStopping

from chatgpt import ask_chatGPT

MODEL_PATH = './models/checkpoint'


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
        self.vocab = [x for x in "abcdefghijklmnopqrstuvwxyz'?!123456789 "]
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
        print(f'predic() data: {data.shape}')
        yhat = self.model.predict(data)
        decoded = tf.keras.backend.ctc_decode(yhat, input_length=[75], greedy=True)[0][0].numpy()
        print('~'*100, 'PREDICTIONS')
        rslt = [tf.strings.reduce_join([self.num_to_char(word) for word in sentence]) for sentence in decoded]

        # TensorFlow 텐서에서 문자열 값 추출
        self.predict_string = rslt[0].numpy().decode('utf-8')
        print(self.predict_string)

        return self.predict_string


        # 문자열 list 형태
        # string_list = self.predict_string.split(' ')  # 두 번째부터 끌까지의 단어만 추출
        # print(string_list)

    def translate(self, foreign_string):
        if foreign_string != None:

            # ChatGPT에게 요청할 텍스트
            user_input = "\"{}\"의 한국어 발음 결과만 보여줘".format(foreign_string)

            # ChatGPT에게 요청 전달
            print("User: " +  user_input)
            chat_response = ask_chatGPT(user_input)
            print(chat_response)

            # ChatGPT의 응답 출력
            content = chat_response.choices[0].message.content
            print("GPT: " + content)

            return content

