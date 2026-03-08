import streamlit as st
from openai import OpenAI

# API
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="MindNest AI", page_icon="🧠")

st.title("🧠 MindNest AI")

st.info(
    "⚠️ MindNest AI chỉ là công cụ hỗ trợ học tập. "
    "Kết quả có thể chưa hoàn toàn chính xác. "
    "Bạn nên tham khảo thêm ý kiến của thầy cô và ba mẹ trước khi áp dụng."
)

# Lưu lịch sử
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị chat cũ
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# Hàm gọi AI
def ask_ai(question):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Bạn là trợ lý học tập thân thiện cho học sinh."},
            {"role": "user", "content": question}
        ]
    )

    return response.choices[0].message.content


# Nhập text
prompt = st.chat_input("Hỏi MindNest AI...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    answer = ask_ai(prompt)

    with st.chat_message("assistant"):
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})


# =========================
# Nhập bằng giọng nói
# =========================

st.markdown("### 🎤 Nhập bằng giọng nói")

speech_html = """
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

            window.parent.postMessage(
                {type: "streamlit:setComponentValue",
                value: e.results[0][0].transcript},
                "*"
            );

            recognition.stop();
        };

        recognition.onerror = function(e) {
            recognition.stop();
        }
    }
}

</script>
"""

voice_text = st.components.v1.html(speech_html, height=120)

if voice_text:

    st.session_state.messages.append({"role": "user", "content": voice_text})

    with st.chat_message("user"):
        st.write(voice_text)

    answer = ask_ai(voice_text)

    with st.chat_message("assistant"):
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
