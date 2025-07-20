

# 🌍 QuantFolio

A Streamlit-based web app for tracking your global investment portfolio with real-time valuations, currency-aware performance, split-adjusted prices, and XIRR analytics.



## ✨ Features

* 📈 Daily portfolio valuation across multiple currencies (USD, INR, SGD)
* 🔄 Auto-adjusts for stock splits
* 💹 Computes XIRR (Extended Internal Rate of Return) for investment performance
* 💰 Fetches real-time prices using Yahoo Finance
* 🔃 Live currency conversion using historical FX rates
* 📊 Interactive charts and summary tables for holdings
* 📁 Upload and analyze your own transaction data

---

## 📂 Folder Structure

```
project-root/
├── app.py                    # Main Streamlit app
├── data/
│   └── adjusted_transactions.csv
│   └── currency_rates_july2023_july2025.csv
├── utils/
│   └── xirr_calculator.py
│   └── adjust_transactions.py
├── requirements.txt
└── README.md
```

---

## 🏗️ How It Works

1. Upload or load your transactions (symbol, date, quantity, price, currency).
2. Transactions are adjusted for splits.
3. Daily FX rates are loaded for USD/INR and USD/SGD.
4. Split-adjusted prices are fetched from Yahoo Finance.
5. Daily holdings are calculated.
6. Portfolio is valued in USD, INR, and SGD.
7. XIRR is computed per asset class.

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/portfolio-tracker.git
cd portfolio-tracker
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
streamlit run app.py
```

---

## 🧪 Sample CSV Format

`adjusted_transactions.csv`:

| Date       | Symbol  | Quantity | Price | Currency |
| ---------- | ------- | -------- | ----- | -------- |
| 2023-07-01 | AAPL    | 5        | 180   | USD      |
| 2023-08-12 | INFY.NS | 10       | 1450  | INR      |

---

## 🛠️ Built With

* [Streamlit](https://streamlit.io)
* [Pandas](https://pandas.pydata.org/)
* [yFinance](https://pypi.org/project/yfinance/)
* [Matplotlib / Altair](https://altair-viz.github.io/)
* [NumPy](https://numpy.org/)

---

## 📜 License

MIT License
