# Free Stock Rater (Buy / Strong Buy / Sell / Strong Sell)

Zero-cost, end-to-end screener that uses free Python libs:
- **yfinance** (no API key) for historical prices
- Simple technical indicators (RSI, MACD, SMA) for signals
- Runs locally or via **GitHub Actions** on a schedule

> This is **not investment advice**. It's a toy screener for educational use.

## Quickstart (Local)

1) Install Python 3.10+ and run:
```bash
pip install -r requirements.txt
```

2) Put tickers (one per line) into `config/tickers.txt`. Example provided in `config/example_tickers.txt`.

3) Run it:
```bash
python app/main.py --tickers-file config/tickers.txt --days 400 --output output/results.csv
```

4) See the CSV in `output/results.csv`.

## How it labels

We compute **SMA50**, **SMA200**, **RSI(14)**, and **MACD(12,26,9)**.
Then we classify:

- **Strong Buy**: Uptrend (SMA50 > SMA200) **and** MACD crossed up today **and** 30 ≤ RSI ≤ 60
- **Buy**: Uptrend **and** (MACD > signal **or** RSI < 35)
- **Strong Sell**: Downtrend (SMA50 < SMA200) **and** MACD crossed down today **and** 40 ≤ RSI ≤ 70
- **Sell**: Downtrend **and** (MACD < signal **or** RSI > 65)
- Otherwise: **Hold/Neutral**

Cross = signal changed side today vs yesterday.

You can tune rules in `app/strategy.py`.

## Run on GitHub Actions (optional, free)

1) Create a **public** GitHub repo, upload this folder.
2) Ensure `config/tickers.txt` exists (and is committed).
3) The included workflow `.github/workflows/screener.yml` runs **Mon–Fri at 21:00 UTC** and on manual dispatch.
4) Results land in `output/results.csv` as an artifact + push (commit) back to the repo.

> If you prefer private repos: Actions is still free for small runs, but check your account's minutes.

## Example usage

```bash
python app/main.py --tickers AAPL MSFT NVDA TSLA AMZN --output output/results.csv
```

## Notes

- yfinance is unofficial and can break when upstream changes. If you prefer a key-based API, swap in Alpha Vantage/Finnhub easily.
- Technical signals are noisy. Treat this as a screening input, not a decision engine.
