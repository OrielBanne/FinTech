import pandas as pd
import json
import os
import ta
from ta.utils import dropna

# Fix the data paths - use absolute path if needed
# Option 1: Define absolute path
data_dir = r'C:\Users\Oriel\FinAlgoTrading\FinTech\rl_trading_system\data'
processed_data_dir = os.path.join(data_dir, 'processed')

# Option 2: Or use relative path properly (if script is in src folder)
# data_dir = os.path.join('..', 'data')
# processed_data_dir = os.path.join(data_dir, 'processed')

# Create the processed directory if it doesn't exist
os.makedirs(processed_data_dir, exist_ok=True)

symbols = ['AAPL', 'GOOG', 'NVDA', '^GSPC']

# Debug statement to check if files exist
for symbol in symbols:
    file_path = os.path.join(data_dir, f'{symbol}_5y_1d.json')
    if os.path.exists(file_path):
        print(f"Found file: {file_path}")
    else:
        print(f"File not found: {file_path}")

def process_price_data(symbol):
    file_path = os.path.join(data_dir, f'{symbol}_5y_1d.json')
    print(f'Processing price data for {symbol} from {file_path}...')
    try:
        with open(file_path, 'r') as f:
            data_dict = json.load(f)
        
        # Check if this is directly a dictionary of date -> OHLCV data
        if isinstance(data_dict, dict):
            # Create a DataFrame from the dictionary
            dates = []
            price_data = []
            
            for date_str, values in data_dict.items():
                dates.append(date_str)
                price_data.append(values)
            
            df = pd.DataFrame(price_data, index=dates)
            df.index = pd.to_datetime(df.index)
            
            # Rename columns if needed to match expected names
            column_mapping = {
                'Open': 'open',
                'High': 'high',
                'Low': 'low',
                'Close': 'close',
                'Adj Close': 'adj_close',
                'Volume': 'volume'
            }
            df = df.rename(columns=column_mapping)
            
            # Ensure all required columns exist
            required_cols = ['open', 'high', 'low', 'close', 'volume', 'adj_close']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"Warning: Missing required columns {missing_cols} for {symbol}")
                if 'adj_close' in missing_cols and 'close' in df.columns:
                    df['adj_close'] = df['close']
                    missing_cols.remove('adj_close')
                
                if missing_cols:  # If there are still missing columns
                    return None
            
            # Clean data - drop rows with any NaN/None in essential columns
            df.dropna(subset=required_cols, inplace=True)
            
            if df.empty:
                print(f'Warning: DataFrame empty after dropping NaNs for {symbol}.')
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
            
        # If original format was expected (chart -> result structure)
        elif 'chart' in data_dict and 'result' in data_dict['chart']:
            # Original processing code for Yahoo Finance API format
            chart_data = data_dict['chart']['result'][0]
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
            
        else:
            print(f'Warning: Unrecognized data format for {symbol} in {file_path}')
            return None
            
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

