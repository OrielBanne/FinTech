import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
import matplotlib.pyplot as plt

class TradingEnvironment(gym.Env):
    """
    סביבת מסחר מבוססת RL לטווחי זמן של ימים עד חודשים
    """
    
    def __init__(self, df, initial_balance=10000, transaction_fee_percent=0.001, window_size=30):
        super(TradingEnvironment, self).__init__()
        
        # נתוני המחירים והאינדיקטורים
        self.df = df
        self.initial_balance = initial_balance
        self.transaction_fee_percent = transaction_fee_percent
        self.window_size = window_size
        
        # מרחב הפעולות: 0 (החזקה), 1 (קנייה), 2 (מכירה)
        self.action_space = spaces.Discrete(3)
        
        # מרחב המצבים: מערך של אינדיקטורים טכניים + מצב התיק הנוכחי
        # נשתמש באינדיקטורים הטכניים שחישבנו בשלב הקודם
        # בנוסף למידע על מצב התיק (מזומן, מניות, שווי כולל)
        obs_shape = (self.window_size, self._get_observation_dimension())
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=obs_shape, dtype=np.float32)
        
        # משתנים פנימיים
        self.current_step = None
        self.balance = None
        self.shares_held = None
        self.total_shares_sold = None
        self.total_sales_value = None
        self.total_shares_bought = None
        self.total_cost_basis = None
        self.total_profit = None
        self.current_value = None
        
    def _get_observation_dimension(self):
        """
        מחזיר את מספר התכונות במרחב המצבים
        """
        # נבחר תכונות רלוונטיות מהדאטאפריים
        # מחירים
        price_features = ['open', 'high', 'low', 'close', 'adj_close', 'volume']
        
        # אינדיקטורים טכניים נבחרים
        technical_indicators = [
            # מומנטום
            'momentum_rsi', 'momentum_stoch', 'momentum_stoch_signal', 'momentum_tsi',
            # מגמה
            'trend_macd', 'trend_macd_signal', 'trend_ema_fast', 'trend_ema_slow',
            'trend_adx', 'trend_ichimoku_a', 'trend_ichimoku_b',
            # תנודתיות
            'volatility_bbm', 'volatility_bbh', 'volatility_bbl', 'volatility_atr',
            # נפח
            'volume_obv', 'volume_cmf'
        ]
        
        # תכונות נוספות למצב התיק
        portfolio_features = 3  # מזומן, מניות מוחזקות, שווי כולל
        
        # סך כל התכונות
        return len(price_features) + len(technical_indicators) + portfolio_features
    
    def reset(self, seed=None):
        """
        איפוס הסביבה למצב התחלתי
        """
        super().reset(seed=seed)
        
        # איפוס מיקום בדאטאסט
        self.current_step = self.window_size
        
        # איפוס מצב התיק
        self.balance = self.initial_balance
        self.shares_held = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0
        self.total_shares_bought = 0
        self.total_cost_basis = 0
        self.total_profit = 0
        
        # חישוב ערך נוכחי
        self.current_value = self.balance + self.shares_held * self._get_current_price()
        
        return self._get_observation(), {}
    
    def _get_current_price(self):
        """
        מחזיר את מחיר הסגירה הנוכחי
        """
        return self.df.iloc[self.current_step]['adj_close']
    
    def _get_observation(self):
        """
        מחזיר את המצב הנוכחי כמערך של תכונות
        """
        # חלון של נתונים היסטוריים
        frame = self.df.iloc[self.current_step - self.window_size:self.current_step]
        
        # נרמול הנתונים
        obs = self._normalize_frame(frame)
        
        # הוספת מידע על מצב התיק
        portfolio_info = np.array([
            self.balance / self.initial_balance,  # מזומן מנורמל
            self.shares_held * self._get_current_price() / self.initial_balance,  # ערך המניות המוחזקות מנורמל
            self.current_value / self.initial_balance  # שווי כולל מנורמל
        ])
        
        # שכפול מידע התיק לכל נקודת זמן בחלון
        portfolio_info = np.tile(portfolio_info, (self.window_size, 1))
        
        # שילוב הנתונים
        obs_with_portfolio = np.hstack([obs, portfolio_info])
        
        return obs_with_portfolio.astype(np.float32)
    
    def _normalize_frame(self, frame):
        """
        נרמול הנתונים בחלון הנוכחי
        """
        # בחירת העמודות הרלוונטיות
        price_features = ['open', 'high', 'low', 'close', 'adj_close', 'volume']
        
        technical_indicators = [col for col in frame.columns if 
                               col.startswith(('momentum_', 'trend_', 'volatility_', 'volume_'))]
        
        selected_features = price_features + technical_indicators
        
        # בדיקה שהעמודות קיימות
        available_features = [f for f in selected_features if f in frame.columns]
        
        # נרמול פשוט - חלוקה בערך המקסימלי בחלון
        normalized_frame = frame[available_features].copy()
        
        for feature in available_features:
            max_value = normalized_frame[feature].max()
            min_value = normalized_frame[feature].min()
            
            # הימנעות מחלוקה באפס
            if max_value == min_value:
                normalized_frame[feature] = 0
            else:
                normalized_frame[feature] = (normalized_frame[feature] - min_value) / (max_value - min_value)
        
        return normalized_frame.values
    
    def step(self, action):
        """
        ביצוע פעולה בסביבה
        """
        # קבלת המחיר הנוכחי
        current_price = self._get_current_price()
        
        # ביצוע הפעולה
        if action == 0:  # החזקה
            pass
        
        elif action == 1:  # קנייה
            # חישוב כמות המניות שניתן לקנות (נשתמש ב-90% מהמזומן הזמין)
            available_amount = self.balance * 0.9
            shares_bought = int(available_amount / current_price)
            
            # עדכון מצב התיק
            if shares_bought > 0:
                cost = shares_bought * current_price * (1 + self.transaction_fee_percent)
                self.balance -= cost
                self.shares_held += shares_bought
                self.total_shares_bought += shares_bought
                self.total_cost_basis += cost
        
        elif action == 2:  # מכירה
            # מכירת כל המניות המוחזקות
            if self.shares_held > 0:
                sales_value = self.shares_held * current_price * (1 - self.transaction_fee_percent)
                self.balance += sales_value
                self.total_shares_sold += self.shares_held
                self.total_sales_value += sales_value
                self.shares_held = 0
        
        # התקדמות לצעד הבא
        self.current_step += 1
        
        # בדיקה אם הסימולציה הסתיימה
        done = self.current_step >= len(self.df) - 1
        
        # חישוב שווי נוכחי
        self.current_value = self.balance + self.shares_held * current_price
        
        # חישוב רווח כולל
        self.total_profit = self.current_value - self.initial_balance
        
        # חישוב התגמול - שינוי באחוזים בשווי התיק
        reward = (self.current_value - self.initial_balance) / self.initial_balance
        
        # מידע נוסף
        info = {
            'current_step': self.current_step,
            'current_price': current_price,
            'balance': self.balance,
            'shares_held': self.shares_held,
            'current_value': self.current_value,
            'total_profit': self.total_profit,
            'total_profit_percent': (self.total_profit / self.initial_balance) * 100
        }
        
        return self._get_observation(), reward, done, False, info
    
    def render(self):
        """
        הצגה ויזואלית של מצב הסביבה
        """
        print(f"Step: {self.current_step}")
        print(f"Balance: ${self.balance:.2f}")
        print(f"Shares held: {self.shares_held}")
        print(f"Current price: ${self._get_current_price():.2f}")
        print(f"Current value: ${self.current_value:.2f}")
        print(f"Total profit: ${self.total_profit:.2f} ({(self.total_profit / self.initial_balance) * 100:.2f}%)")
        print("-" * 50)
