import os
import openai

# from openai import OpenAI
# client = OpenAI(
#     api_key=os.environ.get("OPENAI_API_KEY"),
# )

openai.api_key=os.environ.get("OPENAI_API_KEY")


# ChatGPT에 요청을 전달하는 함수
def ask_chatgpt(prompt):
    response = openai.Completion.create( 
        engine="text-davinci-003",  # 현재는 text-davinci-002 엔진을 사용합니다.
        prompt=prompt,
        max_tokens=150,  # 생성된 텍스트의 최대 토큰 수
        n=1,  # 생성할 텍스트의 수
        stop=None  # 텍스트 생성 중지 조건을 지정하려면 stop을 사용합니다.
    )

    return response.choices[0].text.strip()


# if __name__ == '__main__':
#     # ChatGPT에게 요청할 텍스트
#     user_input = "Tell me about artificial intelligence."

#     # ChatGPT에게 요청 전달
#     chatgpt_response = ask_chatgpt(user_input)

#     # ChatGPT의 응답 출력
#     print("User:", user_input)
#     print("ChatGPT:", chatgpt_response)
