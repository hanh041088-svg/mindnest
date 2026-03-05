import streamlit as st
import os
import json
import random
import tempfile
import pandas as pd
import plotly.express as px
from datetime import datetime
from openai import OpenAI

# ======================
# PAGE CONFIG
# ======================

st.set_page_config(
    page_title="MindNest AI",
    page_icon="☁️",
    layout="wide"
)

# ======================
# API KEY
# ======================

api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("Chưa cấu hình OPENAI_API_KEY trong Streamlit Secrets")
    st.stop()

client = OpenAI(api_key=api_key)

# ======================
# FILE PATH
# ======================

USER_FILE = "users.json"
EMOTION_FILE = "emotion_data.json"

if not os.path.exists(EMOTION_FILE):
    with open(EMOTION_FILE,"w") as f:
        json.dump([],f)

# ======================
# LOAD USERS
# ======================

with open(USER_FILE,"r",encoding="utf-8") as f:
    USERS = json.load(f)

# ======================
# SESSION
# ======================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ======================
# LOGIN PAGE
# ======================

if not st.session_state.logged_in:

    st.title("☁️ MindNest AI")

    st.subheader("Đăng nhập hệ thống")

    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu",type="password")

    if st.button("Đăng nhập"):

        if username in USERS and USERS[username]["password"] == password:

            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]

            st.rerun()

        else:

            st.error("Sai tài khoản hoặc mật khẩu")

    st.stop()

# ======================
# STYLE
# ======================

st.markdown("""
<style>

.stApp{
background:linear-gradient(120deg,#ffd6ec,#e6ccff,#d6e4ff,#ffe6f7);
}

.card{
background:white;
padding:20px;
border-radius:15px;
box-shadow:0 5px 20px rgba(0,0,0,0.1);
margin-bottom:20px;
}

.chat-user{
background:#d6f5ff;
padding:12px;
border-radius:12px;
margin:6px;
}

.chat-bot{
background:white;
padding:12px;
border-radius:12px;
margin:6px;
}

</style>
""",unsafe_allow_html=True)

# ======================
# HEADER
# ======================

st.markdown("""
<div class="card">
<h2>☁️ MindNest AI</h2>
AI hỗ trợ sức khỏe tinh thần học sinh
</div>
""",unsafe_allow_html=True)

role = st.session_state.role

# ======================
# EMOTION DETECTION
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
# AI CHAT
# ======================

def ask_ai(text):

    prompt=f"""
Bạn là AI hỗ trợ tâm lý học sinh.

Giọng nói nhẹ nhàng, tích cực.
Không phán xét.
Khuyến khích tìm sự giúp đỡ khi cần.

Tin nhắn học sinh:
{text}
"""

    try:

        res=client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )

        return res.output_text

    except:

        return "Hiện AI đang bận."

# ======================
# TTS
# ======================

def speak_text(text):

    try:

        speech_file=tempfile.NamedTemporaryFile(delete=False,suffix=".mp3")

        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="nova",
            input=text
        ) as response:

            response.stream_to_file(speech_file.name)

        return speech_file.name

    except:

        return None

# ======================
# RISK SCORE
# ======================

def calculate_risk(df):

    score=0

    for e in df["emotion"]:

        if e=="sad":
            score+=1

        elif e=="anxious":
            score+=2

        elif e=="stress":
            score+=3

        elif e=="crisis":
            score+=5

    return score

# ======================
# STUDENT MODE
# ======================

if role=="student":

    st.subheader("💬 Chat với MindNest")

    if "messages" not in st.session_state:
        st.session_state.messages=[]

    for msg in st.session_state.messages:

        if msg["role"]=="user":

            st.markdown(f"<div class='chat-user'>{msg['content']}</div>",unsafe_allow_html=True)

        else:

            st.markdown(f"<div class='chat-bot'>{msg['content']}</div>",unsafe_allow_html=True)

    user_input=st.chat_input("Hãy chia sẻ cảm xúc của bạn...")

    if user_input:

        st.session_state.messages.append({"role":"user","content":user_input})

        emotion=detect_emotion(user_input)

        reply=ask_ai(user_input)

        st.session_state.messages.append({"role":"assistant","content":reply})

        with open(EMOTION_FILE,"r") as f:
            logs=json.load(f)

        logs.append({

            "student":st.session_state.username,
            "time":str(datetime.now()),
            "emotion":emotion

        })

        with open(EMOTION_FILE,"w") as f:
            json.dump(logs,f,indent=2)

        audio=speak_text(reply)

        st.session_state.last_audio=audio

        st.rerun()

    if "last_audio" in st.session_state:

        st.audio(st.session_state.last_audio)

# ======================
# TEACHER DASHBOARD
# ======================

if role=="teacher":

    st.title("📊 Dashboard sức khỏe tinh thần")

    with open(EMOTION_FILE,"r") as f:
        data=json.load(f)

    if not data:

        st.info("Chưa có dữ liệu học sinh.")
        st.stop()

    df=pd.DataFrame(data)

    df["time"]=pd.to_datetime(df["time"])

    # ======================
    # CLASS OVERVIEW
    # ======================

    col1,col2,col3,col4=st.columns(4)

    col1.metric("🙂 Happy",(df["emotion"]=="happy").sum())
    col2.metric("😐 Neutral",(df["emotion"]=="neutral").sum())
    col3.metric("😟 Stress",(df["emotion"]=="stress").sum())
    col4.metric("🚨 Crisis",(df["emotion"]=="crisis").sum())

    st.divider()

    st.subheader("Cảm xúc toàn lớp")

    st.bar_chart(df["emotion"].value_counts())

    # ======================
    # STUDENT SELECT
    # ======================

    st.subheader("👩‍🎓 Theo dõi từng học sinh")

    students=df["student"].unique()

    selected=st.selectbox("Chọn học sinh",students)

    student_df=df[df["student"]==selected]

    st.dataframe(student_df)

    # ======================
    # TIMELINE
    # ======================

    st.subheader("📈 Timeline cảm xúc")

    fig=px.line(
        student_df,
        x="time",
        y="emotion",
        markers=True
    )

    st.plotly_chart(fig,use_container_width=True)

    # ======================
    # RISK SCORE
    # ======================

    risk_score=calculate_risk(student_df)

    st.subheader("🧠 AI Risk Score")

    st.metric("Risk Score",risk_score)

    if risk_score>=10:

        st.error("🔴 Nguy cơ cao")

    elif risk_score>=5:

        st.warning("🟡 Cần theo dõi")

    else:

        st.success("🟢 Ổn định")

    # ======================
    # TOP RISK
    # ======================

    st.subheader("🚨 Học sinh cần chú ý")

    risk_students=[]

    for s in df["student"].unique():

        s_df=df[df["student"]==s]

        score=calculate_risk(s_df)

        risk_students.append({
            "student":s,
            "risk_score":score
        })

    risk_df=pd.DataFrame(risk_students)

    risk_df=risk_df.sort_values("risk_score",ascending=False)

    st.dataframe(risk_df)

# ======================
# LOGOUT
# ======================

if st.sidebar.button("Đăng xuất"):

    st.session_state.clear()

    st.rerun()
