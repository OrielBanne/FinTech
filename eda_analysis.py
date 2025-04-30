import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define directories
processed_data_dir = r'C:\Users\Oriel\FinAlgoTrading\FinTech\rl_trading_system\data\processed'
results_dir = r'C:\Users\Oriel\FinAlgoTrading\FinTech\rl_trading_system\results\eda_plots'
os.makedirs(results_dir, exist_ok=True)

# Symbol to analyze
symbol = "^GSPC" # Can be changed to AAPL, GOOG, or NVDA

# Load processed price data
price_file = os.path.join(processed_data_dir, f"{symbol}_processed_prices.csv")
print(f"Loading processed data from {price_file}...")

try:
    df = pd.read_csv(price_file, index_col='timestamp', parse_dates=True)
    print("Data loaded successfully.")

    # --- Exploratory Data Analysis --- 

    # 1. Plot Adjusted Close Price
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['adj_close'], label=f"{symbol} Adjusted Close Price")
    plt.title(f"{symbol} Adjusted Close Price Over 5 Years")
    plt.xlabel("Date")
    plt.ylabel("Adjusted Close Price (USD)")
    plt.legend()
    plt.grid(True)
    plot_path_close = os.path.join(results_dir, f"{symbol}_adj_close_price.png")
    plt.savefig(plot_path_close)
    plt.close()
    print(f"Saved adjusted close price plot to {plot_path_close}")

    # 2. Plot Trading Volume
    plt.figure(figsize=(14, 7))
    plt.bar(df.index, df['volume'], label=f"{symbol} Volume")
    plt.title(f"{symbol} Trading Volume Over 5 Years")
    plt.xlabel("Date")
    plt.ylabel("Volume")
    plt.legend()
    plt.grid(True)
    plot_path_volume = os.path.join(results_dir, f"{symbol}_volume.png")
    plt.savefig(plot_path_volume)
    plt.close()
    print(f"Saved volume plot to {plot_path_volume}")

    # 3. Plot a Moving Average (e.g., SMA 12 and SMA 26 from the 'ta' library)
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['adj_close'], label="Adj Close")
    # Check if the columns exist before plotting
    if 'trend_sma_fast' in df.columns: # Assuming 'trend_sma_fast' is the 12-day SMA from ta
        plt.plot(df.index, df['trend_sma_fast'], label="SMA 12")
    if 'trend_sma_slow' in df.columns: # Assuming 'trend_sma_slow' is the 26-day SMA from ta
        plt.plot(df.index, df['trend_sma_slow'], label="SMA 26")
    plt.title(f"{symbol} Adjusted Close Price and Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plot_path_sma = os.path.join(results_dir, f"{symbol}_sma.png")
    plt.savefig(plot_path_sma)
    plt.close()
    print(f"Saved moving average plot to {plot_path_sma}")

    # 4. Plot Distribution of Daily Returns
    df['daily_return'] = df['adj_close'].pct_change()
    plt.figure(figsize=(10, 6))
    sns.histplot(df['daily_return'].dropna(), bins=100, kde=True)
    plt.title(f"{symbol} Distribution of Daily Returns")
    plt.xlabel("Daily Return")
    plt.ylabel("Frequency")
    plt.grid(True)
    plot_path_returns = os.path.join(results_dir, f"{symbol}_daily_returns_dist.png")
    plt.savefig(plot_path_returns)
    plt.close()
    print(f"Saved daily returns distribution plot to {plot_path_returns}")

    print(f"\nFinished EDA for {symbol}.")

except FileNotFoundError:
    print(f"Error: Processed file not found at {price_file}")
except Exception as e:
    print(f"An error occurred during EDA for {symbol}: {e}")

