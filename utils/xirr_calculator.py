from pyxirr import xirr
import pandas as pd
from datetime import datetime

def compute_xirr(transactions):
    results = {}
    transactions['Date'] = pd.to_datetime(transactions['Date/Time']).dt.date
    grouped = transactions.groupby('Symbol')

    for symbol, group in grouped:
        # Create list of (date, amount) tuples
        cashflows = [
            (pd.to_datetime(date), -proceeds)
            for date, proceeds in zip(group['Date'], group['Proceeds'])
        ]

        total_qty = group['Quantity'].sum()
        if total_qty != 0:
            est_price = group.iloc[-1]['T. Price']
            # Add current value of holding as inflow
            cashflows.append((datetime.today(), total_qty * est_price))

        try:
            results[symbol] = xirr(cashflows)
        except Exception as e:
            print(f"XIRR failed for {symbol}: {e}")
            results[symbol] = None

    return results
