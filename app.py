import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import base64
import time
import html

# ==========================================================
# PAGE SETTINGS (must be the first Streamlit command)
# ==========================================================
st.set_page_config(
    page_title="AI Customer Support Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================================
# BACKGROUND FUNCTION
# Make sure rm373batch13-087.jpg is in the same folder as app.py
# ==========================================================
def set_background(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as file:
            encoded = base64.b64encode(file.read()).decode()

        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        # Fallback gradient if image is not found
        st.markdown(
            """
            <style>
            .stApp {
                background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                background-attachment: fixed;
            }
            </style>
            """,
            unsafe_allow_html=True
        )


# ==========================================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================================
# ==========================================================
# LOAD API KEY (Works Locally and on Streamlit Cloud)
# ==========================================================
load_dotenv()

api_key = None

# 1. Try to read from Streamlit Secrets (Cloud Deployment)
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
except Exception:
    # No secrets configured yet on Streamlit Cloud
    pass

# 2. If not found, try local .env file
if not api_key:
    api_key = os.getenv("GOOGLE_API_KEY")

# 3. If still not found, show error and stop
if not api_key:
    st.error(
        "GOOGLE_API_KEY not found. "
        "Please add it to Streamlit Secrets or your local .env file."
    )
    st.stop()

# Configure Gemini API
genai.configure(api_key=api_key)

# Load Gemini Model
model = genai.GenerativeModel("models/gemini-2.5-flash")

# Configure Gemini API
genai.configure(api_key=api_key)

# Load Gemini Model
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ==========================================================
# APPLY BACKGROUND
# ==========================================================
set_background("rm373batch13-087.jpg")

# ==========================================================
# CUSTOM CSS
# ==========================================================
st.markdown(
    """
    <style>

    /* Hide sidebar completely */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Hide sidebar toggle button */
    [data-testid="collapsedControl"] {
        display: none;
    }

    /* Transparent header */
    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
    }

    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #f0f0f0;
        font-size: 20px;
        margin-bottom: 30px;
    }

    /* Welcome info box */
    .welcome-box {
        background: rgba(255, 255, 255, 0.15);
        padding: 15px;
        border-radius: 15px;
        color: white;
        margin-bottom: 20px;
    }

    /* Main glass card */
    .chat-container {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(12px);
        padding: 30px;
        border-radius: 25px;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.35);
        animation: fadeIn 0.8s ease-in-out;
    }

    /* Text input */
    .stTextInput input {
        border-radius: 15px !important;
        border: 2px solid #4fc3f7 !important;
        padding: 12px !important;
        background-color: white !important;
        color: black !important;
    }

    /* Send button */
    .stButton > button {
        width: 100%;
        border-radius: 15px;
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white;
        border: none;
        font-size: 20px;
        padding: 12px;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0px 0px 20px rgba(0, 198, 255, 0.7);
    }

    /* User message box */
    .user-box {
        background: rgba(0, 114, 255, 0.15);
        border-left: 6px solid #00c6ff;
        padding: 15px;
        border-radius: 12px;
        margin-top: 15px;
        color: white;
    }

    /* AI response box */
    .answer-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        color: black;
        margin-top: 15px;
        border-left: 6px solid #0072ff;
        line-height: 1.8;
    }

    /* Spinner */
    div[data-testid="stSpinner"] p {
        color: #FFD700 !important;
        font-size: 20px !important;
        font-weight: bold !important;
    }

    div[data-testid="stSpinner"] svg {
        stroke: #FFD700 !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #e0e0e0;
        margin-top: 40px;
        font-size: 14px;
    }

    /* Animation */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(15px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# SESSION STATE
# ==========================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

# ==========================================================
# CLEAR CHAT BUTTON (TOP RIGHT)
# ==========================================================
col1, col2, col3 = st.columns([8, 1, 1])

with col3:
    if st.button("🗑️"):
        st.session_state.chat_history = []
        st.session_state.last_answer = ""
        st.rerun()

# ==========================================================
# TITLE
# ==========================================================
st.markdown(
    """
    <h1 style="
        text-align:center;
        color:white;
        font-size:55px;
        font-weight:bold;
        margin-top:20px;
    ">
    🤖 AI Customer Support Chatbot
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<p class="subtitle">Ask anything about internships, AI/ML, technology and services</p>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="welcome-box">
        👋 Welcome! Ask me questions about AI, Machine Learning, internships,
        technology, and career guidance.
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# MAIN CHAT CARD
# ==========================================================
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Input
question = st.text_input(
    "Ask something",
    placeholder="Type your question here..."
)
# Send Button
if st.button("Send"):
    if question.strip():
        with st.spinner("Thinking..."):
            try:
                # Prompt for Acadeno-specific chatbot
                prompt = f"""
You are the official AI Customer Support Assistant for Acadeno Technologies Pvt. Ltd.

Company Name:
Acadeno Technologies Pvt. Ltd.

Company Website:
https://www.acadeno.com

Company Overview:
Acadeno Technologies Pvt. Ltd. is an AI engineering and enterprise software development company based in Government Cyberpark, Kozhikode, Kerala, India. The company specializes in integrating Artificial Intelligence into existing software systems and building custom AI-powered business solutions.

Services Offered by Acadeno Technologies:
1. AI Integration into Existing Software
2. Custom AI Solutions and Machine Learning Models
3. AI Agents and Intelligent Automation
4. RAG (Retrieval-Augmented Generation) Knowledge Systems
5. Web Application Development
6. Mobile Application Development
7. API and System Integration
8. Cloud and DevOps Services
9. Cybersecurity Solutions
10. Data Analytics and Business Intelligence
11. IoT Solutions
12. Embedded Systems
13. Robotics and Automation
14. Smart City Solutions
15. Digital Marketing
16. AI Consulting and Training

Internships and Careers:
Acadeno Technologies offers internship and career opportunities in:
- Artificial Intelligence and Machine Learning
- Web Development
- Mobile App Development
- Cloud Computing
- Cybersecurity
- Data Analytics

Contact Information:
- Website: https://www.acadeno.com
- Email: info@acadeno.com
- Office Phone: +91 4954-600-504
- Sales Phone: +91 9895-600-504
- Location: Government Cyberpark, Kozhikode, Kerala, India

Instructions:
1. Answer ONLY questions related to Acadeno Technologies Pvt. Ltd.
2. Allowed topics:
   - Company overview
   - Services offered
   - AI solutions
   - Internship opportunities
   - Careers
   - Contact information
   - Office location
   - Technologies used
3. If the user asks anything unrelated, respond exactly:
   "I am the official AI Customer Support Assistant for Acadeno Technologies Pvt. Ltd. and can answer only questions related to the company, its services, internships, and contact information."
4. Always respond professionally, clearly, and concisely.
5. Use bullet points when appropriate.

User Question:
{question}
"""

                # Generate response
                response = model.generate_content(prompt)
                answer = response.text
                st.session_state.last_answer = answer

                # Save to chat history
                st.session_state.chat_history.append(("You", question))
                st.session_state.chat_history.append(("AI", answer))

                # Typing animation
                placeholder = st.empty()
                typed_text = ""

                for word in answer.split():
                    typed_text += html.escape(word) + " "

                    placeholder.markdown(
                        f"""
                        <div class="answer-box">
                            <h4>Acadeno AI Response</h4>
                            <p>{typed_text}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    time.sleep(0.02)

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.warning("Please enter a question.")