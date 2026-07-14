from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import requests

from feature_engineering import add_technical_features


APP_ROOT = Path(__file__).resolve().parent
MODEL_PATH = APP_ROOT / "models" / "random_forest_model.joblib"
METADATA_PATH = APP_ROOT / "models" / "model_metadata.json"

MODEL = joblib.load(MODEL_PATH)

with METADATA_PATH.open("r", encoding="utf-8") as file:
    METADATA = json.load(file)

FEATURE_COLUMNS = METADATA["features"]
DECISION_THRESHOLD = float(METADATA["decision_threshold"])
PREDICTION_HORIZON = int(METADATA["prediction_horizon"])
TARGET_RETURN = float(METADATA["target_return"])


def _get_finnhub_api_key() -> str:
    api_key = os.getenv("FINNHUB_API_KEY")

    if not api_key:
        raise RuntimeError(
            "FINNHUB_API_KEY is not configured in the server environment."
        )

    return api_key


def download_stock_data(
    symbol: str,
    days_back: int = 900,
    retries: int = 3,
) -> pd.DataFrame:
    symbol = str(symbol).upper().strip()

    if not symbol:
        raise ValueError("A stock symbol is required.")

    api_key = _get_finnhub_api_key()

    end_timestamp = int(time.time())
    start_timestamp = end_timestamp - (days_back * 24 * 60 * 60)

    url = "https://finnhub.io/api/v1/stock/candle"

    params = {
        "symbol": symbol,
        "resolution": "D",
        "from": start_timestamp,
        "to": end_timestamp,
        "token": api_key,
    }

    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=30,
            )
            response.raise_for_status()

            result = response.json()

            if result.get("s") != "ok":
                raise ValueError(
                    f"No Finnhub market data returned for {symbol}."
                )

            data = pd.DataFrame(
                {
                    "Date": pd.to_datetime(
                        result["t"],
                        unit="s",
                    ),
                    "Open": result["o"],
                    "High": result["h"],
                    "Low": result["l"],
                    "Close": result["c"],
                    "Volume": result["v"],
                }
            )

            data["Symbol"] = symbol

            data = (
                data
                .sort_values("Date")
                .drop_duplicates(subset=["Date"])
                .reset_index(drop=True)
            )

            if data.empty:
                raise ValueError(
                    f"Finnhub returned an empty dataset for {symbol}."
                )

            return data

        except Exception as error:
            last_error = error

            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))

    raise ValueError(
        f"Could not download market data for {symbol}: {last_error}"
    )


def get_signal(probability: float) -> str:
    if probability >= DECISION_THRESHOLD + 0.15:
        return "Strong Watch"

    if probability >= DECISION_THRESHOLD:
        return "Watch"

    if probability >= DECISION_THRESHOLD - 0.10:
        return "Neutral"

    return "Low Potential"


def get_rsi_status(rsi: float) -> str:
    if rsi >= 70:
        return "Overbought"

    if rsi <= 30:
        return "Oversold"

    if rsi >= 55:
        return "Positive momentum"

    if rsi <= 45:
        return "Weak momentum"

    return "Neutral momentum"


def get_trend(
    ema_20: float,
    ema_50: float,
    ema_200: float,
) -> str:
    if ema_20 > ema_50 > ema_200:
        return "Strong bullish trend"

    if ema_20 < ema_50 < ema_200:
        return "Strong bearish trend"

    if ema_20 > ema_50:
        return "Short-term bullish trend"

    return "Mixed trend"


def analyze_stock(symbol: str) -> dict[str, Any]:
    symbol = str(symbol).upper().strip()

    try:
        raw_data = download_stock_data(symbol)

        feature_data = add_technical_features(raw_data)

        valid_rows = feature_data.dropna(
            subset=FEATURE_COLUMNS
        )

        if valid_rows.empty:
            return {
                "success": False,
                "symbol": symbol,
                "message": (
                    "Not enough historical data to calculate "
                    "all model features."
                ),
            }

        latest = valid_rows.iloc[-1]

        model_input = pd.DataFrame(
            [latest[FEATURE_COLUMNS].to_dict()],
            columns=FEATURE_COLUMNS,
        ).replace([np.inf, -np.inf], np.nan)

        if model_input.isna().any().any():
            return {
                "success": False,
                "symbol": symbol,
                "message": (
                    "The latest feature row contains invalid values."
                ),
            }

        probability = float(
            MODEL.predict_proba(model_input)[0, 1]
        )

        rsi = float(latest["RSI_14"])
        macd = float(latest["MACD"])
        macd_signal = float(latest["MACD_Signal"])
        ema_20 = float(latest["EMA_20"])
        ema_50 = float(latest["EMA_50"])
        ema_200 = float(latest["EMA_200"])

        return {
            "success": True,
            "symbol": symbol,
            "date": str(
                pd.to_datetime(latest["Date"]).date()
            ),
            "close": round(float(latest["Close"]), 2),
            "target_return_percent": round(
                TARGET_RETURN * 100,
                2,
            ),
            "prediction_horizon_days": PREDICTION_HORIZON,
            "probability_percent": round(
                probability * 100,
                2,
            ),
            "decision_threshold_percent": round(
                DECISION_THRESHOLD * 100,
                2,
            ),
            "signal": get_signal(probability),
            "rsi_14": round(rsi, 2),
            "rsi_status": get_rsi_status(rsi),
            "macd": round(macd, 4),
            "macd_signal": round(macd_signal, 4),
            "macd_status": (
                "Bullish"
                if macd > macd_signal
                else "Bearish"
            ),
            "trend": get_trend(
                ema_20,
                ema_50,
                ema_200,
            ),
            "ema_20": round(ema_20, 4),
            "ema_50": round(ema_50, 4),
            "ema_200": round(ema_200, 4),
            "atr_14": round(
                float(latest["ATR_14"]),
                4,
            ),
            "volatility_20_percent": round(
                float(latest["Volatility_20"]) * 100,
                2,
            ),
        }

    except Exception as error:
        return {
            "success": False,
            "symbol": symbol,
            "message": str(error),
        }


def compare_stocks(
    symbols: list[str],
) -> dict[str, Any]:
    clean_symbols = list(
        dict.fromkeys(
            str(symbol).upper().strip()
            for symbol in symbols
            if str(symbol).strip()
        )
    )

    if len(clean_symbols) < 2:
        return {
            "success": False,
            "message": "At least two stock symbols are required.",
        }

    if len(clean_symbols) > 5:
        return {
            "success": False,
            "message": "A maximum of five stocks can be compared.",
        }

    results = [
        analyze_stock(symbol)
        for symbol in clean_symbols
    ]

    successful = [
        result
        for result in results
        if result.get("success")
    ]

    if not successful:
        return {
            "success": False,
            "message": "No stocks could be analyzed.",
            "results": results,
        }

    ranked = sorted(
        successful,
        key=lambda item: item["probability_percent"],
        reverse=True,
    )

    return {
        "success": True,
        "comparison": ranked,
        "highest_probability_symbol": ranked[0]["symbol"],
        "failed_results": [
            result
            for result in results
            if not result.get("success")
        ],
    }


def scan_rsi(
    symbols: list[str],
    minimum_rsi: float = 26,
    maximum_rsi: float = 35,
) -> dict[str, Any]:
    if minimum_rsi < 0 or maximum_rsi > 100:
        return {
            "success": False,
            "message": "RSI values must be between 0 and 100.",
        }

    if minimum_rsi > maximum_rsi:
        return {
            "success": False,
            "message": (
                "minimum_rsi cannot be greater than maximum_rsi."
            ),
        }

    clean_symbols = list(
        dict.fromkeys(
            str(symbol).upper().strip()
            for symbol in symbols
            if str(symbol).strip()
        )
    )[:30]

    matches = []
    failures = []

    for symbol in clean_symbols:
        result = analyze_stock(symbol)

        if not result.get("success"):
            failures.append(result)
            continue

        if minimum_rsi <= result["rsi_14"] <= maximum_rsi:
            matches.append(result)

    matches = sorted(
        matches,
        key=lambda item: abs(item["rsi_14"] - 30),
    )

    return {
        "success": True,
        "minimum_rsi": minimum_rsi,
        "maximum_rsi": maximum_rsi,
        "scanned_count": len(clean_symbols),
        "match_count": len(matches),
        "matches": matches,
        "failed_count": len(failures),
    }


def find_high_probability_stocks(
    symbols: list[str],
    minimum_probability_percent: float = 45,
) -> dict[str, Any]:
    clean_symbols = list(
        dict.fromkeys(
            str(symbol).upper().strip()
            for symbol in symbols
            if str(symbol).strip()
        )
    )[:30]

    matches = []

    for symbol in clean_symbols:
        result = analyze_stock(symbol)

        if not result.get("success"):
            continue

        if (
            result["probability_percent"]
            >= minimum_probability_percent
        ):
            matches.append(result)

    matches = sorted(
        matches,
        key=lambda item: item["probability_percent"],
        reverse=True,
    )

    return {
        "success": True,
        "minimum_probability_percent": (
            minimum_probability_percent
        ),
        "scanned_count": len(clean_symbols),
        "match_count": len(matches),
        "matches": matches,
    }


def explain_indicator(
    indicator: str,
) -> dict[str, Any]:
    key = (
        str(indicator)
        .lower()
        .strip()
        .replace(" ", "_")
    )

    explanations = {
        "rsi": {
            "name": "Relative Strength Index",
            "description": (
                "RSI is a momentum indicator ranging from 0 to 100. "
                "Values near or below 30 are commonly interpreted as "
                "oversold, while values near or above 70 are commonly "
                "interpreted as overbought."
            ),
        },
        "macd": {
            "name": "Moving Average Convergence Divergence",
            "description": (
                "MACD compares two exponential moving averages. "
                "A MACD value above its signal line may indicate "
                "improving momentum, while a value below it may indicate "
                "weakening momentum."
            ),
        },
        "ema": {
            "name": "Exponential Moving Average",
            "description": (
                "EMA is a moving average that gives more weight to "
                "recent prices. Comparing short, medium and long EMAs "
                "can help describe the current trend."
            ),
        },
        "atr": {
            "name": "Average True Range",
            "description": (
                "ATR estimates recent price movement and volatility. "
                "A higher ATR means the stock has recently moved through "
                "a wider daily range."
            ),
        },
        "volatility": {
            "name": "Historical Volatility",
            "description": (
                "Historical volatility measures how much daily returns "
                "have varied over a selected rolling period."
            ),
        },
        "bollinger_bands": {
            "name": "Bollinger Bands",
            "description": (
                "Bollinger Bands place upper and lower bands around a "
                "moving average using recent standard deviation."
            ),
        },
    }

    aliases = {
        "rsi_14": "rsi",
        "relative_strength_index": "rsi",
        "moving_average_convergence_divergence": "macd",
        "exponential_moving_average": "ema",
        "average_true_range": "atr",
        "bb": "bollinger_bands",
        "bollinger": "bollinger_bands",
    }

    key = aliases.get(key, key)

    if key not in explanations:
        return {
            "success": False,
            "message": (
                f"No explanation is available for '{indicator}'."
            ),
            "available_indicators": list(explanations.keys()),
        }

    return {
        "success": True,
        "indicator": key,
        **explanations[key],
    }
