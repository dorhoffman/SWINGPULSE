from __future__ import annotations

from pathlib import Path

import streamlit as st

from agent import ask_agent


# ---------------------------------------------------------
# APP CONFIGURATION
# ---------------------------------------------------------

APP_ROOT = Path(__file__).resolve().parent
LOGO_PATH = APP_ROOT / "assets" / "logo.png"

st.set_page_config(
    page_title="SWINGPULSE AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# DESIGN
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    /* Main page */
    .stApp {
        background:
            linear-gradient(
                180deg,
                #F5FBFC 0%,
                #FFFFFF 45%,
                #F7FAFC 100%
            );
    }

    .block-container {
        max-width: 1050px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    /* Hide Streamlit default elements */
    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent;
    }

    /* Header */
    .swingpulse-title {
        font-size: 2.45rem;
        font-weight: 800;
        color: #17324D;
        margin: 0;
        line-height: 1.1;
    }

    .swingpulse-subtitle {
        font-size: 1rem;
        color: #5D7488;
        margin-top: 0.35rem;
        margin-bottom: 1.4rem;
    }

    .agent-badge {
        display: inline-block;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background: #DFF7F4;
        color: #087D78;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        border: 1px solid #DDE9EE;
        border-radius: 18px;
        padding: 0.6rem 0.8rem;
        margin-bottom: 0.8rem;
        background: rgba(255, 255, 255, 0.94);
        box-shadow: 0 5px 18px rgba(44, 92, 112, 0.06);
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        border-radius: 18px;
    }

    [data-testid="stChatInput"] textarea {
        font-size: 1rem;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        border: 1px solid #B9DEDD;
        background: white;
        color: #24546A;
        font-weight: 600;
        transition: 0.2s;
    }

    .stButton > button:hover {
        border-color: #21A7A0;
        color: #087D78;
        background: #EEFBFA;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #EDF9FA 0%,
                #F8FCFD 100%
            );
        border-right: 1px solid #D8EAED;
    }

    /* Information card */
    .info-card {
        background: white;
        border: 1px solid #DCEBED;
        border-radius: 15px;
        padding: 1rem;
        color: #496474;
        font-size: 0.88rem;
        line-height: 1.55;
        margin-top: 1rem;
    }

    .disclaimer {
        color: #718796;
        font-size: 0.78rem;
        text-align: center;
        padding-top: 1.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "שלום, אני **SWINGPULSE AI**. 📈\n\n"
                "אפשר לבקש ממני לנתח מניה, להשוות בין מניות, "
                "לסרוק RSI או להסביר אינדיקטורים טכניים.\n\n"
                "לדוגמה: **תנתח לי את AAPL**"
            ),
        }
    ]

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    if LOGO_PATH.exists():
        st.image(
            str(LOGO_PATH),
            use_container_width=True,
        )
    else:
        st.markdown("## 📈 SWINGPULSE")

    st.markdown("### שאלות לדוגמה")

    example_prompts = [
        (
            "נתח את AAPL",
            "תנתח לי את AAPL ותסביר את התוצאה.",
        ),
        (
            "השווה NVDA ו־AMD",
            "השווה בין NVDA ל-AMD ותגיד איזו נראית חזקה יותר.",
        ),
        (
            "מניות סביב RSI 30",
            "מצא מניות עם RSI בין 26 ל-35.",
        ),
        (
            "הסתברות מעל 45%",
            "מצא מניות עם הסתברות מודל מעל 45 אחוז.",
        ),
        (
            "הסבר MACD",
            "מה זה MACD ואיך מפרשים אותו?",
        ),
    ]

    for index, (button_label, prompt_text) in enumerate(
        example_prompts
    ):
        if st.button(
            button_label,
            key=f"example_{index}",
        ):
            st.session_state.pending_prompt = prompt_text

    st.divider()

    if st.button(
        "🗑️ נקה את השיחה",
        key="clear_chat",
    ):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "השיחה נוקתה. מה תרצה לבדוק?"
                ),
            }
        ]
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown(
        """
        <div class="info-card">
            <b>איך המערכת עובדת?</b><br><br>
            הסוכן מבין את השאלה, בוחר כלי מתאים,
            מושך נתוני שוק, מחשב אינדיקטורים ומפעיל
            את מודל ה־Random Forest של SWINGPULSE.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

header_left, header_right = st.columns(
    [1, 4],
    vertical_alignment="center",
)

with header_left:
    if LOGO_PATH.exists():
        st.image(
            str(LOGO_PATH),
            width=150,
        )

with header_right:
    st.markdown(
        '<div class="agent-badge">LIVE AI MARKET AGENT</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="swingpulse-title">SWINGPULSE AI</h1>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="swingpulse-subtitle">
            שאל שאלות על מניות בשפה חופשית וקבל ניתוח
            המבוסס על נתוני שוק, אינדיקטורים טכניים ומודל ML.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# CHAT HISTORY
# ---------------------------------------------------------

for message in st.session_state.messages:

    avatar = (
        "🤖"
        if message["role"] == "assistant"
        else "👤"
    )

    with st.chat_message(
        message["role"],
        avatar=avatar,
    ):
        st.markdown(message["content"])


# ---------------------------------------------------------
# CHAT INPUT
# ---------------------------------------------------------

typed_prompt = st.chat_input(
    "לדוגמה: מצא מניות עם RSI בין 26 ל־35"
)

prompt = typed_prompt

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None


# ---------------------------------------------------------
# AGENT RESPONSE
# ---------------------------------------------------------

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message(
        "user",
        avatar="👤",
    ):
        st.markdown(prompt)

    previous_messages = (
        st.session_state.messages[:-1]
    )

    with st.chat_message(
        "assistant",
        avatar="🤖",
    ):

        with st.spinner(
            "SWINGPULSE מנתח את הבקשה..."
        ):

            try:
                answer = ask_agent(
                    user_message=prompt,
                    conversation_history=previous_messages,
                )

            except Exception as error:
                answer = (
                    "לא הצלחתי להשלים את הבקשה כרגע.\n\n"
                    f"שגיאה: `{error}`"
                )

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="disclaimer">
        SWINGPULSE הוא פרויקט לימודי המבוסס על נתוני עבר
        ומודל ניסיוני. המידע אינו ייעוץ פיננסי ואינו מבטיח תשואה.
    </div>
    """,
    unsafe_allow_html=True,
)
