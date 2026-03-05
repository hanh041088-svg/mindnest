import streamlit as st
import os
import json
import random
import tempfile
from datetime import datetime
from openai import OpenAI

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(
    page_title="MindNest 🌥️",
    page_icon="☁️",
    layout="centered"
)

# ======================
# API KEY
# ======================
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("API key chưa cấu hình.")
    st.stop()

client = OpenAI(api_key=api_key)

# ======================
# FILE PATH
# ======================
USER_FILE = "users.json"
EMOTION_FILE = "emotion_log.json"

# tạo file emotion nếu chưa có
if not os.path.exists(EMOTION_FILE):
    with open(EMOTION_FILE,"w") as f:
        json.dump([],f)

# ======================
# LOAD USERS
# ======================
with open(USER_FILE,"r",encoding="utf-8") as f:
    USERS=json.load(f)

# ======================
# LOGIN STATE
# ======================
if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

# ======================
# LOGIN PAGE
# ======================
if not st.session_state.logged_in:

    st.title("☁️ MindNest Login")

    username=st.text_input("Tên đăng nhập")
    password=st.text_input("Mật khẩu",type="password")

    if st.button("Đăng nhập"):

        if username in USERS and USERS[username]["password"]==password:

            st.session_state.logged_in=True
            st.session_state.username=username
            st.session_state.role=USERS[username]["role"]

            st.success("Đăng nhập thành công")
            st.rerun()

        else:
            st.error("Sai tài khoản")

    st.stop()

# ======================
# UI STYLE
# ======================
st.markdown("""
<style>

.stApp{
background:linear-gradient(135deg,#ffd6ec,#e6ccff,#d6e4ff,#ffe6f7);
background-size:400% 400%;
animation:gradientBG 10s ease infinite;
}

@keyframes gradientBG{
0%{background-position:0% 50%}
50%{background-position:100% 50%}
100%{background-position:0% 50%}
}

.chat-user{
background:#e0f7fa;
padding:10px;
border-radius:12px;
margin:6px;
}

.chat-bot{
background:white;
padding:10px;
border-radius:12px;
margin:6px;
box-shadow:0 2px 8px rgba(0,0,0,0.1);
}

</style>
""",unsafe_allow_html=True)

# ======================
# HEADER
# ======================
st.markdown("""
### ☁️ MindNest  
AI hỗ trợ sức khỏe tinh thần học sinh
""")

# ======================
# SESSION
# ======================
if "messages" not in st.session_state:
    st.session_state.messages=[]

if "student_id" not in st.session_state:
    st.session_state.student_id=f"HS{random.randint(100,999)}"

role=st.session_state.role

# ======================
# SAVE EMOTION
# ======================
def save_emotion(student,emotion):

    with open(EMOTION_FILE,"r") as f:
        data=json.load(f)

    data.append({
        "student":student,
        "emotion":emotion,
        "time":datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    with open(EMOTION_FILE,"w") as f:
        json.dump(data,f)

# ======================
# DETECT EMOTION
# ======================
def detect_emotion(text):

    prompt=f"""
Phân loại cảm xúc học sinh.
Chỉ trả về 1 từ:

happy
sad
anxious
stress
crisis
neutral

Câu: {text}
"""

    try:

        res=client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )

        return res.output_text.strip().lower()

    except:
        return "neutral"

# ======================
# CHAT AI
# ======================
def chat_ai(user_text):

    system_prompt="""
Bạn là AI hỗ trợ tâm lý học sinh.
Giọng nhẹ nhàng, tích cực.
Không chẩn đoán bệnh.
"""

    history=""

    for m in st.session_state.messages:
        history+=f"{m['role']}:{m['content']}\n"

    prompt=system_prompt+history+f"user:{user_text}"

    try:

        res=client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )

        return res.output_text

    except:

        return "Xin lỗi, AI đang bận."

# ======================
# TEXT TO SPEECH
# ======================
def speak(text):

    try:

        speech=tempfile.NamedTemporaryFile(delete=False,suffix=".mp3")

        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="nova",
            input=text
        ) as response:

            response.stream_to_file(speech.name)

        return speech.name

    except:
        return None

# ======================
# STUDENT MODE
# ======================
if role=="student":

    st.subheader("Chat với MindNest")

    for m in st.session_state.messages:

        if m["role"]=="user":
            st.markdown(f"<div class='chat-user'>{m['content']}</div>",unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bot'>{m['content']}</div>",unsafe_allow_html=True)

    user_input=st.chat_input("Bạn đang cảm thấy thế nào?")

    if user_input:

        st.session_state.messages.append({"role":"user","content":user_input})

        emotion=detect_emotion(user_input)

        save_emotion(st.session_state.student_id,emotion)

        reply=chat_ai(user_input)

        st.session_state.messages.append({"role":"assistant","content":reply})

        audio=speak(reply)

        st.session_state.last_audio=audio

        st.rerun()

    if "last_audio" in st.session_state and st.session_state.last_audio:

        st.audio(st.session_state.last_audio)

# ======================
# TEACHER DASHBOARD
# ======================
if role=="teacher":

    st.sidebar.write("👋",st.session_state.username)

    if st.sidebar.button("Đăng xuất"):
        st.session_state.clear()
        st.rerun()

    st.header("📊 Dashboard cảm xúc học sinh")

    with open(EMOTION_FILE,"r") as f:
        data=json.load(f)

    if not data:
        st.info("Chưa có dữ liệu.")
        st.stop()

    emotions=[d["emotion"] for d in data]

    chart_data={
        "happy":emotions.count("happy"),
        "neutral":emotions.count("neutral"),
        "sad":emotions.count("sad"),
        "anxious":emotions.count("anxious"),
        "stress":emotions.count("stress"),
        "crisis":emotions.count("crisis"),
    }

    st.subheader("Tổng quan lớp")

    st.bar_chart(chart_data)

    risk=chart_data["stress"]+chart_data["crisis"]

    st.subheader("Cảnh báo")

    if risk>=3:
        st.error("Nguy cơ cao")
    elif risk>0:
        st.warning("Có dấu hiệu căng thẳng")
    else:
        st.success("Tình trạng ổn định")
