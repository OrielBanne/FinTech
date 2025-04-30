import yfinance as yf
import json
import os
import pandas as pd


tickers = ['AAPL', 'GOOG', 'NVDA', '^GSPC']
data_dir = r'C:\Users\Oriel\FinAlgoTrading\FinTech\rl_trading_system\data'

# Create directory if it doesn't exist
os.makedirs(data_dir, exist_ok=True)

for ticker in tickers:
    print(f'Fetching 5-year daily data for {ticker}...')
    try:
        # Download the data
        stock_data = yf.download(
            tickers=ticker,
            start='2015-01-01',
            end='2020-01-01',
            interval='1d'
        )
        
        # Print the index and column types for debugging
        print(f"Data shape: {stock_data.shape}")
        print(f"Index type: {type(stock_data.index)}")
        print(f"Column names: {list(stock_data.columns)}")
        
        # Handle MultiIndex if present
        if isinstance(stock_data.columns, pd.MultiIndex):
            print("MultiIndex detected, converting to flat structure...")
            # Create a flat DataFrame
            flat_data = pd.DataFrame()
            for col_tuple in stock_data.columns:
                # Join tuple elements to create flat column names
                col_name = '_'.join([str(x) for x in col_tuple if x != ''])
                flat_data[col_name] = stock_data[col_tuple]
            stock_data = flat_data
            print(f"New column names: {list(stock_data.columns)}")
        
        # Save the data to a JSON file
        file_path = f'{data_dir}/{ticker}_5y_1d.json'
        
        # Convert to dictionary for JSON serialization
        stock_dict = {}
        for date, row in stock_data.iterrows():
            date_str = date.strftime('%Y-%m-%d')
            
            # Create entry with available columns
            # Remove ticker suffix from column names
            entry = {}
            for column in stock_data.columns:
                # Extract base column name by removing ticker suffix
                base_column = column.split('_')[0] if '_' in column else column
                
                # Get the scalar value properly
                if 'Volume' in str(column):
                    entry[base_column] = int(row[column])
                else:
                    entry[base_column] = float(row[column])
            
            stock_dict[date_str] = entry
        
        # Save the data to a JSON file
        with open(file_path, 'w') as f:
            json.dump(stock_dict, f, indent=2)
            
        print(f'Successfully fetched and saved data for {ticker} to {file_path}')
    except Exception as e:
        print(f'Error fetching data for {ticker}: {str(e)}')
        # Print more details for debugging
        import traceback
        traceback.print_exc()

print('Finished fetching stock price data.')

