import numpy as np
import pandas as pd

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / (loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi

def macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def label_signal(df: pd.DataFrame) -> str:
    # Expects columns: Close, SMA50, SMA200, RSI, MACD, MACD_signal
    if df.empty or len(df) < 2:
        return "Insufficient Data"

    last = df.iloc[-1]
    prev = df.iloc[-2]

    uptrend = last['SMA50'] > last['SMA200']
    downtrend = last['SMA50'] < last['SMA200']

    macd_cross_up = (prev['MACD'] <= prev['MACD_signal']) and (last['MACD'] > last['MACD_signal'])
    macd_cross_down = (prev['MACD'] >= prev['MACD_signal']) and (last['MACD'] < last['MACD_signal'])

    # Strong Buy
    if uptrend and macd_cross_up and (30 <= last['RSI'] <= 60):
        return "Strong Buy"
    # Buy
    if uptrend and (last['MACD'] > last['MACD_signal'] or last['RSI'] < 35):
        return "Buy"
    # Strong Sell
    if downtrend and macd_cross_down and (40 <= last['RSI'] <= 70):
        return "Strong Sell"
    # Sell
    if downtrend and (last['MACD'] < last['MACD_signal'] or last['RSI'] > 65):
        return "Sell"

    return "Hold/Neutral"
