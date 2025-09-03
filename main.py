import argparse
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf
from pathlib import Path

from strategy import rsi, macd, label_signal

def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['SMA50'] = df['Close'].rolling(50).mean()
    df['SMA200'] = df['Close'].rolling(200).mean()
    df['RSI'] = rsi(df['Close'], 14)
    macd_line, signal_line, hist = macd(df['Close'], 12, 26, 9)
    df['MACD'] = macd_line
    df['MACD_signal'] = signal_line
    df['MACD_hist'] = hist
    return df

def fetch_history(ticker: str, days: int = 450) -> pd.DataFrame:
    period_days = max(days, 250)  # need enough for SMA200
    df = yf.download(ticker, period=f"{period_days}d", interval="1d", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        # yfinance sometimes returns multi-index for multiple tickers; ensure single
        df.columns = [c[0] for c in df.columns]
    return df.dropna(how="all")

def run(tickers, days: int, output_path: str):
    records = []
    for t in tickers:
        try:
            df = fetch_history(t, days=days)
            if df.empty:
                records.append({'ticker': t, 'status': 'no_data'})
                continue
            df = compute_indicators(df).dropna()
            label = label_signal(df)
            last = df.iloc[-1]
            records.append({
                'ticker': t,
                'as_of_date': df.index[-1].date().isoformat(),
                'last_close': round(float(last['Close']), 4),
                'sma50': round(float(last['SMA50']), 4),
                'sma200': round(float(last['SMA200']), 4),
                'rsi14': round(float(last['RSI']), 2),
                'macd': round(float(last['MACD']), 4),
                'macd_signal': round(float(last['MACD_signal']), 4),
                'label': label,
                'status': 'ok'
            })
        except Exception as e:
            records.append({'ticker': t, 'status': f'error: {e}'})

    out_df = pd.DataFrame(records)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)
    print(f"Wrote {output_path}")
    return out_df

def load_tickers(args) -> list:
    if args.tickers:
        return [t.strip().upper() for t in args.tickers]
    if args.tickers_file:
        with open(args.tickers_file) as f:
            return [line.strip().upper() for line in f if line.strip() and not line.startswith('#')]
    raise SystemExit("Provide --tickers or --tickers-file")

def parse_args():
    p = argparse.ArgumentParser(description="Free stock rater (Buy / Strong Buy / Sell / Strong Sell)")
    p.add_argument("--tickers", nargs="*", help="Space-separated tickers, e.g., AAPL MSFT NVDA")
    p.add_argument("--tickers-file", help="Path to a file with one ticker per line")
    p.add_argument("--days", type=int, default=450, help="How many days of history to fetch")
    p.add_argument("--output", default="output/results.csv", help="CSV output path")
    return p.parse_args()

if __name__ == "__main__":
    args = parse_args()
    tickers = load_tickers(args)
    run(tickers, days=args.days, output_path=args.output)
