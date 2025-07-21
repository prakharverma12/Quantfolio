import yfinance as yf
import pandas as pd

def adjust_transactions_for_splits(transactions):
    """
    Adjusts transaction quantity, price, and proceeds for all split events in the transaction history.

    Args:
        transactions (pd.DataFrame): Must contain 'Ticker (Symbol)', 'Date', 'Quantity', 'T. Price' columns.

    Returns:
        pd.DataFrame: Adjusted transactions DataFrame.
    """

    # Ensure Date is in datetime format
    transactions['Date/Time'] = pd.to_datetime(transactions['Date/Time'], errors='coerce')    # Get all unique tickers
    unique_tickers = transactions['Symbol'].unique()
    for tiker in unique_tickers:
        if tiker == 'C6L.SI':
            print("C6L.SI found in unique tickers while Adjusting for splits adjust_transactions_for_splits function")
    # Define date range and localize to the timezone of splits (e.g., New York)
    start_date = pd.Timestamp("2023-07-01", tz="America/New_York")
    end_date = pd.Timestamp("2025-07-01", tz="America/New_York")
    # Container for split data
    split_dict = {}
    

    for ticker in unique_tickers:
        stock = yf.Ticker(ticker)
        splits = stock.splits  # Returns Series with date as index, ratio as values
        #print("splits  : ",splits)
        if not splits.empty:
            filtered = splits[(splits.index >= start_date) & (splits.index <= end_date)]
            # Convert to list of (date, ratio)
            split_events = [(pd.to_datetime(date), ratio) for date, ratio in filtered.items()]
            split_events.sort()  # Sort by date (earliest first)
            split_dict[ticker] = split_events
    
    # Make a copy to avoid modifying original
    df = transactions.copy()
    df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
    df['T. Price'] = pd.to_numeric(df['T. Price'], errors='coerce')
    df['Proceeds'] = pd.to_numeric(df['Proceeds'], errors='coerce')

    for ticker, splits in split_dict.items():
        for split_date, ratio in splits:
            split_date = pd.to_datetime(split_date).tz_localize(None)
            # Affected transactions: before the split
            mask = (df['Symbol'] == ticker) & (df['Date/Time'] < split_date)
            
            # Adjust quantity (multiply) and price (divide)
            df.loc[mask, 'Quantity'] = df.loc[mask, 'Quantity'] * ratio
            df.loc[mask, 'T. Price'] = df.loc[mask, 'T. Price'] / ratio
            
    # Recompute proceeds (adjusted)
    df['Proceeds'] = df['Quantity'] * df['T. Price']

    return df
