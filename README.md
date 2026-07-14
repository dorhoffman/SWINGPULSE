# SwingPulse AI

**An AI-powered swing-trading research assistant.** Ask questions about stocks in plain language (English or Hebrew) and get back technical analysis, model-based probability estimates, comparisons, and market scans — grounded in real market data, not generated from the language model's memory.

Live app: _add your Render URL here_

---

## What it does

SwingPulse combines a classic ML pipeline with an LLM-based conversational agent:

1. **Data layer** — daily OHLCV price history is pulled from yfinance, with automatic fallback to Stooq (and optionally Finnhub) if a provider is rate-limited or unavailable.
2. **Feature engineering** — RSI, MACD, EMA/SMA (20/50/200), Bollinger Bands, ATR, historical volatility, and price-to-moving-average ratios are computed from raw price data (`feature_engineering.py`).
3. **Model** — a trained classifier estimates the probability that a stock rises by a target return within a defined trading-day horizon (see `models/model_metadata.json` for the exact threshold and horizon used).
4. **Agent layer** — an LLM (OpenAI, via the Responses API) interprets the user's natural-language question, decides which analytical tool to call, and turns the structured result into a readable, formatted answer — never inventing numbers itself.
5. **UI** — a Streamlit chat interface (deployed on Render) that supports both English and Hebrew, with RTL rendering for Hebrew responses.

## Example questions

- `Analyze AAPL`
- `Compare NVDA and AMD`
- `Find stocks with an RSI between 26 and 35`
- `Find stocks with a model probability above 45 percent`
- `Explain MACD`
- (Hebrew works the same way, e.g. `נתח לי את מניית טסלה`)

## Project structure

```
SWINGPULSE/
├── .streamlit/
│   └── config.toml          # Streamlit dark theme configuration
├── assets/
│   └── logo.png
├── models/
│   ├── random_forest_model.joblib   # tracked with Git LFS
│   └── model_metadata.json          # feature list, threshold, horizon
├── notebooks/                # exploratory work: cleaning, EDA, feature
│                              # engineering, model training/evaluation,
│                              # agent design, live-data integration, demo
├── agent.py                  # LLM agent: system prompt, tool routing, tool loop
├── app.py                    # Streamlit chat UI
├── feature_engineering.py    # technical indicator calculations
├── tools.py                  # data download, model inference, agent tools
├── render.yaml                # Render deployment configuration
└── requirements.txt
```

## Running locally

```bash
git clone https://github.com/dorhoffman/SWINGPULSE.git
cd SWINGPULSE
git lfs install && git lfs pull      # required — model files are stored via Git LFS
pip install -r requirements.txt

export OPENAI_API_KEY="your-key-here"
# optional, only used as a last-resort data fallback:
export FINNHUB_API_KEY="your-key-here"

streamlit run app.py
```

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | Yes | Powers the conversational agent |
| `OPENAI_MODEL` | No (defaults to `gpt-4.1-mini`) | Overrides the model used |
| `FINNHUB_API_KEY` | No | Optional last-resort market-data fallback |

## Deployment notes

- Deployed on **Render** as a Streamlit web service (see `render.yaml`).
- Model files are stored with **Git LFS**. Render does not pull LFS content by default, so the build command explicitly runs `git lfs install && git lfs pull` before installing Python dependencies — without this step the app fails to start.
- Market data is fetched with a multi-provider fallback (yfinance → Stooq → Finnhub) since single-provider reliability from a cloud host can vary (IP-based rate limits, tier restrictions, etc.).

## Disclaimer

SwingPulse is an educational project built on historical data, third-party market-data services, technical indicators, and an experimental machine-learning model. Its output is not financial advice and does not guarantee future performance.
