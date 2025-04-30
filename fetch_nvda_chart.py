import sys
sys.path.append("/opt/.manus/.sandbox-runtime")
from data_api import ApiClient
import json

client = ApiClient()

symbol = "NVDA"
interval = "1d"
range_ = "5y"

print(f"Fetching chart data for {symbol}...")
try:
    chart_data = client.call_api("YahooFinance/get_stock_chart", query={"symbol": symbol, "interval": interval, "range": range_, "includeAdjustedClose": True})
    # Save the data
    file_path = f"/home/ubuntu/{symbol.lower()}_chart_{range_}.json"
    with open(file_path, "w") as f:
        json.dump(chart_data, f, indent=2)
    print(f"Saved chart data for {symbol} to {file_path}")
except Exception as e:
    print(f"Error fetching chart data for {symbol}: {e}")

print(f"Finished fetching chart data for {symbol}.")

