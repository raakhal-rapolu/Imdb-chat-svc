import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:5000/imdb-chatbot-svc/api/v1/imdb-chatbot-svc/imdb-chat"  # Update this to match your Flask server URL

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
            margin-bottom: 20px; /* Add space below the header */
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
            margin-bottom: 30px; /* Add space below the hero section */
        }
    </style>
    <div class="header">
        <div class="header-title">🎬 IMDb</div>
        <div class="dropdown-container">
            <label for="model-select">Select Model: </label>
            <select id="model-select" style="padding: 5px 10px; font-size: 16px; border-radius: 5px;">
                <option value="Groq">Groq</option>
                <option value="Gemini">Gemini</option>
            </select>
        </div>
    </div>
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

for sender, message in st.session_state.messages:
    with st.chat_message("user" if sender == "You" else "assistant"):
        st.markdown(f"*{sender}:* {message}")

user_input = st.text_input("You:", key="user_input", placeholder="Ask about movies, actors, or ratings...")

if st.button("Send 🎬"):
    if user_input:

        st.session_state.messages.append(("You", user_input))

        try:

            selected_model = st.session_state.get("model_selection", "Groq")
            response = requests.post(
                BACKEND_URL,
                json={"message": user_input, "model": selected_model}
            ).json()
            bot_response = response.get("response", "Sorry, I couldn't find that information.")
            st.session_state.messages.append(("IMDb Bot", bot_response))
        except Exception as e:
            bot_response = f"⚠️ Error: {e}"
            st.session_state.messages.append(("IMDb Bot", bot_response))
        st.rerun()