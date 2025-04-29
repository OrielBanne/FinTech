import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json

client = ApiClient()

symbols = ['AAPL', 'GOOG', 'NVDA', '^GSPC']
data_dir = '/home/ubuntu/rl_trading_system/data'

for symbol in symbols:
    print(f'Fetching 5-year daily data for {symbol}...')
    try:
        stock_data = client.call_api('YahooFinance/get_stock_chart', query={'symbol': symbol, 'range': '5y', 'interval': '1d', 'includeAdjustedClose': True})
        # Save the data to a JSON file
        file_path = f'{data_dir}/{symbol}_5y_1d.json'
        with open(file_path, 'w') as f:
            json.dump(stock_data, f, indent=2)
        print(f'Successfully fetched and saved data for {symbol} to {file_path}')
    except Exception as e:
        print(f'Error fetching data for {symbol}: {e}')

print('Finished fetching stock price data.')

