import pandas as pd
import json
import os
import ta
from ta.utils import dropna

data_dir = '/home/ubuntu/rl_trading_system/data'
processed_data_dir = '/home/ubuntu/rl_trading_system/data/processed'
os.makedirs(processed_data_dir, exist_ok=True)

symbols = ['AAPL', 'GOOG', 'NVDA', '^GSPC']

def process_price_data(symbol):
    file_path = os.path.join(data_dir, f'{symbol}_5y_1d.json')
    print(f'Processing price data for {symbol} from {file_path}...')
    try:
        with open(file_path, 'r') as f:
            raw_data = json.load(f)

        if not raw_data or 'chart' not in raw_data or 'result' not in raw_data['chart'] or not raw_data['chart']['result']:
            print(f'Warning: No valid chart data found for {symbol} in {file_path}')
            return None

        chart_data = raw_data['chart']['result'][0]
        timestamps = chart_data.get('timestamp', [])
        indicators = chart_data.get('indicators', {})
        quote = indicators.get('quote', [{}])[0]
        adjclose = indicators.get('adjclose', [{}])[0].get('adjclose', []) if indicators.get('adjclose') else [] # Adjusted close might be nested differently or missing

        if not timestamps or not quote.get('open') or not quote.get('high') or not quote.get('low') or not quote.get('close') or not quote.get('volume'):
             print(f'Warning: Missing essential price data fields for {symbol} in {file_path}')
             return None

        df = pd.DataFrame({
            'timestamp': timestamps,
            'open': quote.get('open', [None]*len(timestamps)),
            'high': quote.get('high', [None]*len(timestamps)),
            'low': quote.get('low', [None]*len(timestamps)),
            'close': quote.get('close', [None]*len(timestamps)),
            'volume': quote.get('volume', [None]*len(timestamps))
        })

        # Add adjusted close if available
        if adjclose and len(adjclose) == len(timestamps):
             df['adj_close'] = adjclose
        else:
             print(f'Warning: Adjusted close data missing or length mismatch for {symbol}. Using close price.')
             df['adj_close'] = df['close'] # Fallback to close if adj_close is problematic

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('timestamp', inplace=True)

        # Clean data - drop rows with any NaN/None in essential columns before calculating indicators
        essential_cols = ['open', 'high', 'low', 'close', 'volume', 'adj_close'] # Ensure adj_close is included
        df.dropna(subset=essential_cols, inplace=True)

        if df.empty:
            print(f'Warning: DataFrame empty after dropping NaNs for {symbol}. Skipping indicator calculation.')
            return None

        # Calculate technical indicators
        df = ta.add_all_ta_features(
            df, open='open', high='high', low='low', close='close', volume='volume', fillna=True
        )

        # Save processed data
        output_path = os.path.join(processed_data_dir, f'{symbol}_processed_prices.csv')
        df.to_csv(output_path)
        print(f'Successfully processed and saved data for {symbol} to {output_path}')
        return df

    except Exception as e:
        print(f'Error processing price data for {symbol}: {e}')
        return None

# Process data for all symbols
processed_dfs = {}
for symbol in symbols:
    processed_df = process_price_data(symbol)
    if processed_df is not None:
        processed_dfs[symbol] = processed_df

print('\nFinished processing all price data.')

# Example: Display head of processed AAPL data
if 'AAPL' in processed_dfs:
    print('\nSample processed data for AAPL:')
    print(processed_dfs['AAPL'].head())

