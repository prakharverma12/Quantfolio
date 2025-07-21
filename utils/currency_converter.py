import pandas as pd

def convert_currency(transactions_df, fx_rates_df):
    def get_fx_rate(row):
        date = row['Date']
        currency = row['Currency']
        
        if currency == 'USD':
            return 1.0
        elif currency == 'SGD':
            return fx_rates_df.loc[date, ('USD_SGD', 'SGD=X')]
        elif currency == 'INR':
            return fx_rates_df.loc[date, ('USD_INR', 'INR=X')]
        else:
            raise ValueError(f"Unsupported currency: {currency}")
    
    transactions_df['FX Rate'] = transactions_df.apply(get_fx_rate, axis=1)
    transactions_df['Amount_(USD)'] = transactions_df['T. Price'] / transactions_df['FX Rate']
    
    return transactions_df
