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
    page_title="MindNest 🌥️ - HongDucSchool",
    page_icon="☁️",
    layout="centered"
)

# ======================
# SESSION STATE
# ======================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "emotion_log" not in st.session_state:
    st.session_state.emotion_log = []

if "student_id" not in st.session_state:
    st.session_state.student_id = f"HS_{random.randint(100,999)}"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "last_audio" not in st.session_state:
    st.session_state.last_audio = None

# ======================
# LOAD API KEY
# ======================

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ Không tìm thấy OPENAI_API_KEY.")
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

# ======================
# LOGIN
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

            st.rerun()

        else:
            st.error("Sai tài khoản hoặc mật khẩu")

    st.stop()

# ======================
# HEADER
# ======================

st.title("☁️ MindNest")
st.caption("AI hỗ trợ sức khỏe tinh thần học sinh")


# ======================
# AI FUNCTIONS
# ======================

def detect_emotion(text):

    prompt = f"""
Phân loại cảm xúc học sinh.

Chỉ trả về:

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
# AI CHAT
# ======================

def ask_ai(text):

    messages = [
        {
            "role": "system",
            "content":
            "Bạn là AI hỗ trợ tâm lý học sinh. "
            "Luôn trả lời bằng tiếng Việt, nhẹ nhàng, tích cực."
        }
    ]

    for m in st.session_state.messages:

        messages.append({
            "role": m["role"],
            "content": m["content"]
        })

    messages.append({
        "role": "user",
        "content": text
    })

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return res.choices[0].message.content

# ======================
# TEXT TO SPEECH
# ======================

def speak(text):

    speech_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

    with client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="nova",
        input=text
    ) as response:

        response.stream_to_file(speech_file.name)

    return speech_file.name

# ======================
# GREETING
# ======================

if len(st.session_state.messages) == 0:

    st.session_state.messages.append({
        "role":"assistant",
        "content":"Chào bạn! Mình là MindNest ☁️. Bạn muốn chia sẻ điều gì hôm nay?"
    })

# ======================
# SHOW CHAT
# ======================

for msg in st.session_state.messages:

    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])

    else:
        st.chat_message("assistant").write(msg["content"])

# ======================
# VOICE INPUT
# ======================

st.markdown("### 🎤 Nói chuyện")

voice_html = """
<button onclick="startDictation()">🎤 Bắt đầu nói</button>

<p id="speech"></p>

<script>
function startDictation() {

if (window.hasOwnProperty('webkitSpeechRecognition')) {

var recognition = new webkitSpeechRecognition();

recognition.continuous = false;
recognition.interimResults = false;

recognition.lang = "vi-VN";

recognition.start();

recognition.onresult = function(e) {

document.getElementById('speech').innerHTML
= e.results[0][0].transcript;

}

recognition.onerror=function(e){
recognition.stop();
}

}
}
</script>
"""

st.components.v1.html(voice_html, height=120)

# ======================
# TEXT INPUT
# ======================

user_input = st.chat_input("Chia sẻ cảm xúc của bạn...")

if user_input:

    st.session_state.messages.append({
        "role":"user",
        "content":user_input
    })

    emotion = detect_emotion(user_input)

    st.session_state.emotion_log.append({
        "student": st.session_state.student_id,
        "time": datetime.now(),
        "emotion": emotion
    })

    reply = ask_ai(user_input)

    st.session_state.messages.append({
        "role":"assistant",
        "content":reply
    })

    audio = speak(reply)

    st.session_state.last_audio = audio

    st.rerun()

if st.session_state.last_audio:
    st.audio(st.session_state.last_audio)
st.warning(
"⚠️ MindNest AI chỉ là công cụ hỗ trợ. "
"Hãy tham khảo thêm ý kiến của thầy cô hoặc ba mẹ."
)
