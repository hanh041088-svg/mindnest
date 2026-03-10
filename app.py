import streamlit as st
import json
import os
from datetime import datetime
import speech_recognition as sr

st.set_page_config(page_title="MindNest AI", page_icon="🧠")

# =========================
# Tạo thư mục lưu dữ liệu
# =========================
if not os.path.exists("data"):
    os.makedirs("data")

CHAT_FILE = "data/chat_history.json"

if not os.path.exists(CHAT_FILE):
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

# =========================
# Hàm lưu dữ liệu chat
# =========================
def save_chat(user, message, response):

    with open(CHAT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    data.append({
        "user": user,
        "message": message,
        "response": response,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# =========================
# AI trả lời đơn giản
# =========================
def mindnest_ai(prompt):

    return f"""
📚 Gợi ý học tập cho bạn:

{prompt}

MindNest AI chỉ là công cụ hỗ trợ học tập.
Hãy tham khảo thêm ý kiến của thầy cô và ba mẹ trước khi đưa ra quyết định quan trọng.
"""

# =========================
# Nhận giọng nói
# =========================
def voice_to_text():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        st.info("🎤 Đang nghe...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language="vi-VN")
        return text
    except:
        return ""

# =========================
# LOGIN
# =========================

if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:

    st.title("🧠 MindNest AI")

    username = st.text_input("Tên học sinh")

    if st.button("Đăng nhập"):

        if username.strip() != "":
            st.session_state.login = True
            st.session_state.user = username
            st.rerun()

        else:
            st.warning("Vui lòng nhập tên")

    st.stop()

# =========================
# GIAO DIỆN CHÍNH
# =========================

st.title("🧠 MindNest AI")
st.caption("AI hỗ trợ học tập cho học sinh")

st.write(f"👋 Xin chào **{st.session_state.user}**")

# =========================
# CHAT HISTORY
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# =========================
# VOICE INPUT
# =========================

col1, col2 = st.columns([4,1])

with col2:
    if st.button("🎤"):
        voice_text = voice_to_text()

        if voice_text != "":
            st.session_state.voice_input = voice_text
            st.rerun()

# =========================
# TEXT INPUT
# =========================

prompt = st.chat_input("Nhập câu hỏi của bạn...")

if "voice_input" in st.session_state:
    prompt = st.session_state.voice_input
    del st.session_state.voice_input

# =========================
# XỬ LÝ CHAT
# =========================

if prompt:

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    response = mindnest_ai(prompt)

    with st.chat_message("assistant"):
        st.write(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # lưu dữ liệu
    save_chat(st.session_state.user, prompt, response)

# =========================
# FOOTER
# =========================

st.divider()

st.caption(
"MindNest AI chỉ là công cụ hỗ trợ học tập. "
"Hãy tham khảo thêm ý kiến của thầy cô và ba mẹ."
)
