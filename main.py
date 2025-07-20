from utils.data_loader import load_transaction_files
from utils.split_adjuster import adjust_transactions_for_splits
from utils.currency_converter import convert_currency
from utils.xirr_calculator import compute_xirr

# Load
transactions = load_transaction_files(['data/Stock_trading_2023.csv', 'data/Stock_trading_2024.csv', 'data/Stock_trading_2023.csv'])
print("TRANSACTIONS :\n",transactions.head())
# Stock Splits
adjusted_txns = adjust_transactions_for_splits(transactions)
print("ADJUSTMENT : \n",adjusted_txns.head())
# Currency Conversion
converted_txns = convert_currency(adjusted_txns, 'data/currency_rates_july2023_july2025.csv')
print("CONVERSION : \n",converted_txns.head())
# XIRR
xirr_results = compute_xirr(converted_txns)

print("XIRR results :",xirr_results)