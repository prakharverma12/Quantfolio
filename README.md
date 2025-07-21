

# 🌍 QuantFolio

A Streamlit-based web app for tracking your global investment portfolio with real-time valuations, currency-aware performance, split-adjusted prices, and XIRR analytics.
<img width="794" height="708" alt="image" src="https://github.com/user-attachments/assets/54dccfa2-a6ad-43e3-8467-8e83a031ef7f" />


<img width="1022" height="671" alt="image" src="https://github.com/user-attachments/assets/2fca523d-8cd3-483a-9e99-8ce2390ccd6b" />


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
portfolio-tracker/
├── app.py                        # Streamlit app for portfolio visualization
├── main.py                       # Script entry point (if needed)
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation

├── data/                         # Input data files
│   ├── currency_rates_july2023_july2025.csv
│   ├── Stock_trading_2023.csv
│   ├── Stock_trading_2024.csv
│   └── Stock_trading_2025.csv

├── utils/                        # Utility modules
│   ├── currency_converter.py     # Currency conversion logic
│   ├── data_loader.py            # Handles loading & merging trading data
│   ├── split_adjuster.py         # Adjusts for stock splits
│   └── xirr_calculator.py        # Calculates XIRR of portfolio

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
