import pandas as pd

def convert_currency(transactions: pd.DataFrame, currency_file: str) -> pd.DataFrame:
    # Load FX rates
    fx = pd.read_csv(currency_file)
    fx['Date'] = pd.to_datetime(fx['Date'])

    # Parse transaction date
    transactions = transactions.copy()  # To avoid modifying original
    transactions['Date'] = pd.to_datetime(transactions['Date/Time']).dt.normalize()

    # Merge with FX data
    merged = transactions.merge(fx, on='Date', how='left')

    # Ensure Proceeds and FX columns are numeric
    merged['Proceeds'] = pd.to_numeric(merged['Proceeds'], errors='coerce')
    for col in ['USD_INR', 'USD_SGD']:
        merged[col] = pd.to_numeric(merged[col], errors='coerce')
        merged[f'Proceeds_{col}'] = merged['Proceeds'] * merged[col]
    merged = merged.dropna()
    return merged
