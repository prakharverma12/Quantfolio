import yfinance as yf
import pandas as pd
# --- 1. Load Currency Rates ---
def get_daily_currency_rates(start_date, end_date):
    usd_inr = yf.download("INR=X", start=start_date, end=end_date)[['Close']].rename(columns={'Close': 'USD_INR'})
    usd_sgd = yf.download("SGD=X", start=start_date, end=end_date)[['Close']].rename(columns={'Close': 'USD_SGD'})
    fx = usd_inr.join(usd_sgd, how='outer')
    fx.index.name = 'Date'
    return fx.reset_index()

def get_currency_for_tickers(symbols):
    ticker_obj = yf.Tickers(' '.join(symbols))
    currency_map = {}
    for sym in symbols:
        try:
            currency = ticker_obj.tickers[sym].info.get('currency', 'USD')  # Default fallback
            currency_map[sym] = currency
        except Exception:
            currency_map[sym] = 'USD'  # Fallback in case of error
    return currency_map

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
    print("MAX C6L.SI IN computing holdings function:", transactions[transactions['Symbol'] == 'C6L.SI']['Quantity'].max())
    # Ensure datetime and column rename
    if 'Date/Time' in transactions.columns:
        transactions['Date'] = pd.to_datetime(transactions['Date/Time']).dt.normalize()
    elif 'Date' in transactions.columns:
        transactions['Date'] = pd.to_datetime(transactions['Date']).dt.normalize()
    else:
        raise KeyError("No 'Date' or 'Date/Time' column found in transactions")

    grouped = transactions.groupby(['Date', 'Symbol'])['Quantity'].sum().unstack(fill_value=0)
    holdings = grouped.cumsum()
    print("Holdings DataFrame after cumsum:", holdings.head())
    print("Holdings DataFrame columns:", holdings.columns)
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

