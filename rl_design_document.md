# RL Trading Algorithm Design

This document outlines the design choices for the Reinforcement Learning (RL) based trading algorithm.

## 1. Objective

Develop an RL agent capable of learning a trading policy for a portfolio of assets (AAPL, GOOG, ^GSPC, NVDA) targeting medium to long-term holding periods (weeks to a year). The agent must make decisions based solely on historical data available up to the decision point.

## 2. RL Environment Definition

### 2.1. State Space

The state observed by the agent at each time step `t` will be a combination of market information and portfolio status.

*   **Market Information:** A lookback window (e.g., `W=60` days) of historical data for each asset. For each day in the window, the features will include:
    *   Normalized OHLC prices (Open, High, Low, Close)
    *   Normalized Volume
    *   Calculated Technical Indicators (e.g., SMA(20), SMA(50), RSI(14), MACD signal line, MACD histogram) - also normalized.
    *   *Optional: Relevant features extracted from insights data (e.g., technical outlook scores, valuation metrics), if consistently available and alignable with daily data.* Normalization is crucial to prevent features with larger magnitudes from dominating.
*   **Portfolio Status:**
    *   Current holdings for each asset (number of shares).
    *   Remaining cash balance.
    *   *Optional: Current portfolio value.* 

The state will be represented as a multi-dimensional array or vector suitable for input into a neural network.

### 2.2. Action Space

We will start with a discrete action space for simplicity. For each asset in the portfolio, the agent can choose one of the following actions:

*   **Hold (0):** Make no changes to the current position in the asset.
*   **Buy (1):** Allocate a fixed portion of the available cash to buy the asset (e.g., buy shares equivalent to 10% of current cash, or a fixed number of shares if cash allows).
*   **Sell (2):** Sell all currently held shares of the asset.

This results in an action space size of `3^N`, where `N` is the number of assets (currently 4). Alternatively, the agent could output a vector of actions, one for each asset.

*Future Enhancement:* Consider a continuous action space where the agent decides the *percentage* of capital to allocate to buying or selling each asset.

### 2.3. Reward Function

The reward at time step `t` (`R_t`) will primarily reflect the change in the total portfolio value.

`Portfolio Value (t) = Cash (t) + Sum(Current Price (t) * Shares Held (t) for each asset)`

`R_t = Portfolio Value (t) - Portfolio Value (t-1) - Transaction Costs (t)`

*   **Transaction Costs:** A small penalty will be applied for each Buy or Sell action to simulate brokerage fees and slippage, discouraging excessive trading.
*   **Long-term Incentive:** To align with the goal of weeks-to-year holding periods, we can explore modifications:
    *   **Shaping:** Add a small positive reward for holding a profitable position over a certain period.
    *   **Terminal Reward:** Provide a larger reward based on the overall performance (e.g., Sharpe ratio) at the end of an episode (e.g., end of the backtesting period).

## 3. RL Algorithm Choice

**Proximal Policy Optimization (PPO)** is selected due to its:
*   Good balance between sample efficiency and ease of implementation.
*   Relative stability compared to other policy gradient methods.
*   Effectiveness in both discrete and continuous action spaces.

## 4. Agent Architecture

A Multi-Layer Perceptron (MLP) network will be used for both the policy (actor) and value (critic) functions within the PPO framework.

*   **Input Layer:** Size corresponding to the flattened state representation.
*   **Hidden Layers:** 2-3 hidden layers with ReLU activation functions (e.g., 256 units per layer).
*   **Output Layer(s):**
    *   Actor: Output layer appropriate for the action space (e.g., softmax for discrete actions).
    *   Critic: Single output unit representing the estimated value of the state.

## 5. Implementation Considerations

*   **Data Splitting:** The processed historical data will be split into training, validation (for hyperparameter tuning), and testing (for final backtesting) sets.
*   **Normalization:** State features must be normalized (e.g., using min-max scaling or z-score standardization based on the training set) before being fed to the agent.
*   **Framework:** Utilize a standard RL library like Stable Baselines3 (built on PyTorch) or TF-Agents (TensorFlow) for implementation.
