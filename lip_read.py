import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv3D, LSTM, Dense, Dropout, Bidirectional, MaxPool3D, Activation, Reshape, SpatialDropout3D, BatchNormalization, TimeDistributed, Flatten
from tensorflow.keras.optimizers import Adam #`tf.keras.optimizers.Adam` runs slowly on M1/M2 Macs, please use the legacy Keras optimizer instead, located at `tf.keras.optimizers.legacy.Adam`
# from tensorflow.keras.optimizers.legacy import Adam # for m1/m2 mac
from tensorflow.keras.callbacks import ModelCheckpoint, LearningRateScheduler, EarlyStopping

MODEL_PATH = './models/checkpoint'


class LipRead:
    def __init__(self):
        self.model = None

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

