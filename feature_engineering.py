
import numpy as np
import pandas as pd


def calculate_rsi(series, period=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    avg_loss = loss.ewm(
        alpha=1 / period,
        adjust=False,
        min_periods=period
    ).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))


def add_technical_features(stock_df):
    required_columns = {
        "Date",
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    }

    missing_columns = (
        required_columns - set(stock_df.columns)
    )

    if missing_columns:
        raise ValueError(
            f"Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    stock_df = stock_df.copy()

    stock_df["Date"] = pd.to_datetime(
        stock_df["Date"],
        errors="coerce"
    )

    numeric_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume"
    ]

    for column in numeric_columns:
        stock_df[column] = pd.to_numeric(
            stock_df[column],
            errors="coerce"
        )

    stock_df = (
        stock_df
        .dropna(
            subset=[
                "Date",
                "Open",
                "High",
                "Low",
                "Close",
                "Volume"
            ]
        )
        .sort_values("Date")
        .drop_duplicates(subset=["Date"])
        .reset_index(drop=True)
    )

    stock_df["Daily_Return"] = (
        stock_df["Close"].pct_change()
    )

    stock_df["Volume_Change"] = (
        stock_df["Volume"].pct_change()
    )

    stock_df["SMA_20"] = (
        stock_df["Close"]
        .rolling(window=20)
        .mean()
    )

    stock_df["SMA_50"] = (
        stock_df["Close"]
        .rolling(window=50)
        .mean()
    )

    stock_df["SMA_200"] = (
        stock_df["Close"]
        .rolling(window=200)
        .mean()
    )

    stock_df["EMA_20"] = (
        stock_df["Close"]
        .ewm(span=20, adjust=False)
        .mean()
    )

    stock_df["EMA_50"] = (
        stock_df["Close"]
        .ewm(span=50, adjust=False)
        .mean()
    )

    stock_df["EMA_200"] = (
        stock_df["Close"]
        .ewm(span=200, adjust=False)
        .mean()
    )

    stock_df["RSI_14"] = calculate_rsi(
        stock_df["Close"],
        period=14
    )

    ema_12 = (
        stock_df["Close"]
        .ewm(span=12, adjust=False)
        .mean()
    )

    ema_26 = (
        stock_df["Close"]
        .ewm(span=26, adjust=False)
        .mean()
    )

    stock_df["MACD"] = ema_12 - ema_26

    stock_df["MACD_Signal"] = (
        stock_df["MACD"]
        .ewm(span=9, adjust=False)
        .mean()
    )

    stock_df["MACD_Histogram"] = (
        stock_df["MACD"]
        - stock_df["MACD_Signal"]
    )

    rolling_mean = (
        stock_df["Close"]
        .rolling(window=20)
        .mean()
    )

    rolling_std = (
        stock_df["Close"]
        .rolling(window=20)
        .std()
    )

    stock_df["BB_Middle"] = rolling_mean

    stock_df["BB_Upper"] = (
        rolling_mean + 2 * rolling_std
    )

    stock_df["BB_Lower"] = (
        rolling_mean - 2 * rolling_std
    )

    stock_df["BB_Width"] = (
        stock_df["BB_Upper"]
        - stock_df["BB_Lower"]
    ) / stock_df["BB_Middle"]

    previous_close = stock_df["Close"].shift(1)

    true_range = pd.concat(
        [
            stock_df["High"] - stock_df["Low"],
            (
                stock_df["High"]
                - previous_close
            ).abs(),
            (
                stock_df["Low"]
                - previous_close
            ).abs()
        ],
        axis=1
    ).max(axis=1)

    stock_df["ATR_14"] = (
        true_range
        .rolling(window=14)
        .mean()
    )

    stock_df["Volatility_20"] = (
        stock_df["Daily_Return"]
        .rolling(window=20)
        .std()
    )

    stock_df["Price_to_SMA20"] = (
        stock_df["Close"]
        / stock_df["SMA_20"]
    )

    stock_df["Price_to_SMA50"] = (
        stock_df["Close"]
        / stock_df["SMA_50"]
    )

    stock_df["Price_to_EMA20"] = (
        stock_df["Close"]
        / stock_df["EMA_20"]
    )

    stock_df["EMA20_to_EMA50"] = (
        stock_df["EMA_20"]
        / stock_df["EMA_50"]
    )

    stock_df = stock_df.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return stock_df
