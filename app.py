from __future__ import annotations

import re
from pathlib import Path

import streamlit as st

from agent import ask_agent


APP_ROOT = Path(__file__).resolve().parent
LOGO_PATH = APP_ROOT / "assets" / "logo.png"


st.set_page_config(
    page_title="SWINGPULSE AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def contains_hebrew(text: str) -> bool:
    return bool(re.search(r"[\u0590-\u05FF]", str(text)))


# ---------------------------------------------------------------------------
# Signature hero graphic: a heartbeat trace that resolves into a rising
# candlestick pattern. This is the one deliberate visual flourish of the
# page — it makes the "pulse" in SWINGPULSE literal, and it doubles as a
# small piece of real market vocabulary rather than decoration for its own
# sake. Everything else on the page stays quiet by comparison.
# ---------------------------------------------------------------------------
HERO_SIGNATURE_SVG = """
<svg class="sp-signature" viewBox="0 0 860 130" fill="none"
     xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Pulse trace resolving into a rising candlestick pattern">
  <path class="sp-signature-line" d="M0,70 L70,70 L88,28 L106,112 L124,46 L142,70
           L230,70 L248,36 L266,104 L284,58 L300,70
           L380,70 L440,70"
        stroke="url(#sp-pulse-gradient)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle class="sp-signature-dot" cx="440" cy="70" r="4.5" fill="var(--sp-amber)"/>

  <line x1="569" y1="85" x2="569" y2="55" stroke="var(--sp-teal)" stroke-width="2"/>
  <rect x="560" y="60" width="18" height="18" fill="var(--sp-teal)" rx="2"/>
  <line x1="609" y1="65" x2="609" y2="74" stroke="var(--sp-coral)" stroke-width="2"/>
  <rect x="600" y="60" width="18" height="8" fill="var(--sp-coral)" rx="2"/>
  <line x1="649" y1="72" x2="649" y2="38" stroke="var(--sp-teal)" stroke-width="2"/>
  <rect x="640" y="42" width="18" height="26" fill="var(--sp-teal)" rx="2"/>
  <line x1="689" y1="45" x2="689" y2="55" stroke="var(--sp-coral)" stroke-width="2"/>
  <rect x="680" y="42" width="18" height="8" fill="var(--sp-coral)" rx="2"/>
  <line x1="729" y1="54" x2="729" y2="18" stroke="var(--sp-teal)" stroke-width="2"/>
  <rect x="720" y="22" width="18" height="28" fill="var(--sp-teal)" rx="2"/>
  <line x1="769" y1="25" x2="769" y2="34" stroke="var(--sp-coral)" stroke-width="2"/>
  <rect x="760" y="22" width="18" height="8" fill="var(--sp-coral)" rx="2"/>
  <line x1="809" y1="33" x2="809" y2="5" stroke="var(--sp-teal)" stroke-width="2"/>
  <rect x="800" y="8" width="18" height="22" fill="var(--sp-teal)" rx="2"/>

  <defs>
    <linearGradient id="sp-pulse-gradient" x1="0" y1="0" x2="440" y2="0" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#35D0BA"/>
      <stop offset="1" stop-color="#FF9F45"/>
    </linearGradient>
  </defs>
</svg>
"""


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
            "
        >
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_message(role: str, content: str) -> None:
    """
    Renders a chat turn as a terminal-log style row instead of Streamlit's
    default rounded avatar bubble, so the whole page reads as one
    consistent trading-desk surface rather than a generic chat widget
    dropped on top of it.
    """
    is_assistant = role == "assistant"
    row_class = "sp-msg sp-msg-assistant" if is_assistant else "sp-msg sp-msg-user"
    label = "SWINGPULSE" if is_assistant else "YOU"

    st.markdown(
        f'<div class="{row_class}"><div class="sp-msg-label">{label}</div></div>',
        unsafe_allow_html=True,
    )

    body_class = "sp-msg-body sp-msg-body-assistant" if is_assistant else "sp-msg-body sp-msg-body-user"

    with st.container():
        st.markdown(f'<div class="{body_class}">', unsafe_allow_html=True)
        render_chat_text(content)
        st.markdown("</div>", unsafe_allow_html=True)


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
        --sp-ink: #0B1220;
        --sp-panel: #121A2B;
        --sp-panel-2: #17213A;
        --sp-border: rgba(231, 236, 244, 0.10);
        --sp-text: #E7ECF4;
        --sp-muted: #8A96B2;
        --sp-amber: #FF9F45;
        --sp-teal: #35D0BA;
        --sp-coral: #FF5C72;
    }

    * {
        box-sizing: border-box;
    }

    html, body, [class*="css"] {
        font-family: 'IBM Plex Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 85% -10%, rgba(255, 159, 69, 0.08), transparent 32%),
            radial-gradient(circle at -5% 20%, rgba(53, 208, 186, 0.07), transparent 30%),
            var(--sp-ink);
        color: var(--sp-text);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.75rem;
        padding-bottom: 7rem;
    }

    #MainMenu, footer { visibility: hidden; }
    header { background: transparent; }

    a { color: var(--sp-amber); }

    /* Visible keyboard focus, kept even though the rest of the theme is dark */
    button:focus-visible, textarea:focus-visible, input:focus-visible {
        outline: 2px solid var(--sp-amber) !important;
        outline-offset: 2px;
    }

    [data-testid="stSidebar"] {
        background: var(--sp-panel);
        border-right: 1px solid var(--sp-border);
    }

    [data-testid="stSidebarContent"] { padding-top: 1.1rem; }

    .sp-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        color: var(--sp-teal);
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    .sp-eyebrow-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--sp-teal);
        box-shadow: 0 0 0 4px rgba(53, 208, 186, 0.16);
    }

    .sp-hero {
        padding: 0.4rem 0 1.6rem;
        margin-bottom: 0.4rem;
        border-bottom: 1px solid var(--sp-border);
    }

    .sp-title {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--sp-text);
        font-size: 3rem;
        line-height: 1;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
    }

    .sp-subtitle {
        max-width: 620px;
        color: var(--sp-muted);
        font-size: 1rem;
        line-height: 1.65;
        margin-top: 0.85rem;
    }

    .sp-signature {
        width: 100%;
        height: auto;
        margin-top: 1.3rem;
        max-width: 860px;
    }

    .sp-signature-line {
        stroke-dasharray: 620;
        stroke-dashoffset: 620;
        animation: sp-draw 1.6s ease-out forwards;
    }

    .sp-signature-dot {
        opacity: 0;
        animation: sp-dot-in 0.4s ease-out 1.5s forwards, sp-pulse 1.8s ease-in-out 2s infinite;
        transform-origin: 440px 70px;
    }

    @keyframes sp-draw { to { stroke-dashoffset: 0; } }
    @keyframes sp-dot-in { to { opacity: 1; } }
    @keyframes sp-pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.6); }
    }

    @media (prefers-reduced-motion: reduce) {
        .sp-signature-line, .sp-signature-dot { animation: none !important; stroke-dashoffset: 0; opacity: 1; }
    }

    .sp-panels {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.85rem;
        margin: 1.5rem 0 1.5rem;
    }

    .sp-panel {
        background: var(--sp-panel);
        border: 1px solid var(--sp-border);
        border-radius: 10px;
        padding: 1.1rem 1.2rem;
    }

    .sp-panel-code {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        color: var(--sp-amber);
        margin-bottom: 0.55rem;
    }

    .sp-panel-title {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--sp-text);
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }

    .sp-panel-text {
        color: var(--sp-muted);
        font-size: 0.83rem;
        line-height: 1.5;
    }

    .sp-sidebar-heading {
        font-family: 'IBM Plex Mono', monospace;
        color: var(--sp-muted);
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 1.2rem 0 0.6rem;
    }

    .stButton > button {
        width: 100%;
        min-height: 2.6rem;
        border-radius: 8px;
        border: 1px solid var(--sp-border);
        background: var(--sp-panel-2);
        color: var(--sp-text);
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.82rem;
        text-align: left;
        transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease;
    }

    .stButton > button::before {
        content: "\203A  ";
        color: var(--sp-amber);
    }

    .stButton > button:hover {
        border-color: var(--sp-amber);
        color: var(--sp-amber);
        background: rgba(255, 159, 69, 0.06);
    }

    .sp-sidebar-card {
        background: var(--sp-panel-2);
        border: 1px solid var(--sp-border);
        border-radius: 10px;
        padding: 0.95rem 1rem;
        color: var(--sp-muted);
        font-size: 0.82rem;
        line-height: 1.6;
        margin-top: 0.9rem;
    }

    .sp-sidebar-card b { color: var(--sp-text); }

    .sp-msg {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 1.3rem 0 0.5rem;
    }

    .sp-msg-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        color: var(--sp-muted);
    }

    .sp-msg-assistant .sp-msg-label { color: var(--sp-amber); }
    .sp-msg-user .sp-msg-label { color: var(--sp-teal); }

    .sp-msg-body {
        background: var(--sp-panel);
        border: 1px solid var(--sp-border);
        border-left: 3px solid var(--sp-muted);
        border-radius: 0 10px 10px 0;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.2rem;
        color: var(--sp-text);
    }

    .sp-msg-body-assistant { border-left-color: var(--sp-amber); }
    .sp-msg-body-user { border-left-color: var(--sp-teal); }

    .sp-msg-body table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
        margin: 0.6rem 0;
    }

    .sp-msg-body th, .sp-msg-body td {
        border-bottom: 1px solid var(--sp-border);
        padding: 0.4rem 0.6rem;
        text-align: left;
    }

    .sp-msg-body th {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.06em;
        color: var(--sp-muted);
        text-transform: uppercase;
    }

    .sp-msg-body code {
        font-family: 'IBM Plex Mono', monospace;
        background: rgba(255, 255, 255, 0.06);
        padding: 0.1rem 0.35rem;
        border-radius: 4px;
    }

    [data-testid="stChatInput"] {
        border-radius: 10px;
        border: 1px solid var(--sp-border);
        background: var(--sp-panel);
    }

    [data-testid="stChatInput"] textarea {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 1rem;
        color: var(--sp-text);
    }

    .sp-footer {
        max-width: 900px;
        margin: 2.2rem auto 0;
        border-top: 1px solid var(--sp-border);
        padding-top: 1rem;
        color: var(--sp-muted);
        font-size: 0.76rem;
        line-height: 1.55;
        text-align: center;
    }

    @media (max-width: 850px) {
        .sp-panels { grid-template-columns: 1fr; }
        .sp-title { font-size: 2.1rem; }
        .block-container { padding-left: 1rem; padding-right: 1rem; }
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
        {"role": "assistant", "content": WELCOME_MESSAGE}
    ]

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.markdown("## ◈ SWINGPULSE")

    st.markdown('<div class="sp-sidebar-heading">Quick commands</div>', unsafe_allow_html=True)

    examples = [
        ("Analyze AAPL", "Analyze AAPL and explain the model result."),
        ("Compare NVDA and AMD", "Compare NVDA and AMD and explain which currently appears stronger."),
        ("Find stocks near RSI 30", "Find stocks with an RSI between 26 and 35."),
        ("Probability above 45%", "Find stocks with a model probability above 45 percent."),
        ("Explain MACD", "Explain MACD and how it is commonly interpreted."),
    ]

    for index, (label, prompt_text) in enumerate(examples):
        if st.button(label, key=f"quick_action_{index}"):
            st.session_state.pending_prompt = prompt_text

    st.divider()

    if st.button("Clear conversation", key="clear_chat"):
        st.session_state.messages = [
            {"role": "assistant", "content": WELCOME_MESSAGE}
        ]
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown(
        """
        <div class="sp-sidebar-card">
            <b>How it works</b><br><br>
            The agent understands your request, selects an analytical
            tool, retrieves market data, calculates indicators, and
            applies the SWINGPULSE model.
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
    f"""
    <section class="sp-hero">
        <div class="sp-eyebrow"><span class="sp-eyebrow-dot"></span>AI SWING-TRADE RESEARCH DESK</div>
        <h1 class="sp-title">SWINGPULSE</h1>
        <p class="sp-subtitle">
            Ask natural-language questions about stocks and receive
            analysis powered by market data, technical indicators,
            and a trained machine-learning model.
        </p>
        {HERO_SIGNATURE_SVG}
    </section>
    """,
    unsafe_allow_html=True,
)


if len(st.session_state.messages) == 1:
    st.markdown(
        """
        <div class="sp-panels">
            <div class="sp-panel">
                <div class="sp-panel-code">ANALYZE</div>
                <div class="sp-panel-title">Stock analysis</div>
                <div class="sp-panel-text">
                    Review probability, RSI, MACD, volatility,
                    trend and additional technical features.
                </div>
            </div>
            <div class="sp-panel">
                <div class="sp-panel-code">SCAN</div>
                <div class="sp-panel-title">Market scanning</div>
                <div class="sp-panel-text">
                    Search selected stocks using RSI ranges
                    and model-probability conditions.
                </div>
            </div>
            <div class="sp-panel">
                <div class="sp-panel-code">RANK</div>
                <div class="sp-panel-title">Stock comparison</div>
                <div class="sp-panel-text">
                    Compare multiple companies using one
                    consistent analytical framework.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


for message in st.session_state.messages:
    render_message(message["role"], message["content"])


typed_prompt = st.chat_input(
    "Ask about a stock, indicator, comparison or market scan..."
)

prompt = typed_prompt

if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None


if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_message("user", prompt)

    previous_messages = st.session_state.messages[:-1]

    placeholder = st.empty()
    with placeholder.container():
        st.markdown(
            '<div class="sp-msg sp-msg-assistant"><div class="sp-msg-label">SWINGPULSE</div></div>'
            '<div class="sp-msg-body sp-msg-body-assistant">Analyzing…</div>',
            unsafe_allow_html=True,
        )

    try:
        answer = ask_agent(
            user_message=prompt,
            conversation_history=previous_messages,
        )
    except Exception as error:
        print(f"SWINGPULSE application error: {error}")
        answer = (
            "Sorry, I could not complete the request right now. "
            "Please try again shortly."
        )

    placeholder.empty()
    render_message("assistant", answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})


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
