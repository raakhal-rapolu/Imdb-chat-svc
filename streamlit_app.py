import streamlit as st
import requests

# Define backend URLs for different models
BACKEND_URLS = {
    "Ollama llama3.2 + RAG": "http://127.0.0.1:5000/imdb-chatbot-svc/api/v1/imdb-chatbot-svc/imdb-chat",
    "Groq llama-3.3-70b-versatile + Hybrid Search + RAG": "http://127.0.0.1:5000/imdb-chatbot-svc/api/v1/imdb-chatbot-svc/groq-imdb-chat",
    "Gemini gemini-1.5-pro + RAG": "http://127.0.0.1:5000/imdb-chatbot-svc/api/v1/imdb-chatbot-svc/gemini-imdb-chat"
}


st.set_page_config(page_title="IMDb Chatbot", page_icon="🎥", layout="centered")

st.markdown(
    """
    <style>
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #f8f9fa;
            padding: 10px 20px;
            border-radius: 8px;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .header-title {
            font-size: 24px;
            font-weight: bold;
            color: #FF5733;
        }
        .dropdown-container {
            font-size: 16px;
        }
        .hero-section {
            text-align: center;
            margin-bottom: 30px;
        }
    </style>
    <div class="header">
        <div class="header-title">🎬 IMDb</div>
    </div>
    <script>
        function set_model_selection(value) {
            fetch('/_st_set_model', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model: value })
            });
        }
    </script>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-section">
        <h1 style="color: #FF5733;">🎬 IMDb Movie Genie</h1>
        <p style="font-size:18px;">Ask about movies, actors, ratings, and more!</p>
        <hr style="border: 1px solid #FF5733; width: 100%;">
    </div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("<h3 style='text-align: center;'>🤖 Chat with IMDb Bot</h3>", unsafe_allow_html=True)

# Display chat messages
for sender, message in st.session_state.messages:
    with st.chat_message("user" if sender == "You" else "assistant"):
        st.markdown(f"*{sender}:* {message}")

# Model selection dropdown
selected_model = st.selectbox("Select Model:", options=["Groq llama-3.3-70b-versatile + Hybrid Search + RAG", "Gemini gemini-1.5-pro + RAG", "Ollama llama3.2 + RAG"], index=1, key="model_selection")

# User input field
user_input = st.text_input("You:", key="user_input", placeholder="Ask about movies, actors, or ratings...")

if st.button("Send 🎬"):
    if user_input:
        st.session_state.messages.append(("You", user_input))

        # Get the API endpoint based on selected model
        backend_url = BACKEND_URLS.get(selected_model, BACKEND_URLS[selected_model])

        try:
            response = requests.post(
                backend_url,
                json={"message": user_input, "model": selected_model}
            ).json()
            bot_response = response.get("response", "Sorry, I couldn't find that information.")
            st.session_state.messages.append(("IMDb Bot", bot_response))
        except Exception as e:
            bot_response = f"⚠️ Error: {e}"
            st.session_state.messages.append(("IMDb Bot", bot_response))

        st.rerun()
