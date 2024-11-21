import streamlit as st
from openai import OpenAI
import pandas as pd

# 데이터 저장을 위한 변수
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = 0

# header를 이용하면 제목 입력이 가능합니다

st.header("학생들이 만든 자료를 바탕으로 문제 만들어주는 콘텐츠")

st.divider()

# openai에 연결하기

client = OpenAI(api_key = st.secrets["api_key"])

# 데이터 입력받기

uploaded_file = st.file_uploader("파일을 업로드하세요")

@st.cache_data
def upload_to_openai(file):
    # #파일 올리기
    message_file = client.files.create(
        file=file, purpose="assistants"
    )
    #thread 만들기
    thread = client.beta.threads.create(
        messages=[
            {
            "role": "user",
            "content": "다음 파일을 읽고 문제를 만들어줘",
            "attachments" :[{ "file_id": message_file.id, "tools": [{"type": "file_search"}] }]
            }
        ]
    )
    #run 하기
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=st.secrets["assistant_id"]
    )

    messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

    st.session_state['thread_id'] = thread.id
    return thread.id, messages[0].content[0].text.value

if uploaded_file :
    id, text = upload_to_openai(uploaded_file)
    st.write(id)
    st.divider()
    st.write(text)

# 데이터 저장을 위한 함수
@st.cache_data
def generate_df(thread_id):
    data = {
        "thread_id" : [thread_id]
    }
    df = pd.DataFrame(data)
    return df

if st.button("결과 다운로드받기"):
    df = generate_df(st.session_state['thread_id'])
    csv = df.to_csv(index = False, encoding="cp949")
    st.download_button(label = "눌러서 파일 다운로드 받기", data = csv, file_name = f"data.csv")