
import streamlit as st
import pandas as pd
from utils.data_loader import load_transaction_files
from utils.split_adjuster import adjust_transactions_for_splits
from utils.currency_converter import convert_currency
from utils.xirr_calculator import compute_xirr

import yfinance as yf
from datetime import datetime


files = load_transaction_files(['data/Stock_trading_2023.csv', 'data/Stock_trading_2024.csv', 'data/Stock_trading_2023.csv'])

# --- 1. Load Currency Rates ---
def get_daily_currency_rates(start_date, end_date):
    usd_inr = yf.download("INR=X", start=start_date, end=end_date)[['Close']].rename(columns={'Close': 'USD_INR'})
    usd_sgd = yf.download("SGD=X", start=start_date, end=end_date)[['Close']].rename(columns={'Close': 'USD_SGD'})
    fx = usd_inr.join(usd_sgd, how='outer')
    fx.index.name = 'Date'
    return fx.reset_index()

# --- 2. Load Split-Adjusted Prices ---
def get_split_adjusted_prices(symbols, start_date, end_date):
    price_data = pd.DataFrame()
    
    for sym in symbols:
        data = yf.download(sym, start=start_date, end=end_date)  # auto_adjust=True by default
        if data.empty:
            print(f"Warning: No data found for {sym}")
            continue

        if 'Close' in data.columns:
            price_data[sym] = data['Close']
        else:
            print(f"Warning: 'Close' column not found for {sym}")

    return price_data

# --- 3. Compute Daily Holdings ---
def compute_daily_holdings(transactions):
    transactions = transactions.copy()
    
    # Ensure datetime and column rename
    if 'Date/Time' in transactions.columns:
        transactions['Date'] = pd.to_datetime(transactions['Date/Time']).dt.normalize()
    elif 'Date' in transactions.columns:
        transactions['Date'] = pd.to_datetime(transactions['Date']).dt.normalize()
    else:
        raise KeyError("No 'Date' or 'Date/Time' column found in transactions")

    grouped = transactions.groupby(['Date', 'Symbol'])['Quantity'].sum().unstack(fill_value=0)
    holdings = grouped.cumsum()
    return holdings

# --- 4. Compute Portfolio Value ---
def compute_portfolio_value(holdings, daily_prices, fx_rates):
    # Compute total USD value per day
    # Flatten MultiIndex columns
    fx_rates.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in fx_rates.columns]

    portfolio_usd = (holdings * daily_prices).sum(axis=1).to_frame('USD')
    portfolio_usd.index.name = 'Date'  # explicitly name the index for clarity
    print("fx_rates.columns:", fx_rates.columns)
    print("fx_rates.index:", fx_rates.index)

    # Fix fx_rates: remove multiindex if present
    if isinstance(fx_rates.columns, pd.MultiIndex):
        fx_rates.columns = fx_rates.columns.get_level_values(-1)

    if isinstance(fx_rates.index, pd.MultiIndex):
        fx_rates = fx_rates.reset_index()

    # Ensure proper datetime index for fx_rates
    fx_rates['Date'] = pd.to_datetime(fx_rates['Date_'])
    fx_rates = fx_rates.drop_duplicates(subset='Date')
    fx_rates = fx_rates.set_index('Date')

    # Align indices before joining
    fx_rates = fx_rates.reindex(portfolio_usd.index)
    fx_rates.rename(columns={
    'USD_INR_INR=X': 'USD_INR',
    'USD_SGD_SGD=X': 'USD_SGD'
    }, inplace=True)

    print("portfolio_rates.columns:", portfolio_usd.columns)
    # Final join and currency conversion
    portfolio = portfolio_usd.join(fx_rates, how='left', rsuffix='_fx')
    portfolio['INR'] = portfolio['USD'] * portfolio['USD_INR']
    portfolio['SGD'] = portfolio['USD'] * portfolio['USD_SGD']

    return portfolio.dropna()


# --- Main App ---
st.title("📊 QuantFolio")
transactions = load_transaction_files(['data/Stock_trading_2023.csv', 'data/Stock_trading_2024.csv', 'data/Stock_trading_2023.csv'])
# Sample Data (Replace with actual loader)
adj_df = adjust_transactions_for_splits(transactions)
adj_df['Date/Time'] = pd.to_datetime(adj_df['Date/Time']).dt.date
symbols = adj_df['Symbol'].unique().tolist()

start_date = adj_df['Date/Time'].min()
end_date = datetime.today().date()

# FX Rates
st.write("Loading FX Rates...")
fx_rates = get_daily_currency_rates(start_date, end_date)

# Prices
st.write("Loading Split-Adjusted Prices...")
daily_prices = get_split_adjusted_prices(symbols, start_date, end_date)
daily_prices.index = pd.to_datetime(daily_prices.index.date)

# Holdings
holdings = compute_daily_holdings(adj_df)
holdings.index = pd.to_datetime(holdings.index)

# Align indexes
daily_prices = daily_prices.reindex(holdings.index).fillna(method='ffill')
fx_rates = fx_rates[fx_rates['Date'].isin(holdings.index)]

# Portfolio Value
portfolio = compute_portfolio_value(holdings, daily_prices, fx_rates)

latest_date = holdings.index.max()
latest_holdings = holdings.loc[latest_date]
latest_holdings = latest_holdings[latest_holdings != 0]  # Filter zero-quantity stocks

master_df = latest_holdings.reset_index()
master_df.columns = ['Symbol', 'Quantity']
master_df = master_df.sort_values(by='Symbol')
# --- Display Results ---
st.subheader("📄 Master List of Holdings")
st.dataframe(master_df.style.format({"Quantity": "{:.2f}"}))
# --- 5. Compute Current Price and Total Value ---
st.subheader("💰 Current Portfolio Value")

# 1. Get current prices using Yahoo Finance API
symbols_list = master_df['Symbol'].tolist()
tickers = yf.Tickers(' '.join(symbols_list))
current_prices = {sym: tickers.tickers[sym].info.get('regularMarketPrice') for sym in symbols_list}

# 2. Merge prices with master holdings
master_df['Current Price (USD)'] = master_df['Symbol'].map(current_prices)
master_df['Value (USD)'] = master_df['Quantity'] * master_df['Current Price (USD)']

# 3. Latest FX Rates
latest_fx = fx_rates[fx_rates['Date'] == latest_date].iloc[0]
print("latest fx :", latest_fx)

usd_inr = latest_fx['USD_INR_INR=X']
usd_sgd = latest_fx['USD_SGD_SGD=X']

# 4. Convert to INR and SGD
master_df['Value (INR)'] = master_df['Value (USD)'] * usd_inr
master_df['Value (SGD)'] = master_df['Value (USD)'] * usd_sgd

# 5. Show updated master with prices and value
st.dataframe(master_df.style.format({
    "Quantity": "{:.2f}",
    "Current Price (USD)": "${:.2f}",
    "Value (USD)": "${:.2f}",
    "Value (INR)": "₹{:.2f}",
    "Value (SGD)": "S${:.2f}"
}))

# 6. Show total portfolio value
total_usd = master_df['Value (USD)'].sum()
total_inr = master_df['Value (INR)'].sum()
total_sgd = master_df['Value (SGD)'].sum()

st.markdown(f"### 📈 Total Portfolio Value")
st.markdown(f"- **USD:** ${total_usd:,.2f}")
st.markdown(f"- **INR:** ₹{total_inr:,.2f}")
st.markdown(f"- **SGD:** S${total_sgd:,.2f}")
print(portfolio)

if not files.empty:
    df = files
    adj_df = adjust_transactions_for_splits(df)
    converted = convert_currency(adj_df, 'data/currency_rates_july2023_july2025.csv')
    xirr_vals = compute_xirr(converted)

    st.subheader("📈 XIRR Results")

    # Format as percentage and display in a styled table
    xirr_df = pd.DataFrame(xirr_vals.items(), columns=['Symbol', 'XIRR'])
    xirr_df['XIRR'] = xirr_df['XIRR'] * 100  # Convert to percentage

    st.dataframe(
        xirr_df.style.format({'XIRR': '{:.2f}%'}).set_properties(**{
            'text-align': 'center'
        }).set_table_styles([{
            'selector': 'th',
            'props': [('text-align', 'center')]
        }])
    )
import altair as alt

# Reset index for plotting
portfolio_reset = portfolio.reset_index().rename(columns={'index': 'Date'})

st.subheader("📅 Daily Portfolio Value (USD)")
usd_chart = alt.Chart(portfolio_reset).mark_line().encode(
    x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m', labelAngle=-45)),
    y=alt.Y('USD:Q', title='USD Value')
).properties(width=700, height=300)

st.altair_chart(usd_chart, use_container_width=True)

st.subheader("📅 Daily Portfolio Value (INR)")
inr_chart = alt.Chart(portfolio_reset).mark_line().encode(
    x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m', labelAngle=-45)),
    y=alt.Y('INR:Q', title='INR Value')
).properties(width=700, height=300)
st.altair_chart(inr_chart, use_container_width=True)

st.subheader("📅 Daily Portfolio Value (SGD)")
sgd_chart = alt.Chart(portfolio_reset).mark_line().encode(
    x=alt.X('Date:T', title='Date', axis=alt.Axis(format='%Y-%m', labelAngle=-45)),
    y=alt.Y('SGD:Q', title='SGD Value')
).properties(width=700, height=300)
st.altair_chart(sgd_chart, use_container_width=True)