import json
import pandas as pd
import pandas_ta as ta
import os

def preprocess_stock_data(symbol, chart_file, insights_file, output_dir):
    """Loads, preprocesses, and adds technical indicators to stock data."""
    print(f"Processing data for {symbol}...")

    # --- Load Chart Data ---
    try:
        with open(chart_file, 'r') as f:
            chart_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Chart file not found for {symbol} at {chart_file}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from chart file for {symbol}")
        return None

    if not chart_data or 'chart' not in chart_data or 'result' not in chart_data['chart'] or not chart_data['chart']['result']:
        print(f"Error: Chart data is empty or malformed for {symbol}")
        return None

    result = chart_data['chart']['result'][0]
    timestamps = result.get('timestamp')
    indicators = result.get('indicators')

    if not timestamps or not indicators or 'quote' not in indicators or not indicators['quote'] or 'adjclose' not in indicators or not indicators['adjclose']:
        print(f"Error: Missing essential keys (timestamp, indicators, quote, adjclose) in chart data for {symbol}")
        return None

    quote = indicators['quote'][0]
    adjclose = indicators['adjclose'][0]['adjclose']

    # Check if all lists have the same length
    required_keys = ['open', 'high', 'low', 'close', 'volume']
    if not all(key in quote for key in required_keys):
        print(f"Error: Missing price/volume keys in quote data for {symbol}")
        return None

    lengths = [len(timestamps), len(adjclose)] + [len(quote[key]) for key in required_keys]
    if len(set(lengths)) > 1:
        print(f"Error: Data arrays have inconsistent lengths for {symbol}. Lengths: {lengths}")
        # Attempt to truncate to the minimum length if reasonable
        min_len = min(lengths)
        if min_len > 0:
            print(f"Attempting to truncate all arrays to minimum length: {min_len}")
            timestamps = timestamps[:min_len]
            adjclose = adjclose[:min_len]
            for key in required_keys:
                quote[key] = quote[key][:min_len]
        else:
            return None # Cannot proceed if minimum length is 0

    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': quote['open'],
        'high': quote['high'],
        'low': quote['low'],
        'close': quote['close'],
        'volume': quote['volume'],
        'adj_close': adjclose
    })

    # Convert timestamp to datetime and set as index
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df.set_index('timestamp')

    # Handle potential missing values (e.g., forward fill)
    # Check for NaNs introduced by inconsistent lengths or API issues
    df = df.dropna(subset=['open', 'high', 'low', 'close', 'adj_close', 'volume'])
    # df = df.fillna(method='ffill') # Optional: Forward fill if needed after dropna

    if df.empty:
        print(f"Error: DataFrame became empty after handling missing values for {symbol}")
        return None

    # --- Calculate Technical Indicators ---
    print(f"Calculating technical indicators for {symbol}...")
    try:
        df.ta.sma(length=20, append=True)
        df.ta.sma(length=50, append=True)
        df.ta.rsi(length=14, append=True)
        df.ta.macd(append=True)
        # Add more indicators as needed
    except Exception as e:
        print(f"Error calculating technical indicators for {symbol}: {e}")
        # Continue without indicators if calculation fails

    # --- (Optional) Integrate Insights Data ---
    # This part can be complex. For now, we'll skip direct integration
    # but you could extract specific fields like outlook scores if needed.
    # Example: Load insights, find relevant date, add score as feature.

    # --- Save Processed Data ---
    output_file = os.path.join(output_dir, f"{symbol.lower().replace('^', '')}_processed.csv")
    try:
        df.to_csv(output_file)
        print(f"Successfully processed and saved data for {symbol} to {output_file}")
        return output_file
    except Exception as e:
        print(f"Error saving processed data for {symbol}: {e}")
        return None

# --- Main Execution --- #
symbols = ["AAPL", "GOOG", "^GSPC", "NVDA"]
base_dir = "/home/ubuntu"
output_dir = "/home/ubuntu/processed_data"

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

processed_files = []
for symbol in symbols:
    safe_symbol_name = symbol.lower().replace('^', '')
    chart_file = os.path.join(base_dir, f"{safe_symbol_name}_chart_5y.json")
    insights_file = os.path.join(base_dir, f"{safe_symbol_name}_insights.json") # Path to insights file

    processed_path = preprocess_stock_data(symbol, chart_file, insights_file, output_dir)
    if processed_path:
        processed_files.append(processed_path)

print("\n--- Preprocessing Summary ---")
if processed_files:
    print("Successfully processed files:")
    for f in processed_files:
        print(f"- {f}")
else:
    print("No files were processed successfully.")

