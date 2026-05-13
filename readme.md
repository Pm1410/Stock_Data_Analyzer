# 📊 Stock Data Analyzer — BTC/USD

A Python tool that downloads real Bitcoin price data and calculates key financial indicators used in quantitative analysis — moving averages, daily returns, rolling volatility, and Sharpe ratio.

---



## ⚙️ How to Run

```bash
pip install -r requirements.txt
python main.py
```

**requirements.txt**
```
yfinance==0.2.38
pandas==2.1.0
numpy==1.26.0
matplotlib==3.8.0
```

---

## 📈 Sample Output

![Moving Averages](outputs/moving_avg.png)

```
BTC Analysis Report
===================
Mean Close Price:    87432.21
Median Close Price:  85610.44
Standard Deviation:  12043.87
Maximum Close Price: 109114.88
Minimum Close Price: 76453.12
Sharpe Ratio:        1.847
```

---

## 🧠 Concepts & Formulas Explained

Every calculation in this project explained from scratch.

---

### 1. Simple Moving Average (SMA)

**What it is:**
The average of the last N closing prices. Recalculated at every new data point by dropping the oldest value and adding the newest. This smooths out noise in the price data and reveals the underlying trend direction.

**Formula:**

```
SMA(N) at time t = (Close[t] + Close[t-1] + Close[t-2] + ... + Close[t-N+1]) / N
```

**Example — SMA(3) on 5 days of data:**
```
Prices:  100, 102, 98, 105, 110

Day 3:   SMA = (100 + 102 + 98)  / 3 = 100.0
Day 4:   SMA = (102 + 98  + 105) / 3 = 101.7
Day 5:   SMA = (98  + 105 + 110) / 3 = 104.3
```

**In code:**
```python
df['SMA_20'] = df["Close"].rolling(20).mean()
df['SMA_50'] = df["Close"].rolling(50).mean()
```

**Why two SMAs (20 and 50)?**
- SMA_20 reacts faster — it uses fewer days, so it tracks recent price action more closely
- SMA_50 is slower — it uses more days, so it shows the longer-term trend
- When SMA_20 crosses **above** SMA_50 → prices are accelerating upward → potential buy signal (Golden Cross)
- When SMA_20 crosses **below** SMA_50 → prices are slowing down → potential sell signal (Death Cross)

**Limitation:**
SMA lags the actual price — it always looks backward. By the time it signals a trend, part of the move has already happened.

---

### 2. Exponential Moving Average (EMA)

**What it is:**
Like SMA but gives more weight to recent prices and less weight to older prices. This makes it react faster to price changes than SMA.

**Formula:**

```
EMA(today) = alpha × Close(today) + (1 - alpha) × EMA(yesterday)

where:
alpha = 2 / (N + 1)

For N = 20:
alpha = 2 / (20 + 1) = 0.0952
```

This means today's price gets ~9.5% weight, yesterday's EMA gets ~90.5% weight.

**Example — EMA(3) on 5 days:**
```
alpha = 2 / (3 + 1) = 0.5

Prices:  100, 102, 98, 105, 110

Day 1:   EMA = 100  (seed value — first EMA = first price)
Day 2:   EMA = 0.5 × 102 + 0.5 × 100 = 101.0
Day 3:   EMA = 0.5 × 98  + 0.5 × 101 = 99.5
Day 4:   EMA = 0.5 × 105 + 0.5 × 99.5 = 102.25
Day 5:   EMA = 0.5 × 110 + 0.5 × 102.25 = 106.13
```

**In code:**
```python
df['EMA_20'] = df["Close"].ewm(span=20, adjust=False).mean()
```
`span=20` sets N=20, `adjust=False` uses the recursive formula above.

**SMA vs EMA — when to use which:**

| | SMA | EMA |
|--|-----|-----|
| Reacts to recent prices | Slowly | Quickly |
| Smoothness | Smoother | More jagged |
| Good for | Identifying long-term trends | Catching trend changes faster |
| Used in | Support/resistance levels | MACD indicator |

---

### 3. Daily Returns

**What it is:**
The percentage change in price from one day to the next. This is the most fundamental measure in finance — we work with returns rather than raw prices because returns are comparable across assets and time periods.

**Formula:**

```
Return(t) = (Close(t) - Close(t-1)) / Close(t-1)

Equivalently:
Return(t) = Close(t) / Close(t-1) - 1
```

**Example:**
```
Monday Close:    $80,000
Tuesday Close:   $84,000

Return = (84,000 - 80,000) / 80,000 = 0.05 = +5%

Wednesday Close: $79,800
Return = (79,800 - 84,000) / 84,000 = -0.05 = -5%
```

**In code:**
```python
df["Returns"] = df["Close"].pct_change()
```
`pct_change()` does exactly this formula. The first row is NaN because there's no previous day.

**Why returns instead of prices?**
- Prices are not comparable: a $1 move in a $10 stock is 10%, a $1 move in a $1000 stock is 0.1%
- Returns are scale-independent — they represent the same thing across all assets
- Returns are roughly stationary (their statistical properties don't change over time), prices are not
- All risk metrics (Sharpe, volatility) are calculated using returns, not prices

---

### 4. Rolling Volatility

**What it is:**
The standard deviation of daily returns calculated over a rolling window of N days. Measures how wildly prices are moving — high volatility means large unpredictable swings, low volatility means calm, steady movement.

**Formula:**

```
Volatility(t) = std(Returns[t], Returns[t-1], ..., Returns[t-N+1])

std = sqrt( (1/(N-1)) × sum( (r_i - mean_r)^2 ) )
```

Where `mean_r` is the mean return over the N-day window.

**Example — Rolling Volatility with N=3:**
```
Returns:  +2%, -1%, +3%, -4%, +1%

Day 3 vol = std(+2%, -1%, +3%)
  mean = (2 - 1 + 3) / 3 = 1.33%
  variance = ((2-1.33)^2 + (-1-1.33)^2 + (3-1.33)^2) / 2
           = (0.45 + 5.43 + 2.79) / 2 = 4.33
  std = sqrt(4.33) = 2.08%

Day 4 vol = std(-1%, +3%, -4%) → recalculated on new window
```

**In code:**
```python
df["Volatility"] = df["Returns"].rolling(20).std()
```

**How to read it:**
- Volatility spike → market uncertainty, large moves, often around news events
- Volatility low → calm market, prices moving in tight range
- Bitcoin typically has much higher volatility than stocks (daily std of 3-5% vs 0.5-1% for S&P 500)
- Volatility clusters — high volatility tends to be followed by more high volatility (this is a real statistical property called volatility clustering)

---

### 5. Sharpe Ratio

**What it is:**
The single most important number for evaluating a strategy or asset. It measures how much return you're getting per unit of risk you're taking. A higher Sharpe means you're being compensated well for the risk you're bearing.

**Formula:**

```
Sharpe Ratio = (Mean Return - Risk-Free Rate) / Standard Deviation of Returns

Using daily returns, annualised:
Sharpe = ((mean_daily_return - daily_risk_free_rate) / std_daily_return) × sqrt(252)
```

`sqrt(252)` annualises it — there are 252 trading days in a year.

**Why sqrt(252)?**

```
Annualised mean return   = mean_daily × 252
Annualised std           = std_daily  × sqrt(252)   ← std scales with sqrt of time, not time

Sharpe = (mean_daily × 252) / (std_daily × sqrt(252))
       = (mean_daily / std_daily) × (252 / sqrt(252))
       = (mean_daily / std_daily) × sqrt(252)
```

**In code:**
```python
risk_free_rate = 0.0   # treating risk-free rate as 0 (simplification)
mean_return    = df["Returns"].mean()
volatility     = df["Returns"].std()
sharpe_ratio   = ((mean_return - risk_free_rate) / volatility) * np.sqrt(252)
```

**Example calculation:**
```
Suppose:
  mean daily return = 0.001  (0.1% per day)
  std daily return  = 0.03   (3% per day — typical for BTC)

Sharpe = (0.001 / 0.03) × sqrt(252)
       = 0.0333 × 15.87
       = 0.53
```

**How to interpret Sharpe ratio:**

| Sharpe | Interpretation |
|--------|----------------|
| < 0 | Losing money after risk adjustment — bad |
| 0 – 0.5 | Barely worth it |
| 0.5 – 1.0 | Acceptable |
| 1.0 – 2.0 | Good — solid risk-adjusted returns |
| 2.0 – 3.0 | Very good — hard to achieve consistently |
| > 3.0 | Exceptional — or the strategy has a bug |

**Limitations of Sharpe ratio:**
- Assumes returns are normally distributed — crypto returns have fat tails (extreme events happen more often than normal distribution predicts)
- Penalises upside volatility the same as downside — a strategy that occasionally makes huge gains gets penalised even though that's not "bad" risk
- Can be manipulated by smoothing returns or selecting a favourable time window
- This is why Sortino ratio (penalises only downside volatility) is often used alongside it

---

### 6. Returns Distribution

**What it is:**
A histogram showing how frequently different return values occurred. Tells you whether returns are symmetric, skewed, or have extreme outliers.

**In code:**
```python
plt.hist(df['Returns'].dropna(), bins=50)
```

**What to look for:**
- A bell-curve shape suggests returns are roughly normally distributed
- A fat-tailed distribution (more extreme values than the bell curve would predict) is typical for crypto
- Negative skew (long left tail) means occasional large losses — dangerous for a trading strategy
- Positive skew (long right tail) means occasional large gains — preferred

**Normal distribution properties (the 68-95-99.7 rule):**
```
If returns are normally distributed with mean μ and std σ:

68% of returns fall within μ ± 1σ
95% of returns fall within μ ± 2σ
99.7% of returns fall within μ ± 3σ

For BTC with std ≈ 3%:
68% of daily moves are within ±3%
95% of daily moves are within ±6%
Only 0.3% of days should have moves larger than ±9%

In reality BTC has more ±9% days than the normal distribution predicts.
This is called "fat tails" and is why risk models that assume normality underestimate real risk.
```

---

## 📊 Charts Explained

### Chart 1 — Price with Moving Averages (`moving_avg.png`)

Shows Close price, EMA_20, SMA_20, SMA_50 on the same chart.

**What to observe:**
- EMA_20 tracks Close price most closely — most responsive
- SMA_20 is slightly smoother and lags slightly more
- SMA_50 is the smoothest and slowest — shows the big trend
- When price is above all MAs → bullish trend
- When price is below all MAs → bearish trend
- When SMA_20 crosses SMA_50 → potential trend change signal

---

### Chart 2 — Returns Distribution (`returns.png`)

Histogram of all daily returns.

**What to observe:**
- How centred around zero is it?
- Is the tail on the left (losses) longer than the right? That's negative skew.
- How wide is the distribution? Wider = more volatile asset

---

### Chart 3 — Rolling Volatility (`rolling_volatility.png`)

Shows 20-day rolling standard deviation of returns over time.

**What to observe:**
- Spikes in volatility correspond to major market events (crashes, rallies)
- Extended periods of low volatility often precede a big move (volatility compression)
- Compare periods — is BTC more or less volatile recently compared to a year ago?

---

## 💡 What I Learned

- Why we work with returns instead of raw prices — scale independence and stationarity
- How exponential weighting works in EMA — recent data gets more weight through a decay factor
- Why annualising Sharpe uses `sqrt(252)` — variance scales linearly with time, std scales with the square root
- How volatility clustering appears in real data — high volatility begets more high volatility
- Lookahead bias in rolling calculations — `rolling(20).mean()` on day 10 only uses 10 data points, not future data, which is correct behaviour
- Why fat tails matter — real return distributions have more extreme events than a normal distribution predicts

---

## 🔧 What I Would Improve

- Add RSI (Relative Strength Index) as a momentum indicator
- Add Bollinger Bands to identify overbought/oversold conditions
- Calculate Sortino ratio alongside Sharpe — it only penalises downside volatility
- Add maximum drawdown calculation — the largest peak-to-trough decline
- Compare BTC to a second asset (ETH or S&P 500) to see correlation
- Add statistical significance test — is the Sharpe ratio high because of skill or luck?

---

## 🎯 Interview Questions From This Project

**Q: Why do we multiply by sqrt(252) when annualising the Sharpe ratio?**

A: Because variance scales linearly with time but standard deviation (volatility) scales with the square root of time. If daily variance is σ², annual variance is 252σ², so annual std is σ√252. The mean scales linearly: annual mean = 252 × daily mean. So annual Sharpe = (252 × daily_mean) / (σ√252) = (daily_mean / σ) × √252.

**Q: Why use returns instead of raw prices for volatility calculations?**

A: Raw prices are non-stationary — their statistical properties change over time as the price level changes. A $100 move means something completely different at a price of $1000 vs $100,000. Returns are scale-independent and roughly stationary, making them comparable across time and assets.

**Q: What does a Sharpe ratio of 1.5 mean?**

A: For every unit of risk taken (as measured by return volatility), the asset returned 1.5 units of excess return above the risk-free rate. In practical terms, it means the risk-adjusted returns are good — most actively managed funds struggle to maintain Sharpe above 1.0 over long periods.

**Q: What is a limitation of using SMA as a trading signal?**

A: SMA is a lagging indicator — it always looks backward. By the time a crossover signal fires, a significant portion of the price move has already happened. It also generates false signals in choppy, sideways markets where prices oscillate around the moving average without establishing a real trend.
