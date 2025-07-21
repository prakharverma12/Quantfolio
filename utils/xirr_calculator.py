from pyxirr import xirr
import pandas as pd
from datetime import datetime
def compute_xirr(transactions, daily_prices, fx_rates=None):
    results = {}
    transactions['Date'] = pd.to_datetime(transactions['Date/Time']).dt.date
    grouped = transactions.groupby('Symbol')

    for symbol, group in grouped:
        cashflows = [
            (pd.to_datetime(date), -proceeds)
            for date, proceeds in zip(group['Date'], group['Proceeds'])
        ]

        total_qty = group['Quantity'].sum()
        if total_qty != 0 and symbol in daily_prices.columns:
            try:
                latest_price = daily_prices[symbol].dropna().iloc[-1]
                inflow = total_qty * latest_price

                # Optional: Convert inflow to USD using fx_rates
                if fx_rates is not None:
                    currency = group.iloc[-1].get('Currency', 'USD')
                    if currency == 'SGD':
                        inflow /= fx_rates[('USD_SGD', 'SGD=X')]
                    elif currency == 'INR':
                        inflow /= fx_rates[('USD_INR', 'INR=X')]

                cashflows.append((datetime.today(), inflow))
            except Exception as e:
                print(f"Price fetch failed for {symbol}: {e}")
                results[symbol] = None
                continue

        try:
            results[symbol] = xirr(cashflows)
        except Exception as e:
            print(f"XIRR failed for {symbol}: {e}")
            results[symbol] = None

    return results
