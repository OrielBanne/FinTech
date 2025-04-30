import sys
sys.path.append("/opt/.manus/.sandbox-runtime")
from data_api import ApiClient
import json

client = ApiClient()

# Symbols for which insights are typically available (companies)
symbols = ["AAPL", "GOOG"]
# Index symbol - insights might be limited or unavailable
index_symbol = "^GSPC"

all_symbols = symbols + [index_symbol]

for symbol in all_symbols:
    print(f"Fetching insights data for {symbol}...")
    try:
        insights_data = client.call_api("YahooFinance/get_stock_insights", query={"symbol": symbol})
        # Check if data was actually returned
        if insights_data and insights_data.get("finance") and insights_data["finance"].get("result"):
            # Prepare filename safely
            safe_symbol = symbol.lower().replace("^", "")
            file_path = f"/home/ubuntu/{safe_symbol}_insights.json"
            # Save the data
            with open(file_path, "w") as f:
                json.dump(insights_data, f, indent=2)
            print(f"Saved insights data for {symbol} to {file_path}")
        else:
            print(f"No significant insights data returned for {symbol}. Skipping file save.")
            if insights_data and insights_data.get("finance") and insights_data["finance"].get("error"):
                 print(f"API Error for {symbol}: {insights_data['finance']['error']}")

    except Exception as e:
        print(f"Error fetching insights data for {symbol}: {e}")

print("Finished fetching insights data.")

