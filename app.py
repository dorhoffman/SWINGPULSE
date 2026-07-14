from __future__ import annotations

from pathlib import Path

import streamlit as st

from agent import ask_agent


# =========================================================
# CONFIGURATION
# =========================================================

APP_ROOT = Path(__file__).resolve().parent
LOGO_PATH = APP_ROOT / "assets" / "logo.png"

st.set_page_config(
    page_title="SWINGPULSE AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# DESIGN SYSTEM
# =========================================================

st.markdown(
    """
    <style>
    :root {
        --navy: #173A4D;
        --blue: #2797BB;
        --teal: #26ADA4;
        --green: #43BC7B;
        --surface: #FFFFFF;
        --background: #F5FAFB;
        --border: #DCEAED;
        --muted: #6A818D;
    }

    * {
        box-sizing: border-box;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 85% 0%,
                rgba(38, 173, 164, 0.12),
                transparent 28%
            ),
            radial-gradient(
                circle at 15% 20%,
                rgba(39, 151, 187, 0.06),
                transparent 22%
            ),
            linear-gradient(
                180deg,
                #F7FCFD 0%,
                #FFFFFF 42%,
                #F6FAFB 100%
            );
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.5rem;
        padding-bottom: 7rem;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    header {
        background: transparent;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #ECF9FA 0%,
                #F8FCFD 60%,
                #FFFFFF 100%
            );
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebarContent"] {
        padding-top: 1rem;
    }

    /* Hero */
    .hero {
        position: relative;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid var(--border);
        border-radius: 26px;
        padding: 1.7rem 1.9rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 18px 50px rgba(31, 86, 103, 0.08);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 190px;
        height: 190px;
        right: -60px;
        top: -80px;
        border-radius: 50%;
        background: linear-gradient(
            135deg,
            rgba(39, 151, 187, 0.10),
            rgba(67, 188, 123, 0.10)
        );
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.38rem 0.78rem;
        border-radius: 999px;
        background: #E1F8F3;
        color: #117E72;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        margin-bottom: 0.8rem;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 0 4px rgba(67, 188, 123, 0.13);
    }

    .hero-title {
        color: var(--navy);
        font-size: 2.55rem;
        line-height: 1.05;
        font-weight: 850;
        letter-spacing: -0.035em;
        margin: 0;
    }

    .hero-text {
        max-width: 760px;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.65;
        margin-top: 0.65rem;
        margin-bottom: 0;
    }

    /* Capability cards */
    .capabilities {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
        margin: 1rem 0 1.35rem;
    }

    .capability-card {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: 0 8px 25px rgba(31, 86, 103, 0.045);
    }

    .capability-icon {
        font-size: 1.4rem;
        margin-bottom: 0.45rem;
    }

    .capability-title {
        color: var(--navy);
        font-size: 0.95rem;
        font-weight: 780;
        margin-bottom: 0.3rem;
    }

    .capability-text {
        color: var(--muted);
        font-size: 0.8rem;
        line-height: 1.48;
    }

    /* Chat */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.96);
        border: 1px solid var(--border);
        border-radius: 21px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 8px 28px rgba(31, 86, 103, 0.055);
    }

    [data-testid="stChatMessageContent"] {
        color: #294B5D;
        font-size: 0.98rem;
        line-height: 1.75;

        /*
        Automatically supports English LTR and Hebrew RTL
        according to each paragraph's text.
        */
        unicode-bidi: plaintext;
        text-align: start;
    }

    [data-testid="stChatInput"] {
        border-radius: 18px;
        box-shadow: 0 12px 34px rgba(31, 86, 103, 0.14);
    }

    [data-testid="stChatInput"] textarea {
        font-size: 1rem;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        min-height: 2.75rem;
        border-radius: 13px;
        border: 1px solid #C6E1E5;
        background: rgba(255, 255, 255, 0.92);
        color: #285368;
        font-weight: 680;
        text-align: left;
        transition:
            transform 0.16s ease,
            border-color 0.16s ease,
            background 0.16s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: var(--teal);
        color: #087D78;
        background: #EAF9F7;
    }

    /* Sidebar */
    .sidebar-heading {
        color: var(--navy);
        font-size: 0.95rem;
        font-weight: 780;
        margin: 1rem 0 0.7rem;
    }

    .sidebar-card {
        background: rgba(255, 255, 255, 0.90);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1rem;
        color: #57717E;
        font-size: 0.84rem;
        line-height: 1.6;
        margin-top: 1rem;
    }

    .sidebar-card b {
        color: var(--navy);
    }

    .footer-note {
        max-width: 900px;
        margin: 2rem auto 0;
        border-top: 1px solid #DFEAED;
        padding-top: 1rem;
        color: #82959E;
        font-size: 0.76rem;
        line-height: 1.55;
        text-align: center;
    }

    @media (max-width: 850px) {
        .capabilities {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 1.9rem;
        }

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SESSION STATE
# =========================================================

WELCOME_MESSAGE = """
Hello! I’m **SWINGPULSE AI**, your stock-market research agent. 📈

I can analyze stocks, compare companies, scan technical conditions,
and explain indicators using market data and the SWINGPULSE machine-learning model.

You can ask questions in **English or Hebrew**.

Try: **Analyze AAPL**
"""

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE,
        }
    ]

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    if LOGO_PATH.exists():
        st.image(
            str(LOGO_PATH),
            use_container_width=True,
        )
    else:
        st.markdown("## 📈 SWINGPULSE")

    st.markdown(
        '<div class="sidebar-heading">Quick actions</div>',
        unsafe_allow_html=True,
    )

    examples = [
        (
            "Analyze AAPL",
            "Analyze AAPL and explain the model result.",
        ),
        (
            "Compare NVDA and AMD",
            "Compare NVDA and AMD and explain which currently appears stronger.",
        ),
        (
            "Find stocks near RSI 30",
            "Find stocks with an RSI between 26 and 35.",
        ),
        (
            "Probability above 45%",
            "Find stocks with a model probability above 45 percent.",
        ),
        (
            "Explain MACD",
            "Explain MACD and how it is commonly interpreted.",
        ),
    ]

    for index, (label, prompt_text) in enumerate(examples):
        if st.button(
            label,
            key=f"quick_action_{index}",
        ):
            st.session_state.pending_prompt = prompt_text

    st.divider()

    if st.button(
        "🗑️ Clear conversation",
        key="clear_chat",
    ):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": WELCOME_MESSAGE,
            }
        ]
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown(
        """
        <div class="sidebar-card">
            <b>How it works</b><br><br>
            The agent understands your request, selects an analytical
            tool, retrieves market data, calculates indicators, and
            applies the SWINGPULSE Random Forest model.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-card">
            <b>Language support</b><br><br>
            The interface is in English. You can ask questions in
            English or Hebrew, and the agent responds in the language
            used in your question.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <section class="hero">
        <div class="status-badge">
            <span class="status-dot"></span>
            LIVE AI MARKET AGENT
        </div>

        <h1 class="hero-title">
            SWINGPULSE AI
        </h1>

        <p class="hero-text">
            Ask natural-language questions about stocks and receive
            analysis powered by market data, technical indicators,
            and a trained machine-learning model.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CAPABILITIES
# =========================================================

if len(st.session_state.messages) == 1:
    st.markdown(
        """
        <div class="capabilities">

            <div class="capability-card">
                <div class="capability-icon">📊</div>
                <div class="capability-title">Stock analysis</div>
                <div class="capability-text">
                    Review probability, RSI, MACD, volatility,
                    trend and other technical features.
                </div>
            </div>

            <div class="capability-card">
                <div class="capability-icon">🔎</div>
                <div class="capability-title">Market scanning</div>
                <div class="capability-text">
                    Search selected stocks using RSI ranges
                    and model-probability conditions.
                </div>
            </div>

            <div class="capability-card">
                <div class="capability-icon">⚖️</div>
                <div class="capability-title">Stock comparison</div>
                <div class="capability-text">
                    Compare multiple companies using one
                    consistent analytical framework.
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# CHAT HISTORY
# =========================================================

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


# =========================================================
# USER INPUT
# =========================================================

typed_prompt = st.chat_input(
    "Ask about a stock, indicator, comparison or market scan..."
)

prompt = typed_prompt

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None


# =========================================================
# AGENT RESPONSE
# =========================================================

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

    previous_messages = st.session_state.messages[:-1]

    with st.chat_message(
        "assistant",
        avatar="🤖",
    ):

        with st.spinner(
            "SWINGPULSE is analyzing your request..."
        ):

            try:
                answer = ask_agent(
                    user_message=prompt,
                    conversation_history=previous_messages,
                )

            except Exception as error:
                print(
                    f"SWINGPULSE application error: {error}"
                )

                answer = (
                    "Sorry, I could not complete the request right now. "
                    "Please try again shortly."
                )

        st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer-note">
        SWINGPULSE is an educational project based on historical data,
        external market-data services, technical indicators and an
        experimental machine-learning model. Its output is not financial
        advice and does not guarantee future performance.
    </div>
    """,
    unsafe_allow_html=True,
)
