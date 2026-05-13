import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = yf.download(
    "BTC-USD",
    start="2025-01-01",
    end="2026-03-01"
)

df.columns = df.columns.get_level_values(0)

# Moving averages
df['SMA_20'] = df["Close"].rolling(20).mean()

df['SMA_50'] = df["Close"].rolling(50).mean()

df['EMA_20'] = df["Close"].ewm(span=20, adjust=False).mean()

# Daily returns
df["Returns"] = df["Close"].pct_change()

# Rolling volatility
df["Volatility"] = df["Returns"].rolling(20).std()

# Sharpe ratio
risk_free_rate = 0.0

mean_return = df["Returns"].mean()

volatility = df["Returns"].std()

sharpe_ratio = ((mean_return - risk_free_rate) / volatility) * np.sqrt(252)

print("Sharpe Ratio:", sharpe_ratio)

df.dropna(inplace=True)

# Save CSV
df.to_csv("btc_analysis.csv")

print(df.head())
plt.figure(figsize=(12,6))

plt.plot(df['Close'], label='Close Price')

plt.plot(df['EMA_20'], label='EMA 20')

plt.plot(df['SMA_20'], label='SMA 20')

plt.plot(df['SMA_50'], label='SMA 50')

plt.legend()

plt.title("BTC Price with Moving Averages")

plt.savefig("moving_avg.png")

plt.show()

plt.figure(figsize=(10,5))

plt.hist(df['Returns'].dropna(), bins=50)

plt.title("Returns Distribution")

plt.xlabel("Daily Returns")

plt.ylabel("Frequency")

plt.savefig("returns.png")

plt.show()

plt.figure(figsize=(12,5))

plt.plot(df['Volatility'])

plt.title("Rolling Volatility")

plt.savefig("rolling_volatility.png")

plt.show()

with open("report.txt", "w") as f:
    f.write("BTC Analysis Report\n")
    f.write("===================\n\n")

    f.write(f"Mean Close Price: {df['Close'].mean()}\n")
    f.write(f"Median Close Price: {df['Close'].median()}\n")
    f.write(f"Standard Deviation: {df['Close'].std()}\n")
    f.write(f"Maximum Close Price: {df['Close'].max()}\n")
    f.write(f"Minimum Close Price: {df['Close'].min()}\n")
    f.write(f"Sharpe Ratio: {sharpe_ratio}\n")