import json
with open(r'C:\Users\Oriel\FinAlgoTrading\FinTech\rl_trading_system\data\AAPL_5y_1d.json', 'r') as f:
    data = json.load(f)
    print(type(data))
    if isinstance(data, dict):
        print(list(data.keys())[:5])  # Print first 5 keys
    else:
        print(f"Data is a {type(data)} with {len(data)} items")