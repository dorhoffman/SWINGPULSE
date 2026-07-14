from __future__ import annotations

import re
from pathlib import Path

import streamlit as st

from agent import ask_agent


# =========================================================
# APP CONFIGURATION
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
# LANGUAGE AND DIRECTION HELPERS
# =========================================================

def contains_hebrew(text: str) -> bool:
    """Check whether a text contains Hebrew characters."""
    return bool(re.search(r"[\u0590-\u05FF]", str(text)))


def render_message_content(content: str) -> None:
    """
    Display Hebrew messages right-to-left
    and English messages left-to-right.
    """

    direction = "rtl" if contains_hebrew(content) else "ltr"
    alignment = "right" if direction == "rtl" else "left"

    st.markdown(
        f"""
        <div
            dir="{direction}"
            style="
                text-align: {alignment};
                line-height: 1.75;
                font-size: 0.98rem;
            "
        >
            {content}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# DESIGN
# =========================================================

st.markdown(
    """
    <style>

    :root {
        --sp-navy: #18364A;
        --sp-blue: #258EB5;
        --sp-teal: #22AAA1;
        --sp-green: #43BC7B;
        --sp-light: #F4FAFB;
        --sp-border: #DCECEF;
        --sp-muted: #6A8290;
    }

    /* Main application background */
    .stApp {
        background:
            radial-gradient(
                circle at 90% 0%,
                rgba(34, 170, 161, 0.10),
                transparent 28%
            ),
            linear-gradient(
                180deg,
                #F7FCFD 0%,
                #FFFFFF 38%,
                #F7FAFB 100%
            );
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.8rem;
        padding-bottom: 6rem;
    }

    /* Remove unnecessary Streamlit interface */
    #MainMenu {
        visibility: hidden;
    }

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
                #F8FCFD 55%,
                #FFFFFF 100%
            );
        border-right: 1px solid var(--sp-border);
    }

    [data-testid="stSidebarContent"] {
        padding-top: 1.2rem;
    }

    /* Main header */
    .sp-header {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid var(--sp-border);
        border-radius: 24px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 12px 36px rgba(31, 92, 110, 0.07);
    }

    .sp-product-name {
        color: var(--sp-navy);
        font-size: 2.35rem;
        font-weight: 850;
        line-height: 1.05;
        letter-spacing: -0.03em;
        margin: 0;
    }

    .sp-product-description {
        color: var(--sp-muted);
        font-size: 1rem;
        line-height: 1.65;
        margin-top: 0.55rem;
        margin-bottom: 0;
    }

    .sp-live-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.38rem 0.78rem;
        border-radius: 999px;
        background: #E1F8F3;
        color: #117E72;
        font-size: 0.76rem;
        font-weight: 750;
        letter-spacing: 0.05em;
        margin-bottom: 0.7rem;
    }

    .sp-live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #2CBB7F;
        display: inline-block;
    }

    /* Chat area */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid var(--sp-border);
        border-radius: 20px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 7px 24px rgba(43, 93, 110, 0.055);
    }

    [data-testid="stChatMessage"]:has(
        [data-testid="chatAvatarIcon-user"]
    ) {
        background: #F0FAFA;
        border-color: #CFEAE8;
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        border-radius: 18px;
        box-shadow: 0 10px 32px rgba(32, 91, 108, 0.12);
    }

    [data-testid="stChatInput"] textarea {
        font-size: 1rem;
    }

    /* Buttons */
    .stButton > button {
        width: 100%;
        min-height: 2.65rem;
        border-radius: 13px;
        border: 1px solid #C7E3E6;
        background: rgba(255, 255, 255, 0.90);
        color: #285368;
        font-weight: 650;
        text-align: left;
        transition:
            transform 0.16s ease,
            border-color 0.16s ease,
            background 0.16s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        border-color: var(--sp-teal);
        color: #0D7E77;
        background: #EAF9F7;
    }

    /* Sidebar cards */
    .sp-sidebar-title {
        color: var(--sp-navy);
        font-size: 1rem;
        font-weight: 750;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }

    .sp-info-card {
        background: rgba(255, 255, 255, 0.90);
        border: 1px solid var(--sp-border);
        border-radius: 16px;
        padding: 1rem;
        color: #55707E;
        font-size: 0.84rem;
        line-height: 1.6;
        margin-top: 1rem;
    }

    .sp-info-card b {
        color: var(--sp-navy);
    }

    /* Welcome prompts */
    .sp-capabilities {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
        margin: 1rem 0 1.25rem;
    }

    .sp-capability-card {
        background: rgba(255, 255, 255, 0.90);
        border: 1px solid var(--sp-border);
        border-radius: 16px;
        padding: 0.95rem;
        min-height: 105px;
    }

    .sp-capability-title {
        color: var(--sp-navy);
        font-weight: 750;
        font-size: 0.91rem;
        margin-bottom: 0.3rem;
    }

    .sp-capability-text {
        color: var(--sp-muted);
        font-size: 0.79rem;
        line-height: 1.45;
    }

    .sp-disclaimer {
        max-width: 880px;
        margin: 2rem auto 0;
        padding-top: 1rem;
        border-top: 1px solid #E1ECEF;
        color: #8496A0;
        font-size: 0.76rem;
        text-align: center;
        line-height: 1.55;
    }

    @media (max-width: 850px) {
        .sp-capabilities {
            grid-template-columns: 1fr;
        }

        .sp-product-name {
            font-size: 1.85rem;
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

WELCOME_MESSAGE = (
    "Hello! I’m **SWINGPULSE AI**, your stock-market research agent. 📈\n\n"
    "You can ask me to analyze a stock, compare companies, scan for "
    "technical conditions, or explain indicators.\n\n"
    "You may ask questions in **English or Hebrew**."
)

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
        '<div class="sp-sidebar-title">Quick actions</div>',
        unsafe_allow_html=True,
    )

    example_prompts = [
        (
            "Analyze AAPL",
            "Analyze AAPL and explain the model result.",
        ),
        (
            "Compare NVDA and AMD",
            "Compare NVDA and AMD. Which currently appears stronger?",
        ),
        (
            "Find stocks near RSI 30",
            "Find stocks with an RSI between 26 and 35.",
        ),
        (
            "Find probability above 45%",
            "Find stocks with a model probability above 45 percent.",
        ),
        (
            "Explain MACD",
            "Explain MACD and how traders commonly interpret it.",
        ),
    ]

    for index, (label, prompt_text) in enumerate(example_prompts):
        if st.button(
            label,
            key=f"example_prompt_{index}",
        ):
            st.session_state.pending_prompt = prompt_text

    st.divider()

    if st.button(
        "Clear conversation",
        key="clear_conversation",
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
        <div class="sp-info-card">
            <b>How does it work?</b><br><br>
            The agent interprets your request, selects an analytical
            tool, retrieves market data, calculates technical indicators,
            and runs the SWINGPULSE Random Forest model.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sp-info-card">
            <b>Supported languages</b><br><br>
            You can write in English or Hebrew. The interface remains
            in English, while the agent can respond in the language
            used in your question.
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="sp-header">
        <div class="sp-live-badge">
            <span class="sp-live-dot"></span>
            LIVE AI MARKET AGENT
        </div>

        <h1 class="sp-product-name">
            SWINGPULSE AI
        </h1>

        <p class="sp-product-description">
            Ask natural-language questions about stocks and receive
            analysis powered by live market data, technical indicators,
            and a trained machine-learning model.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# CAPABILITY CARDS
# =========================================================

if len(st.session_state.messages) == 1:
    st.markdown(
        """
        <div class="sp-capabilities">

            <div class="sp-capability-card">
                <div class="sp-capability-title">
                    📊 Stock analysis
                </div>
                <div class="sp-capability-text">
                    Review model probability, RSI, MACD,
                    volatility and trend information.
                </div>
            </div>

            <div class="sp-capability-card">
                <div class="sp-capability-title">
                    🔎 Market scanning
                </div>
                <div class="sp-capability-text">
                    Search a selected stock list using RSI
                    or model-probability conditions.
                </div>
            </div>

            <div class="sp-capability-card">
                <div class="sp-capability-title">
                    ⚖️ Stock comparison
                </div>
                <div class="sp-capability-text">
                    Compare several stocks using the same
                    technical and machine-learning framework.
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

    avatar = "🤖" if message["role"] == "assistant" else "👤"

    with st.chat_message(
        message["role"],
        avatar=avatar,
    ):
        render_message_content(
            message["content"]
        )


# =========================================================
# CHAT INPUT
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
        render_message_content(prompt)

    previous_messages = (
        st.session_state.messages[:-1]
    )

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
                answer = (
                    "I could not complete the request at this time.\n\n"
                    f"Error: `{error}`"
                )

        render_message_content(answer)

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
    <div class="sp-disclaimer">
        SWINGPULSE is an educational project based on historical data,
        external market-data services and an experimental machine-learning
        model. Its output is not financial advice and does not guarantee
        future performance.
    </div>
    """,
    unsafe_allow_html=True,
)
