
import streamlit as st
import pandas as pd
from utils.data_loader import load_transaction_files
from utils.split_adjuster import adjust_transactions_for_splits
from utils.currency_converter import convert_currency
from utils.xirr_calculator import compute_xirr
from utils.portfolio import get_daily_currency_rates, get_split_adjusted_prices, compute_daily_holdings, compute_portfolio_value, get_currency_for_tickers
import yfinance as yf
from datetime import datetime
import altair as alt

files = load_transaction_files(['data/Stock_trading_2023.csv', 'data/Stock_trading_2024.csv', 'data/Stock_trading_2023.csv'])
files['Quantity'] = files['Quantity'].astype(str).str.replace(',', '')
print("MAX C6L.SI IN FILES: ", files[files['Symbol'] == 'C6L.SI']['Quantity'].max())
portfolio = pd.DataFrame()
def title():
    # --- Main App ---
    st.title("📊 QuantFolio")
def holdings():
    adj_df = adjust_transactions_for_splits(files)
    adj_df['Date/Time'] = pd.to_datetime(adj_df['Date/Time']).dt.date
    print("MAX C6L.SI IN ADJ DF:", adj_df[adj_df['Symbol'] == 'C6L.SI']['Quantity'].max())
    symbols = adj_df['Symbol'].unique().tolist()

    start_date = adj_df['Date/Time'].min()
    end_date = datetime.today().date()

    # FX Rates
    st.write("Loading FX Rates...")
    fx_rates = get_daily_currency_rates(start_date, end_date)
    fx_rates['Date'] = pd.to_datetime(fx_rates['Date'])
    fx_rates = fx_rates.set_index('Date')

    # Prices
    st.write("Loading Split-Adjusted Prices...")
    daily_prices = get_split_adjusted_prices(symbols, start_date, end_date)
    daily_prices.index = pd.to_datetime(daily_prices.index)

    # Holdings
    holdings = compute_daily_holdings(adj_df)
    holdings.index = pd.to_datetime(holdings.index)
    print("Holdings DataFrame:", holdings.columns)
    print("Holdings DataFrame:", holdings.head())
    print("c6l holdings:", holdings['C6L.SI'].max())
    # Align prices and FX rates
    daily_prices = daily_prices.reindex(holdings.index).fillna(method='ffill')
    fx_rates = fx_rates.reindex(holdings.index).fillna(method='ffill')

    # Get currency for each ticker
    st.write("Determining currencies per ticker...")
    currency_map = get_currency_for_tickers(symbols)

    # Convert all prices to USD
    prices_usd = pd.DataFrame(index=daily_prices.index)
    print("\n\nfx_rates index:", fx_rates.index)
    print("\n\ndaily_prices columns:", daily_prices.columns)
    print(daily_prices.head())
    
    for sym in symbols:
        #print(type(daily_prices[sym]), type(fx_rates['USD_SGD']))
        cur = currency_map.get(sym, 'USD')
        print(cur)
        if cur == 'SGD':
            fx_usd_sgd = fx_rates[('USD_SGD', 'SGD=X')]  # This gives a Series: fx_rates.loc[:, ('USD_SGD', 'SGD=X')]
            prices_usd[sym] = daily_prices[sym] / fx_usd_sgd
        elif cur == 'INR':
            fx_usd_inr = fx_rates[('USD_INR', 'INR=X')]  # This gives a Series: fx_rates.loc[:, ('USD_SGD', 'SGD=X')]
            prices_usd[sym] = daily_prices[sym] / fx_usd_inr
        else:
            prices_usd[sym] = daily_prices[sym]  # Already in USD

    # Compute portfolio value in USD
    latest_date = holdings.index.max()
    latest_holdings = holdings.loc[latest_date]
    latest_holdings = latest_holdings[latest_holdings != 0]
    
    portfolio_usd = (holdings * prices_usd).sum(axis=1)

    # Convert daily USD portfolio to INR and SGD
    portfolio_inr = portfolio_usd * fx_rates[('USD_INR', 'INR=X')]
    portfolio_sgd = portfolio_usd * fx_rates[('USD_SGD', 'SGD=X')]

    # Combine into one DataFrame
    global portfolio  # so dailycharts() can access this
    portfolio = pd.DataFrame({
        'USD': portfolio_usd,
        'INR': portfolio_inr,
        'SGD': portfolio_sgd
    })

    master_df = latest_holdings.reset_index()
    master_df.columns = ['Symbol', 'Quantity']
    
    converted = convert_currency(adj_df, fx_rates)
    xirr_vals = compute_xirr(converted, daily_prices)
    xirr_df = pd.DataFrame(xirr_vals.items(), columns=['Symbol', 'XIRR'])
    xirr_df['XIRR'] = xirr_df['XIRR'] * 100  # Convert to percentage
    master_df = master_df.merge(xirr_df, on='Symbol', how='left')

    #st.subheader("📈 XIRR Results")

    # Format as percentage and display in a styled table
    
    
    master_df = master_df.sort_values(by='Symbol')

    st.subheader("📄 Master List of Holdings")

    # Current price and value per stock
    symbols_list = master_df['Symbol'].tolist()
    print("Symbols List:", symbols_list)
    tickers = yf.Tickers(' '.join(symbols_list))
    current_prices = {sym: tickers.tickers[sym].info.get('regularMarketPrice') for sym in symbols_list}
    current_currencies = {sym: tickers.tickers[sym].info.get('currency', 'USD') for sym in symbols_list}

    master_df['Currency'] = master_df['Symbol'].map(current_currencies)
    master_df['Current Price (Native)'] = master_df['Symbol'].map(current_prices)

    # Convert to USD
    latest_fx = fx_rates.loc[latest_date]
    master_df['Price (USD)'] = master_df.apply(lambda row: row['Current Price (Native)'] / latest_fx[('USD_SGD', 'SGD=X')]
                                                if row['Currency'] == 'SGD'
                                                else row['Current Price (Native)'] / latest_fx[('USD_INR', 'INR=X')]
                                                if row['Currency'] == 'INR'
                                                else row['Current Price (Native)'], axis=1)

    master_df['Value (USD)'] = master_df['Quantity'] * master_df['Price (USD)']
    master_df['Value (INR)'] = master_df['Value (USD)'] * latest_fx[('USD_INR', 'INR=X')] 
    master_df['Value (SGD)'] = master_df['Value (USD)'] * latest_fx[('USD_SGD', 'SGD=X')]

    st.dataframe(master_df.style.format({
        "Quantity": "{:.2f}",
        "Current Price (Native)": "{:.2f}",
        "Price (USD)": "${:.2f}",
        "Value (USD)": "${:.2f}",
        "Value (INR)": "₹{:.2f}",
        "Value (SGD)": "S${:.2f}",
        "XIRR": "{:.2f}%"
    }))

    total_usd = master_df['Value (USD)'].sum()
    total_inr = master_df['Value (INR)'].sum()
    total_sgd = master_df['Value (SGD)'].sum()

    st.markdown(f"### 📈 Total Portfolio Value")
    st.markdown(f"- **USD:** ${total_usd:,.2f}")
    st.markdown(f"- **INR:** ₹{total_inr:,.2f}")
    st.markdown(f"- **SGD:** S${total_sgd:,.2f}")



def dailycharts():
    # Reset index for plotting
    portfolio_reset = portfolio.reset_index().rename(columns={'index': 'Date'})

    #DAILY PORTFOLIO VALUE CHARTS
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
    
    
def main():
    title()
    holdings()#xirr to be a part of holdings
    #xirr()
    dailycharts()
    
if __name__ == "__main__":
    main()