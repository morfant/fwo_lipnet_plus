# Import all of the dependencies
import streamlit as st
import os 
import imageio 
import numpy as np

import tensorflow as tf 
from utils import load_data, num_to_char
from modelutil import load_model
from chatgpt import ask_chatgpt

# Set the layout to the streamlit app as wide 
st.set_page_config(layout='wide')

# Setup the sidebar
with st.sidebar: 
    st.image('https://www.onepointltd.com/wp-content/uploads/2020/03/inno2.png')
    st.title('LipBuddy')
    st.info('This application is originally developed from the LipNet deep learning model.')

st.title('LipNet Full Stack App') 
# Generating a list of options or videos 
options = os.listdir(os.path.join('..', 'data', 's1'))
selected_video = st.selectbox('Choose video', options)
st.text(selected_video )

# Generate two columns 
col1, col2 = st.columns(2)

if options: 

    # Rendering the video 
    with col1: 
        st.info('The video below displays the converted video in mp4 format')
        file_path = os.path.join('..','data','s1', selected_video)
        st.text(file_path)
        os.system(f'ffmpeg -i {file_path} -vcodec libx264 test_video.mp4 -y')

        # Rendering inside of the app
        video = open('test_video.mp4', 'rb') 
        video_bytes = video.read() 
        st.video(video_bytes)


    with col2: 
        st.info('This is all the machine learning model sees when making a prediction')
        video, annotations = load_data(tf.convert_to_tensor(file_path))
        # st.text(video.numpy().dtype)
        # st.text(video.numpy().shape)
        # st.text(video.numpy().min())
        # st.text(video.numpy().max())
        imageio.mimsave('animation.gif', (video * 255).numpy().astype('uint8').squeeze(), fps=10)
        st.image('animation.gif', width=400) 

        st.info('This is the output of the machine learning model as tokens')
        model = load_model()
        yhat = model.predict(tf.expand_dims(video, axis=0))
        st.text(yhat)
        decoder = tf.keras.backend.ctc_decode(yhat, [75], greedy=True)[0][0].numpy()
        st.text(decoder)

        # Convert prediction to text
        st.info('Decode the raw tokens into words')
        converted_prediction = tf.strings.reduce_join(num_to_char(decoder)).numpy().decode('utf-8')
        st.text(converted_prediction)
        

    if converted_prediction != None:
        # ChatGPT에게 요청할 텍스트
        user_input = "{}을 한국어 발음으로 변경해줄래".format(converted_prediction)

        # ChatGPT에게 요청 전달
        chatgpt_response = ask_chatgpt(user_input)

        # ChatGPT의 응답 출력
        st.text("User:", user_input)
        st.text("ChatGPT:", chatgpt_response)

