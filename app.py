from __future__ import annotations

import re
from pathlib import Path

import streamlit as st

from agent import ask_agent


APP_ROOT = Path(__file__).resolve().parent
LOGO_PATH = APP_ROOT / "assets" / "logo.png"


st.set_page_config(
    page_title="SWINGPULSE AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def contains_hebrew(text: str) -> bool:
    return bool(re.search(r"[\u0590-\u05FF]", str(text)))


def render_chat_text(text: str) -> None:
    direction = "rtl" if contains_hebrew(text) else "ltr"
    alignment = "right" if direction == "rtl" else "left"

    st.markdown(
        f"""
        <div
            dir="{direction}"
            style="
                text-align: {alignment};
                unicode-bidi: plaintext;
                line-height: 1.75;
                font-size: 0.98rem;
                color: #294B5D;
            "
        >
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
    :root {
        --sp-navy: #173A4D;
        --sp-blue: #2797BB;
        --sp-teal: #26ADA4;
        --sp-green: #43BC7B;
        --sp-bg: #F5FAFB;
        --sp-surface: #FFFFFF;
        --sp-border: #DCEAED;
        --sp-muted: #6A818D;
    }

    * {
        box-sizing: border-box;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 90% 0%,
                rgba(38, 173, 164, 0.12),
                transparent 28%
            ),
            radial-gradient(
                circle at 10% 15%,
                rgba(39, 151, 187, 0.07),
                transparent 24%
            ),
            linear-gradient(
                180deg,
                #F7FCFD 0%,
                #FFFFFF 42%,
                #F5FAFB 100%
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

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #ECF9FA 0%,
                #F8FCFD 58%,
                #FFFFFF 100%
            );
        border-right: 1px solid var(--sp-border);
    }

    [data-testid="stSidebarContent"] {
        padding-top: 1rem;
    }

    .sp-hero {
        position: relative;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid var(--sp-border);
        border-radius: 26px;
        padding: 1.8rem 2rem;
        margin-bottom: 1.15rem;
        box-shadow: 0 18px 50px rgba(31, 86, 103, 0.08);
    }

    .sp-hero::after {
        content: "";
        position: absolute;
        width: 210px;
        height: 210px;
        right: -70px;
        top: -95px;
        border-radius: 50%;
        background:
            linear-gradient(
                135deg,
                rgba(39, 151, 187, 0.10),
                rgba(67, 188, 123, 0.13)
            );
    }

    .sp-status-badge {
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

    .sp-status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--sp-green);
        box-shadow: 0 0 0 4px rgba(67, 188, 123, 0.13);
    }

    .sp-title {
        color: var(--sp-navy);
        font-size: 2.55rem;
        line-height: 1.05;
        font-weight: 850;
        letter-spacing: -0.035em;
        margin: 0;
    }

    .sp-subtitle {
        max-width: 760px;
        color: var(--sp-muted);
        font-size: 1rem;
        line-height: 1.65;
        margin-top: 0.65rem;
        margin-bottom: 0;
    }

    .sp-capabilities {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
        margin: 1rem 0 1.35rem;
    }

    .sp-card {
        background: rgba(255, 255, 255, 0.94);
        border: 1px solid var(--sp-border);
        border-radius: 18px;
        padding: 1rem;
        box-shadow: 0 8px 25px rgba(31, 86, 103, 0.045);
    }

    .sp-card-icon {
        font-size: 1.35rem;
        margin-bottom: 0.45rem;
    }

    .sp-card-title {
        color: var(--sp-navy);
        font-size: 0.95rem;
        font-weight: 780;
        margin-bottom: 0.3rem;
    }

    .sp-card-text {
        color: var(--sp-muted);
        font-size: 0.8rem;
        line-height: 1.5;
    }

    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.97);
        border: 1px solid var(--sp-border);
        border-radius: 21px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.82rem;
        box-shadow: 0 8px 28px rgba(31, 86, 103, 0.055);
    }

    [data-testid="stChatInput"] {
        border-radius: 18px;
        box-shadow: 0 12px 34px rgba(31, 86, 103, 0.14);
    }

    [data-testid="stChatInput"] textarea {
        font-size: 1rem;
    }

    .stButton > button {
        width: 100%;
        min-height: 2.72rem;
        border-radius: 13px;
        border: 1px solid #C6E1E5;
        background: rgba(255, 255, 255, 0.93);
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
        border-color: var(--sp-teal);
        color: #087D78;
        background: #EAF9F7;
    }

    .sp-sidebar-heading {
        color: var(--sp-navy);
        font-size: 0.95rem;
        font-weight: 780;
        margin: 1rem 0 0.7rem;
    }

    .sp-sidebar-card {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid var(--sp-border);
        border-radius: 16px;
        padding: 1rem;
        color: #57717E;
        font-size: 0.84rem;
        line-height: 1.6;
        margin-top: 1rem;
    }

    .sp-sidebar-card b {
        color: var(--sp-navy);
    }

    .sp-footer {
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
        .sp-capabilities {
            grid-template-columns: 1fr;
        }

        .sp-title {
            font-size: 1.95rem;
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


WELCOME_MESSAGE = """
Hello! I’m **SWINGPULSE AI**, your stock-market research agent. 📈

I can analyze stocks, compare companies, scan technical conditions,
and explain indicators using market data and the SWINGPULSE
machine-learning model.

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


with st.sidebar:
    if LOGO_PATH.exists():
        st.image(
            str(LOGO_PATH),
            use_container_width=True,
        )
    else:
        st.markdown("## 📈 SWINGPULSE")

    st.markdown(
        '<div class="sp-sidebar-heading">Quick actions</div>',
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
        <div class="sp-sidebar-card">
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
        <div class="sp-sidebar-card">
            <b>Language support</b><br><br>
            The interface is in English. Questions can be written in
            English or Hebrew, and answers follow the language used
            in the question.
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <section class="sp-hero">
        <div class="sp-status-badge">
            <span class="sp-status-dot"></span>
            LIVE AI MARKET AGENT
        </div>

        <h1 class="sp-title">SWINGPULSE AI</h1>

        <p class="sp-subtitle">
            Ask natural-language questions about stocks and receive
            analysis powered by market data, technical indicators,
            and a trained machine-learning model.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)


if len(st.session_state.messages) == 1:
    st.markdown(
        """
        <div class="sp-capabilities">
            <div class="sp-card">
                <div class="sp-card-icon">📊</div>
                <div class="sp-card-title">Stock analysis</div>
                <div class="sp-card-text">
                    Review probability, RSI, MACD, volatility,
                    trend and additional technical features.
                </div>
            </div>

            <div class="sp-card">
                <div class="sp-card-icon">🔎</div>
                <div class="sp-card-title">Market scanning</div>
                <div class="sp-card-text">
                    Search selected stocks using RSI ranges
                    and model-probability conditions.
                </div>
            </div>

            <div class="sp-card">
                <div class="sp-card-icon">⚖️</div>
                <div class="sp-card-title">Stock comparison</div>
                <div class="sp-card-text">
                    Compare multiple companies using one
                    consistent analytical framework.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
        render_chat_text(
            message["content"]
        )


typed_prompt = st.chat_input(
    "Ask about a stock, indicator, comparison or market scan..."
)

prompt = typed_prompt

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None


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
        render_chat_text(prompt)

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
                print(
                    f"SWINGPULSE application error: {error}"
                )

                answer = (
                    "Sorry, I could not complete the request right now. "
                    "Please try again shortly."
                )

        render_chat_text(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


st.markdown(
    """
    <div class="sp-footer">
        SWINGPULSE is an educational project based on historical data,
        external market-data services, technical indicators and an
        experimental machine-learning model. Its output is not financial
        advice and does not guarantee future performance.
    </div>
    """,
    unsafe_allow_html=True,
)
