# Comparison of Trading Systems and Brokers with APIs

| Broker/System | Connection Difficulty | API Type | Monthly Cost | Account Minimums | Commission | Python Library |
|---------------|----------------------|----------|--------------|------------------|------------|----------------|
| **Interactive Brokers (IBKR)** | Moderate | REST and WebSocket | Free API access with funded account | $0 for IBKR Lite, $10,000 for IBKR Pro | IBKR Lite: Commission-free for US stocks; IBKR Pro: Tiered pricing starting at $0.0035 per share ($0.35 minimum) | `ib_insync` (third-party wrapper for official API) |
| **Alpaca** | Easy | REST and WebSocket | Free for paper trading, commission-free for live trading with funded account | $0 for standard accounts | Commission-free for standard accounts; Alpaca Pro has volume-based pricing | Official `alpaca-trade-api-python` |
| **TD Ameritrade** | Easy to Moderate | REST | Free API access with funded account | $0 | $0 for online equity trades | `tda-api` (third-party) |
| **Tradier** | Easy | REST | $10/month for Developer tier, $30/month for Premium tier | $0 | $0 for Developer tier (with limitations), $0.35 per options contract for Premium | No official library, but REST API is simple to use |
| **OANDA** | Easy | REST and WebSocket | Free with funded account | Varies by region (typically $1-100) | Spread-based pricing model | `oandapyV20` |