import streamlit as st
import os
import json
import random
import tempfile
from datetime import datetime
from openai import OpenAI

# ======================
# PAGE CONFIG (PHẢI Ở TRÊN CÙNG)
# ======================
st.set_page_config(
    page_title="MindNest 🌥️",
    page_icon="☁️",
    layout="centered"
)

# ======================
# LOAD API KEY (AN TOÀN)
# ======================
# Lấy API key từ Streamlit Secrets
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.error("API key chưa được cấu hình trong Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# ======================
# LOAD USERS
# ======================
if not os.path.exists("users.json"):
    st.error("Không tìm thấy file users.json")
    st.stop()

with open("users.json", "r", encoding="utf-8") as f:
    USERS = json.load(f)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ======================
# DATA STORAGE
# ======================
DATA_FILE = "emotion_data.json"

def load_emotion_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_emotion_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
# ======================
# LOGIN PAGE
# ======================
if not st.session_state.logged_in:

    st.title("☁️ Đăng nhập MindNest")

    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")

    if st.button("Đăng nhập"):

        if username in USERS and USERS[username]["password"] == password:

            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]

            st.success("Đăng nhập thành công!")
            st.rerun()
        else:
            st.error("Sai tài khoản hoặc mật khẩu")

    st.stop()

# ======================
# BEAUTIFUL UI
# ======================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: "Segoe UI";
    font-size:13px;
}

.stApp {
background: linear-gradient(135deg,#ffd6ec,#e6ccff,#d6e4ff,#ffe6f7);
background-size:400% 400%;
animation: gradientBG 12s ease infinite;
}

@keyframes gradientBG {
0%{background-position:0% 50%;}
50%{background-position:100% 50%;}
100%{background-position:0% 50%;}
}

.title-box{
text-align:center;
padding:18px;
border-radius:22px;
background:rgba(255,255,255,0.85);
box-shadow:0 8px 25px rgba(0,0,0,0.12);
margin-bottom:15px;
}

.chat-user{
background:linear-gradient(135deg,#a8edea,#fed6e3);
padding:12px;
border-radius:18px;
margin:8px 0;
}

.chat-bot{
background:white;
padding:12px;
border-radius:18px;
margin:8px 0;
box-shadow:0 4px 12px rgba(0,0,0,0.08);
}

.warning-box{
background:linear-gradient(135deg,#fff0c9,#ffe6f2);
padding:14px;
border-radius:16px;
margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# ======================
# HEADER
# ======================
st.markdown("""
<div class="title-box">
<h2>☁️ MindNest – Người sẻ chia cùng bạn!</h2>
<p><b>TRƯỜNG TIỂU HỌC, THCS VÀ THPT HỒNG ĐỨC</b></p>
<p>Hãy chia sẻ với MindNest nhé 💙</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="warning-box">
⚠️ <b>Lưu ý:</b> MindNest chỉ là AI hỗ trợ.
Nếu áp lực kéo dài, hãy tìm sự hỗ trợ từ thầy cô hoặc chuyên gia nhé!
</div>
""", unsafe_allow_html=True)

# ======================
# SESSION STATE
# ======================
# Lưu dữ liệu vào file chung
data = load_emotion_data()

data.append({
    "student": st.session_state.username,
    "time": str(datetime.now()),
    "emotion": emotion
})

save_emotion_data(data)
role = st.session_state.role

# ======================
# EMOTION DETECTION
# ======================
def detect_emotion(text):
    prompt = f"""
Phân loại cảm xúc học sinh.
Chỉ trả về 1 từ:
happy | sad | anxious | stress | crisis | neutral

Câu: {text}
"""
    try:
        res = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )
        return res.output_text.strip().lower()
    except:
        return "neutral"

# ======================
# CHAT AI
# ======================
def ask_may_nho(user_text):

    system_prompt = """
Bạn là MindNest — người bạn đồng hành tâm lý học sinh.
Giọng nhẹ nhàng, tích cực.
Không chẩn đoán bệnh.
Khuyến khích tìm người lớn khi cần.
"""

    history = ""
    for m in st.session_state.messages:
        history += f"{m['role']}: {m['content']}\n"

    prompt = system_prompt + "\n" + history + f"user: {user_text}"

    try:
        res = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )
        return res.output_text
    except:
        return "Xin lỗi, hiện tại hệ thống đang bận."

# ======================
# TEXT TO SPEECH (AN TOÀN)
# ======================
def speak_text(text):
    try:
        speech_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

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
# STUDENT MODE
# ======================
if role == "student":

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-user'>🙂 {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bot'>☁️ {msg['content']}</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Hãy chia sẻ với MindNest ...")

    if user_input:

        st.session_state.messages.append({"role":"user","content":user_input})

        emotion = detect_emotion(user_input)

        st.session_state.emotion_log.append({
            "student": st.session_state.student_id,
            "time": datetime.now(),
            "emotion": emotion
        })

        reply = ask_may_nho(user_input)

        st.session_state.messages.append({"role":"assistant","content":reply})

        audio_path = speak_text(reply)
        st.session_state.last_audio = audio_path

        st.rerun()

    if "last_audio" in st.session_state and st.session_state.last_audio:
        st.audio(st.session_state.last_audio)

# ======================
# TEACHER MODE
# ======================
if role == "teacher":

    st.sidebar.markdown(f"👋 Xin chào: {st.session_state.username}")

    if st.sidebar.button("Đăng xuất"):
        st.session_state.clear()
        st.rerun()

    st.header("📊 Dashboard sức khỏe tinh thần học sinh")

    data = load_emotion_data()

if not data:
    st.info("Chưa có dữ liệu từ học sinh.")
    st.stop()

emotions = [e["emotion"] for e in data]

    data = {
        "happy": emotions.count("happy"),
        "neutral": emotions.count("neutral"),
        "sad": emotions.count("sad"),
        "anxious": emotions.count("anxious"),
        "stress": emotions.count("stress"),
        "crisis": emotions.count("crisis"),
    }

    st.subheader("🌈 Tổng quan cảm xúc lớp")
for item in data[-20:]:
    st.write(
        f"👤 {item['student']} | {item['emotion']} | {item['time']}"
    )
    st.bar_chart(data)

    risk = data["stress"] + data["crisis"]

    st.subheader("🚨 Cảnh báo sớm")

    if risk >= 3:
        st.error("Có dấu hiệu căng thẳng cao. Nên trò chuyện riêng với học sinh.")
    elif risk > 0:
        st.warning("Xuất hiện dấu hiệu lo âu nhẹ.")
    else:

        st.success("Tình trạng lớp ổn định 💙")

