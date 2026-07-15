from __future__ import annotations

import base64
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


def force_scroll_to_top_once() -> None:
    """
    st.chat_input has a known Streamlit behavior where the page loads
    already scrolled down (so the fixed input bar is guaranteed visible),
    which hides the hero/title on first load. This forces the browser
    back to the top right after the initial render. It only runs once
    per session — later reruns (e.g. after sending a message) are left
    alone, since auto-scrolling to a new answer is normal chat behavior.
    """
    if st.session_state.get("_scrolled_to_top"):
        return

    st.session_state["_scrolled_to_top"] = True

    st.components.v1.html(
        "<script>"
        "function spScrollTop(){"
        "  try {"
        "    var doc = window.parent.document;"
        "    var selectors = ["
        "      'section.main', '[data-testid=\"stMain\"]',"
        "      '[data-testid=\"stAppViewContainer\"]',"
        "      '[data-testid=\"stAppViewBlockContainer\"]',"
        "      '.main .block-container'"
        "    ];"
        "    selectors.forEach(function(sel){"
        "      var el = doc.querySelector(sel);"
        "      if (el) { el.scrollTop = 0; }"
        "    });"
        "    if (doc.scrollingElement) { doc.scrollingElement.scrollTop = 0; }"
        "    doc.documentElement.scrollTop = 0;"
        "    doc.body.scrollTop = 0;"
        "    window.parent.scrollTo({top: 0, left: 0, behavior: 'instant'});"
        "  } catch (e) {}"
        "}"
        "spScrollTop();"
        "[0, 50, 150, 300, 600, 1000, 1500, 2000].forEach(function(t){"
        "  setTimeout(spScrollTop, t);"
        "});"
        "</script>",
        height=0,
    )


# ---------------------------------------------------------------------------
# Signature hero graphic: a heartbeat trace that resolves into a rising
# candlestick pattern — a literal rendering of "pulse" in SWINGPULSE.
#
# Embedded as a base64 data-URI <img> rather than inline <svg> markup,
# deliberately, to sidestep two real Streamlit rendering bugs:
#   1. st.markdown(unsafe_allow_html=True) truncates/breaks HTML at the
#      first blank line in a multi-line string (streamlit#921, #859).
#   2. It lowercases SVG attribute names (e.g. viewBox -> viewbox,
#      gradientUnits -> gradientunits), which silently breaks SVG
#      rendering since SVG attributes are case-sensitive (streamlit#2554).
# A data-URI image is opaque to both bugs. The animation is defined in a
# <style> block *inside* the SVG itself, so it still animates on load
# even though it's referenced as an external image.
# ---------------------------------------------------------------------------
def _build_hero_signature_data_uri() -> str:
    svg = """<svg viewBox="0 0 860 130" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Pulse trace resolving into a rising candlestick pattern"><style>.sp-line{stroke-dasharray:620;stroke-dashoffset:620;animation:sp-draw 1.6s ease-out forwards;}.sp-dot{opacity:0;transform-origin:440px 70px;animation:sp-dot-in .4s ease-out 1.5s forwards,sp-pulse 1.8s ease-in-out 2s infinite;}@keyframes sp-draw{to{stroke-dashoffset:0;}}@keyframes sp-dot-in{to{opacity:1;}}@keyframes sp-pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.6);}}@media (prefers-reduced-motion: reduce){.sp-line,.sp-dot{animation:none;stroke-dashoffset:0;opacity:1;}}</style><path class="sp-line" d="M0,70 L70,70 L88,28 L106,112 L124,46 L142,70 L230,70 L248,36 L266,104 L284,58 L300,70 L380,70 L440,70" stroke="url(#g)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><circle class="sp-dot" cx="440" cy="70" r="4.5" fill="#7B61FF"/><line x1="569" y1="85" x2="569" y2="55" stroke="#35D0BA" stroke-width="2"/><rect x="560" y="60" width="18" height="18" fill="#35D0BA" rx="2"/><line x1="609" y1="65" x2="609" y2="74" stroke="#FF5C72" stroke-width="2"/><rect x="600" y="60" width="18" height="8" fill="#FF5C72" rx="2"/><line x1="649" y1="72" x2="649" y2="38" stroke="#35D0BA" stroke-width="2"/><rect x="640" y="42" width="18" height="26" fill="#35D0BA" rx="2"/><line x1="689" y1="45" x2="689" y2="55" stroke="#FF5C72" stroke-width="2"/><rect x="680" y="42" width="18" height="8" fill="#FF5C72" rx="2"/><line x1="729" y1="54" x2="729" y2="18" stroke="#35D0BA" stroke-width="2"/><rect x="720" y="22" width="18" height="28" fill="#35D0BA" rx="2"/><line x1="769" y1="25" x2="769" y2="34" stroke="#FF5C72" stroke-width="2"/><rect x="760" y="22" width="18" height="8" fill="#FF5C72" rx="2"/><line x1="809" y1="33" x2="809" y2="5" stroke="#35D0BA" stroke-width="2"/><rect x="800" y="8" width="18" height="22" fill="#35D0BA" rx="2"/><defs><linearGradient id="g" x1="0" y1="0" x2="440" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#35D0BA"/><stop offset="1" stop-color="#7B61FF"/></linearGradient></defs></svg>"""
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


HERO_SIGNATURE_URI = _build_hero_signature_data_uri()


SIGNAL_STYLES = {
    "Strong Watch": {"color": "#35D0BA", "label": "STRONG WATCH"},
    "Watch": {"color": "#7B61FF", "label": "WATCH"},
    "Neutral": {"color": "#8A96B2", "label": "NEUTRAL"},
    "Low Potential": {"color": "#8A96B2", "label": "LOW POTENTIAL"},
}


def _build_gauge_data_uri(probability_percent: float, color: str) -> str:
    """
    Renders a radial probability gauge as a base64 SVG data-URI (same
    approach as the hero signature graphic, for the same two reasons:
    Streamlit's unsafe_allow_html breaks on blank lines inside a
    multi-line HTML string, and it lowercases SVG attribute names like
    viewBox, which silently breaks rendering).
    """
    probability_percent = max(0.0, min(100.0, probability_percent))
    radius = 50
    circumference = 2 * 3.14159265 * radius
    offset = circumference * (1 - probability_percent / 100)
    label = f"{probability_percent:.1f}%"

    svg = (
        '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="Setup probability {label}">'
        '<circle cx="60" cy="60" r="50" fill="none" stroke="#233150" stroke-width="10"/>'
        '<circle cx="60" cy="60" r="50" fill="none" '
        f'stroke="{color}" stroke-width="10" stroke-linecap="round" '
        f'stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}" '
        'transform="rotate(-90 60 60)"/>'
        f'<text x="60" y="56" text-anchor="middle" font-size="22" font-weight="700" '
        f'font-family="Arial, sans-serif" fill="#E7ECF4">{label}</text>'
        '<text x="60" y="76" text-anchor="middle" font-size="10" '
        'font-family="Arial, sans-serif" fill="#8A96B2">PROBABILITY</text>'
        '</svg>'
    )
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def render_result_card(tool_call: dict | None) -> None:
    """
    Renders a visual summary card for tool results that carry a
    probability/signal (currently analyze_stock). The card is built
    entirely from the structured tool output — the LLM never touches
    these numbers, it only narrates around them afterwards.
    """
    if not tool_call or tool_call.get("tool_name") != "analyze_stock":
        return

    data = tool_call.get("data") or {}
    if not data.get("success"):
        return

    signal = data.get("signal", "Neutral")
    style = SIGNAL_STYLES.get(signal, SIGNAL_STYLES["Neutral"])
    gauge_uri = _build_gauge_data_uri(
        data.get("probability_percent", 0.0), style["color"]
    )

    chips = [
        ("RSI(14)", f'{data.get("rsi_14", "—")} · {data.get("rsi_status", "")}'),
        ("MACD", data.get("macd_status", "—")),
        ("Trend", data.get("trend", "—")),
        ("Volatility(20)", f'{data.get("volatility_20_percent", "—")}%'),
    ]
    chips_html = "".join(
        f'<div class="sp-chip"><span class="sp-chip-k">{k}</span>'
        f'<span class="sp-chip-v">{v}</span></div>'
        for k, v in chips
    )

    st.markdown(
        '<div class="sp-result-card">'
        '<div class="sp-result-gauge">'
        f'<img src="{gauge_uri}" alt="probability gauge" />'
        "</div>"
        '<div class="sp-result-main">'
        f'<div class="sp-result-symbol">{data.get("symbol", "")}'
        f'<span class="sp-result-price">${data.get("close", "—")}</span></div>'
        f'<div class="sp-result-badge" style="background:{style["color"]}22;'
        f'color:{style["color"]};border-color:{style["color"]}55;">{style["label"]}</div>'
        f'<div class="sp-chip-row">{chips_html}</div>'
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def render_wordmark() -> None:
    st.markdown(
        '<div class="sp-wordmark">'
        '<svg class="sp-wordmark-icon" viewBox="0 0 64 40" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M2,26 L14,26 L19,10 L24,32 L29,18 L34,26 L44,26" '
        'stroke="#35D0BA" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
        '<rect x="47" y="16" width="6" height="10" fill="#7B61FF" rx="1.5"/>'
        '<rect x="56" y="8" width="6" height="18" fill="#7B61FF" rx="1.5"/>'
        '</svg>'
        '<div class="sp-wordmark-text">'
        '<div class="sp-wordmark-title">SWINGPULSE</div>'
        '<div class="sp-wordmark-subtitle">AI SWING TRADE ASSISTANT</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_message(role: str, content: str, tool_call: dict | None = None) -> None:
    """
    Renders a chat turn as a labeled panel. The role label lives *inside*
    the bubble (top line) instead of as a separate floating row above it,
    so it reads as one connected unit rather than two disjoined pieces.

    The message body text is rendered with a plain st.markdown(content)
    call (no unsafe_allow_html wrapper around the text itself) so
    Streamlit's normal Markdown parser handles tables, bold text, and
    lists from the agent correctly, and so Hebrew/English mixed text
    goes through the browser's standard bidi algorithm instead of a
    hand-rolled one.
    """
    is_assistant = role == "assistant"
    label = "SWINGPULSE" if is_assistant else "YOU"
    role_class = "sp-msg-body-assistant" if is_assistant else "sp-msg-body-user"
    direction_class = "sp-dir-rtl" if contains_hebrew(content) else "sp-dir-ltr"

    st.markdown(
        f'<div class="sp-msg-body {role_class} {direction_class}">'
        f'<div class="sp-msg-label">{label}</div>',
        unsafe_allow_html=True,
    )
    if is_assistant:
        render_result_card(tool_call)
    st.markdown(content)
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
        --sp-accent: #7B61FF;
        --sp-teal: #35D0BA;
        --sp-coral: #FF5C72;
    }
    * { box-sizing: border-box; }
    html, body { background-color: var(--sp-ink) !important; }
    html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
    .stApp {
        background:
            radial-gradient(circle at 85% -10%, rgba(123, 97, 255, 0.10), transparent 32%),
            radial-gradient(circle at -5% 20%, rgba(53, 208, 186, 0.07), transparent 30%),
            var(--sp-ink);
        color: var(--sp-text);
    }
    [data-testid="stHeader"] { background: var(--sp-ink) !important; box-shadow: none !important; }
    [data-testid="stToolbar"] { background: transparent !important; }
    [data-testid="stDecoration"] { background: transparent !important; }
    .block-container { max-width: 1180px; padding-top: 1.75rem; padding-bottom: 7rem; }
    #MainMenu, footer { visibility: hidden; }
    a { color: var(--sp-accent); }
    button:focus-visible, textarea:focus-visible, input:focus-visible {
        outline: 2px solid var(--sp-accent) !important;
        outline-offset: 2px;
    }
    [data-testid="stSidebar"] { background: var(--sp-panel); border-right: 1px solid var(--sp-border); }
    [data-testid="stSidebarContent"] { padding-top: 1.1rem; }
    .sp-wordmark {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.6rem 0.2rem 1.2rem;
        border-bottom: 1px solid var(--sp-border);
        margin-bottom: 0.4rem;
    }
    .sp-wordmark-icon { width: 40px; height: 26px; flex-shrink: 0; }
    .sp-wordmark-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        color: var(--sp-text);
        line-height: 1.15;
    }
    .sp-wordmark-subtitle {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.6rem;
        letter-spacing: 0.08em;
        color: var(--sp-muted);
        margin-top: 0.15rem;
    }
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
        width: 7px; height: 7px; border-radius: 50%;
        background: var(--sp-teal);
        box-shadow: 0 0 0 4px rgba(53, 208, 186, 0.16);
    }
    .sp-hero { padding: 0.4rem 0 1.6rem; margin-bottom: 0.4rem; border-bottom: 1px solid var(--sp-border); }
    .sp-title {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--sp-text);
        font-size: 3rem;
        line-height: 1;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .sp-subtitle { max-width: 620px; color: var(--sp-muted); font-size: 1rem; line-height: 1.65; margin-top: 0.85rem; }
    .sp-signature { width: 100%; height: auto; margin-top: 1.3rem; max-width: 860px; display: block; }
    .sp-panels { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.85rem; margin: 1.5rem 0; }
    .sp-panel { background: var(--sp-panel); border: 1px solid var(--sp-border); border-radius: 10px; padding: 1.1rem 1.2rem; }
    .sp-panel-code {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem; font-weight: 600; letter-spacing: 0.12em;
        color: var(--sp-accent); margin-bottom: 0.55rem;
    }
    .sp-panel-title { font-family: 'Space Grotesk', sans-serif; color: var(--sp-text); font-size: 1rem; font-weight: 600; margin-bottom: 0.35rem; }
    .sp-panel-text { color: var(--sp-muted); font-size: 0.83rem; line-height: 1.5; }
    .sp-sidebar-heading {
        font-family: 'IBM Plex Mono', monospace;
        color: var(--sp-muted); font-size: 0.72rem; font-weight: 600;
        letter-spacing: 0.12em; text-transform: uppercase; margin: 1.2rem 0 0.6rem;
    }
    .stButton > button {
        width: 100%; min-height: 2.6rem; border-radius: 8px;
        border: 1px solid var(--sp-border); background: var(--sp-panel-2); color: var(--sp-text);
        font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem; text-align: left;
        transition: border-color 0.15s ease, color 0.15s ease, background 0.15s ease;
    }
    .stButton > button::before { content: "\\203A  "; color: var(--sp-accent); }
    .stButton > button:hover { border-color: var(--sp-accent); color: var(--sp-accent); background: rgba(123, 97, 255, 0.08); }
    .sp-sidebar-card {
        background: var(--sp-panel-2); border: 1px solid var(--sp-border); border-radius: 10px;
        padding: 0.95rem 1rem; color: var(--sp-muted); font-size: 0.82rem; line-height: 1.6; margin-top: 0.9rem;
    }
    .sp-sidebar-card b { color: var(--sp-text); }
    .sp-msg-body {
        background: var(--sp-panel); border: 1px solid var(--sp-border); border-left: 3px solid var(--sp-muted);
        border-radius: 0 10px 10px 0; padding: 0.85rem 1.1rem; margin: 1.1rem 0; color: var(--sp-text);
    }
    .sp-msg-body-assistant { border-left-color: var(--sp-accent); }
    .sp-msg-body-user { border-left-color: var(--sp-teal); }
    .sp-msg-label {
        font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; font-weight: 600;
        letter-spacing: 0.12em; margin-bottom: 0.5rem;
    }
    .sp-msg-body-assistant .sp-msg-label { color: var(--sp-accent); }
    .sp-msg-body-user .sp-msg-label { color: var(--sp-teal); }
    .sp-dir-rtl { direction: rtl; text-align: right; }
    .sp-dir-ltr { direction: ltr; text-align: left; }
    .sp-dir-rtl .sp-msg-label, .sp-dir-ltr .sp-msg-label { direction: ltr; text-align: inherit; }
    .sp-msg-body p { margin-bottom: 0.6rem; line-height: 1.7; }
    .sp-msg-body table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin: 0.6rem 0; }
    .sp-msg-body th, .sp-msg-body td { border-bottom: 1px solid var(--sp-border); padding: 0.4rem 0.6rem; text-align: left; }
    .sp-msg-body th { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; letter-spacing: 0.06em; color: var(--sp-muted); text-transform: uppercase; }
    .sp-msg-body code { font-family: 'IBM Plex Mono', monospace; background: rgba(255, 255, 255, 0.06); padding: 0.1rem 0.35rem; border-radius: 4px; }
    [data-testid="stBottom"], [data-testid="stBottomBlockContainer"] { background: var(--sp-ink) !important; }
    [data-testid="stChatInput"] {
        border-radius: 10px !important;
        border: 1px solid var(--sp-border) !important;
        background: var(--sp-panel) !important;
    }
    [data-testid="stChatInput"] * { background: transparent !important; }
    [data-testid="stChatInput"] textarea {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 1rem !important;
        color: var(--sp-text) !important;
        caret-color: var(--sp-accent) !important;
    }
    [data-testid="stChatInput"] textarea::placeholder { color: var(--sp-muted) !important; opacity: 1 !important; }
    [data-testid="stChatInputSubmitButton"] { background: var(--sp-accent) !important; }
    .sp-result-card {
        display: flex;
        align-items: center;
        gap: 1.2rem;
        background: var(--sp-panel-2);
        border: 1px solid var(--sp-border);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 1.3rem 0 0.6rem;
        direction: ltr;
    }
    .sp-result-gauge img { width: 96px; height: 96px; display: block; }
    .sp-result-main { flex: 1; min-width: 0; }
    .sp-result-symbol {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--sp-text);
        display: flex;
        align-items: baseline;
        gap: 0.6rem;
    }
    .sp-result-price { font-family: 'IBM Plex Mono', monospace; font-size: 0.95rem; color: var(--sp-muted); font-weight: 500; }
    .sp-result-badge {
        display: inline-block;
        margin-top: 0.35rem;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        border: 1px solid;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.08em;
    }
    .sp-chip-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.7rem; }
    .sp-chip {
        display: flex;
        flex-direction: column;
        background: var(--sp-panel);
        border: 1px solid var(--sp-border);
        border-radius: 8px;
        padding: 0.3rem 0.6rem;
        min-width: 84px;
    }
    .sp-chip-k {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.62rem;
        color: var(--sp-muted);
        letter-spacing: 0.05em;
    }
    .sp-chip-v { font-size: 0.82rem; color: var(--sp-text); font-weight: 500; }

    @media (max-width: 500px) {
        .sp-result-card { flex-direction: column; align-items: flex-start; }
    }

    .sp-footer {
        max-width: 900px; margin: 2.2rem auto 0; border-top: 1px solid var(--sp-border);
        padding-top: 1rem; color: var(--sp-muted); font-size: 0.76rem; line-height: 1.55; text-align: center;
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


WELCOME_MESSAGE = """Hello! I'm **SWINGPULSE AI**, your stock-market research agent. 📈

I can analyze stocks, compare companies, scan technical conditions, and explain indicators using market data and the SWINGPULSE machine-learning model.

You can ask questions in **English or Hebrew**.

Try: **Analyze AAPL**"""


if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

force_scroll_to_top_once()


with st.sidebar:
    render_wordmark()

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
        st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown(
        '<div class="sp-sidebar-card"><b>How it works</b><br><br>'
        'The agent understands your request, selects an analytical tool, '
        'retrieves market data, calculates indicators, and applies the '
        'SWINGPULSE model.</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sp-sidebar-card"><b>Language support</b><br><br>'
        'The interface is in English. Questions can be written in English '
        'or Hebrew, and answers follow the language used in the '
        'question.</div>',
        unsafe_allow_html=True,
    )


st.markdown(
    f'<section class="sp-hero">'
    f'<div class="sp-eyebrow"><span class="sp-eyebrow-dot"></span>AI SWING-TRADE RESEARCH DESK</div>'
    f'<h1 class="sp-title">SWINGPULSE</h1>'
    f'<p class="sp-subtitle">Ask natural-language questions about stocks and receive analysis '
    f'powered by market data, technical indicators, and a trained machine-learning model.</p>'
    f'<img class="sp-signature" src="{HERO_SIGNATURE_URI}" '
    f'alt="Pulse trace resolving into a rising candlestick pattern" />'
    f'</section>',
    unsafe_allow_html=True,
)


if len(st.session_state.messages) == 1:
    st.markdown(
        '<div class="sp-panels">'
        '<div class="sp-panel"><div class="sp-panel-code">ANALYZE</div>'
        '<div class="sp-panel-title">Stock analysis</div>'
        '<div class="sp-panel-text">Review probability, RSI, MACD, volatility, '
        'trend and additional technical features.</div></div>'
        '<div class="sp-panel"><div class="sp-panel-code">SCAN</div>'
        '<div class="sp-panel-title">Market scanning</div>'
        '<div class="sp-panel-text">Search selected stocks using RSI ranges '
        'and model-probability conditions.</div></div>'
        '<div class="sp-panel"><div class="sp-panel-code">RANK</div>'
        '<div class="sp-panel-title">Stock comparison</div>'
        '<div class="sp-panel-text">Compare multiple companies using one '
        'consistent analytical framework.</div></div>'
        '</div>',
        unsafe_allow_html=True,
    )


for message in st.session_state.messages:
    render_message(message["role"], message["content"], message.get("tool_call"))


typed_prompt = st.chat_input("Ask about a stock, indicator, comparison or market scan...")

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
            '<div class="sp-msg-body sp-msg-body-assistant sp-dir-ltr">'
            '<div class="sp-msg-label">SWINGPULSE</div>Analyzing…</div>',
            unsafe_allow_html=True,
        )

    tool_call = None
    try:
        answer, tool_call = ask_agent(user_message=prompt, conversation_history=previous_messages)
    except Exception as error:
        print(f"SWINGPULSE application error: {error}")
        answer = "Sorry, I could not complete the request right now. Please try again shortly."

    placeholder.empty()
    render_message("assistant", answer, tool_call)

    st.session_state.messages.append(
        {"role": "assistant", "content": answer, "tool_call": tool_call}
    )


st.markdown(
    '<div class="sp-footer">SWINGPULSE is an educational project based on historical data, '
    'external market-data services, technical indicators and an experimental machine-learning '
    'model. Its output is not financial advice and does not guarantee future performance.</div>',
    unsafe_allow_html=True,
)
