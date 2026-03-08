import streamlit as st
import os
import json
import random
import tempfile
import pandas as pd
from datetime import datetime
from openai import OpenAI

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="MindNest AI",
    page_icon="☁️",
    layout="centered"
)

# ==============================
# API KEY
# ==============================
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("Thiếu OPENAI_API_KEY trong Secrets")
    st.stop()

client = OpenAI(api_key=api_key)

# ==============================
# DATA FILE
# ==============================
DATA_FILE = "emotion_data.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE,"w") as f:
        json.dump([],f)

def save_emotion(data):
    with open(DATA_FILE,"r") as f:
        old = json.load(f)

    old.append(data)

    with open(DATA_FILE,"w") as f:
        json.dump(old,f,default=str)

def load_data():
    with open(DATA_FILE) as f:
        return json.load(f)

# ==============================
# USERS
# ==============================
with open("users.json","r",encoding="utf-8") as f:
    USERS=json.load(f)

# ==============================
# SESSION
# ==============================
if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if "messages" not in st.session_state:
    st.session_state.messages=[]

# ==============================
# LOGIN PAGE
# ==============================
if not st.session_state.logged_in:

    st.markdown("# ☁️ MindNest AI")
    st.markdown("### Hệ thống hỗ trợ sức khỏe tinh thần học sinh")

    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu",type="password")

    login_btn = st.button("🚀 Đăng nhập")

    if login_btn or password.endswith("\n"):

        if username in USERS and USERS[username]["password"]==password:

            st.session_state.logged_in=True
            st.session_state.username=username
            st.session_state.role=USERS[username]["role"]

            st.rerun()

        else:
            st.error("Sai tài khoản")

    st.stop()

role = st.session_state.role

# ==============================
# CSS UI
# ==============================
st.markdown("""
<style>

.stApp{
background:linear-gradient(135deg,#ffd6ec,#e6ccff,#d6e4ff);
}

.chat-user{
background:#c8f7ff;
padding:10px;
border-radius:12px;
margin:5px;
}

.chat-bot{
background:white;
padding:10px;
border-radius:12px;
margin:5px;
}

button{
border-radius:20px!important;
}

</style>
""",unsafe_allow_html=True)

# ==============================
# EMOTION DETECT
# ==============================
def detect_emotion(text):

    prompt=f"""
Phân loại cảm xúc học sinh

happy
sad
anxious
stress
crisis
neutral

Câu: {text}

Trả lời 1 từ.
"""

    try:

        r=client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )

        return r.output_text.strip().lower()

    except:

        return "neutral"

# ==============================
# CHAT AI
# ==============================
def ask_ai(text):

    system="""
Bạn là MindNest AI

Bạn hỗ trợ tâm lý học sinh
Nói nhẹ nhàng tích cực
"""

    try:

        r=client.responses.create(
            model="gpt-4o-mini",
            input=system+"\n"+text
        )

        return r.output_text

    except:

        return "Xin lỗi hệ thống đang bận"

# ==============================
# TTS
# ==============================
def speak(text):

    try:

        speech=tempfile.NamedTemporaryFile(delete=False,suffix=".mp3")

        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="nova",
            input=text
        ) as r:

            r.stream_to_file(speech.name)

        return speech.name

    except:

        return None

# ==============================
# STUDENT MODE
# ==============================
if role=="student":

    st.title("☁️ MindNest AI")

    st.success("Xin chào 👋 MindNest luôn sẵn sàng lắng nghe bạn!")

    for m in st.session_state.messages:

        if m["role"]=="user":
            st.markdown(f"<div class='chat-user'>🙂 {m['content']}</div>",unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bot'>☁️ {m['content']}</div>",unsafe_allow_html=True)

    user_input = st.chat_input("Hãy chia sẻ cảm xúc của bạn...")

    if user_input:

        st.session_state.messages.append({"role":"user","content":user_input})

        emotion=detect_emotion(user_input)

        save_emotion({
            "student":st.session_state.username,
            "emotion":emotion,
            "time":str(datetime.now())
        })

        reply=ask_ai(user_input)

        st.session_state.messages.append({"role":"assistant","content":reply})

        audio=speak(reply)

        st.rerun()

# ==============================
# TEACHER DASHBOARD
# ==============================
if role=="teacher":

    st.title("📊 Dashboard sức khỏe tinh thần")

    data=load_data()

    if len(data)==0:

        st.info("Chưa có dữ liệu")

        st.stop()

    df=pd.DataFrame(data)

    st.subheader("🌈 Tổng quan cảm xúc lớp")

    chart=df["emotion"].value_counts()

    st.bar_chart(chart)

    st.subheader("👩‍🎓 Theo từng học sinh")

    students=df["student"].unique()

    s=st.selectbox("Chọn học sinh",students)

    df_s=df[df["student"]==s]

    st.line_chart(df_s["emotion"].value_counts())

    st.subheader("📄 Lịch sử")

    st.dataframe(df_s)
