from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

from feature_engineering import add_technical_features

APP_ROOT = Path(__file__).resolve().parent
MODEL_PATH = APP_ROOT / "models" / "random_forest_model.joblib"
METADATA_PATH = APP_ROOT / "models" / "model_metadata.json"

st.set_page_config(page_title="SWINGPULSE", page_icon="📈", layout="wide")

@st.cache_resource
def load_assets():
    model = joblib.load(MODEL_PATH)
    with METADATA_PATH.open("r", encoding="utf-8") as f:
        metadata = json.load(f)
    return model, metadata

@st.cache_data(ttl=900, show_spinner=False)
def download_stock(symbol: str, period: str = "2y") -> pd.DataFrame:
    symbol = symbol.upper().strip()
    data = yf.download(
        symbol,
        period=period,
        interval="1d",
        auto_adjust=False,
        actions=True,
        progress=False,
        threads=False,
    )
    if data.empty:
        raise ValueError(f"No Yahoo Finance data returned for {symbol}.")
    data = data.reset_index()
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data.columns = [str(c).strip().replace(" ", "_") for c in data.columns]
    if "Adj_Close" in data.columns:
        data = data.drop(columns=["Adj_Close"])
    data["Symbol"] = symbol
    return data

def signal_from_probability(probability: float, threshold: float) -> str:
    if probability >= threshold + 0.15:
        return "Strong Watch"
    if probability >= threshold:
        return "Watch"
    if probability >= threshold - 0.10:
        return "Neutral"
    return "Low Potential"

def interpret_rsi(value: float) -> str:
    if value >= 70:
        return "Overbought"
    if value <= 30:
        return "Oversold"
    if value >= 55:
        return "Positive momentum"
    if value <= 45:
        return "Weak momentum"
    return "Neutral momentum"

def analyze_stock(symbol: str, model: Any, metadata: dict[str, Any]) -> dict[str, Any]:
    feature_columns = metadata["features"]
    threshold = float(metadata["decision_threshold"])
    raw = download_stock(symbol)
    featured = add_technical_features(raw)
    valid = featured.dropna(subset=feature_columns)
    if valid.empty:
        raise ValueError(f"Not enough historical data for {symbol}.")
    latest = valid.iloc[-1]
    model_input = pd.DataFrame(
        [latest[feature_columns].to_dict()],
        columns=feature_columns,
    ).replace([np.inf, -np.inf], np.nan)
    probability = float(model.predict_proba(model_input)[0, 1])

    ema20 = float(latest["EMA_20"])
    ema50 = float(latest["EMA_50"])
    ema200 = float(latest["EMA_200"])
    if ema20 > ema50 > ema200:
        trend = "Strong bullish trend"
    elif ema20 < ema50 < ema200:
        trend = "Strong bearish trend"
    elif ema20 > ema50:
        trend = "Short-term bullish trend"
    else:
        trend = "Mixed trend"

    return {
        "symbol": symbol.upper().strip(),
        "date": pd.to_datetime(latest["Date"]),
        "close": float(latest["Close"]),
        "probability": probability,
        "signal": signal_from_probability(probability, threshold),
        "rsi": float(latest["RSI_14"]),
        "rsi_status": interpret_rsi(float(latest["RSI_14"])),
        "macd": float(latest["MACD"]),
        "macd_signal": float(latest["MACD_Signal"]),
        "macd_status": "Bullish" if float(latest["MACD"]) > float(latest["MACD_Signal"]) else "Bearish",
        "trend": trend,
        "atr": float(latest["ATR_14"]),
        "volatility": float(latest["Volatility_20"]),
        "history": featured,
    }

def price_chart(history: pd.DataFrame, symbol: str):
    chart_data = history.dropna(subset=["Date", "Close"]).tail(180)
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=chart_data["Date"],
        open=chart_data["Open"],
        high=chart_data["High"],
        low=chart_data["Low"],
        close=chart_data["Close"],
        name=symbol,
    ))
    fig.add_trace(go.Scatter(x=chart_data["Date"], y=chart_data["EMA_20"], mode="lines", name="EMA 20"))
    fig.add_trace(go.Scatter(x=chart_data["Date"], y=chart_data["EMA_50"], mode="lines", name="EMA 50"))
    fig.update_layout(height=500, xaxis_rangeslider_visible=False, title=f"{symbol} — Price")
    return fig

def scan_rsi(symbols, minimum_rsi, maximum_rsi, model, metadata):
    rows = []
    progress = st.progress(0)
    for i, symbol in enumerate(symbols, start=1):
        try:
            result = analyze_stock(symbol, model, metadata)
            if minimum_rsi <= result["rsi"] <= maximum_rsi:
                rows.append({
                    "Symbol": result["symbol"],
                    "Date": result["date"].date(),
                    "Close": result["close"],
                    "RSI": result["rsi"],
                    "Probability": result["probability"],
                    "Signal": result["signal"],
                })
        except Exception:
            pass
        progress.progress(i / len(symbols))
    progress.empty()
    return pd.DataFrame(rows)

model, metadata = load_assets()

st.title("📈 SWINGPULSE")
st.caption("Live stock analysis powered by Yahoo Finance and a trained Random Forest model.")

with st.sidebar:
    symbol = st.text_input("Stock symbol", "AAPL").upper().strip()
    analyze_clicked = st.button("Analyze Stock", use_container_width=True, type="primary")
    st.divider()
    min_rsi, max_rsi = st.slider("RSI range", 0, 100, (26, 35))
    ticker_text = st.text_area(
        "Symbols to scan",
        "AAPL, MSFT, NVDA, AMD, META, AMZN, TSLA, GOOGL",
        height=120,
    )
    scan_clicked = st.button("Scan RSI Range", use_container_width=True)

if analyze_clicked or not scan_clicked:
    with st.spinner(f"Analyzing {symbol}..."):
        try:
            result = analyze_stock(symbol, model, metadata)
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Latest close", f"${result['close']:.2f}")
            c2.metric("Model probability", f"{result['probability'] * 100:.2f}%")
            c3.metric("Signal", result["signal"])
            c4.metric("RSI", f"{result['rsi']:.2f}")
            st.plotly_chart(price_chart(result["history"], result["symbol"]), use_container_width=True)
            st.dataframe(pd.DataFrame({
                "Indicator": ["RSI status", "MACD", "Trend", "ATR", "Volatility"],
                "Value": [
                    result["rsi_status"],
                    result["macd_status"],
                    result["trend"],
                    f"{result['atr']:.4f}",
                    f"{result['volatility']:.2%}",
                ],
            }), hide_index=True, use_container_width=True)
        except Exception as e:
            st.error(str(e))

if scan_clicked:
    symbols = [x.strip().upper() for x in ticker_text.replace("\n", ",").split(",") if x.strip()]
    results = scan_rsi(symbols, min_rsi, max_rsi, model, metadata)
    st.subheader(f"RSI scanner results: {min_rsi}–{max_rsi}")
    if results.empty:
        st.info("No matching stocks were found.")
    else:
        results["Close"] = results["Close"].map(lambda x: f"${x:.2f}")
        results["RSI"] = results["RSI"].map(lambda x: f"{x:.2f}")
        results["Probability"] = results["Probability"].map(lambda x: f"{x * 100:.2f}%")
        st.dataframe(results, hide_index=True, use_container_width=True)

st.divider()
st.caption("Educational project only. Not financial advice.")
