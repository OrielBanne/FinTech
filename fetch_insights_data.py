import sys
sys.path.append("/opt/.manus/.sandbox-runtime")
from data_api import ApiClient
import json

client = ApiClient()

symbols = ["AAPL", "GOOG", "NVDA"]
data_dir = "/home/ubuntu/rl_trading_system/data"

for symbol in symbols:
    print(f"Fetching insights data for {symbol}...")
    try:
        insights_data = client.call_api("YahooFinance/get_stock_insights", query={"symbol": symbol})
        # Save the data to a JSON file
        file_path = f"{data_dir}/{symbol}_insights.json"
        with open(file_path, "w") as f:
            json.dump(insights_data, f, indent=2)
        print(f"Successfully fetched and saved insights data for {symbol} to {file_path}")
    except Exception as e:
        print(f"Error fetching insights data for {symbol}: {e}")

print("Finished fetching stock insights data.")

