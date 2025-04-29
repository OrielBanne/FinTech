import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# הוספת תיקיית המקור לנתיב החיפוש
sys.path.append('/home/ubuntu/rl_trading_system/src')

# ייבוא הסביבה והסוכן
from trading_env import TradingEnvironment
from rl_agent import RLTradingAgent

# הגדרת נתיבים
data_dir = '/home/ubuntu/rl_trading_system/data/processed'
results_dir = '/home/ubuntu/rl_trading_system/results'
os.makedirs(results_dir, exist_ok=True)

# טעינת נתוני AAPL מעובדים
symbol = 'AAPL'
price_file = os.path.join(data_dir, f'{symbol}_processed_prices.csv')
print(f'טוען נתונים מעובדים מ-{price_file}...')

try:
    # טעינת הנתונים
    df = pd.read_csv(price_file, index_col='timestamp', parse_dates=True)
    print(f'נטענו {len(df)} רשומות של נתוני {symbol}')
    
    # יצירת סביבת המסחר
    env = TradingEnvironment(df, initial_balance=10000, window_size=30)
    
    # יצירת סוכן ה-RL
    agent = RLTradingAgent(
        env=env,
        learning_rate=0.001,
        discount_factor=0.95,
        exploration_rate=1.0,
        exploration_decay=0.995,
        min_exploration_rate=0.01
    )
    
    # הגדרת פרמטרים לאימון
    episodes = 100  # מספר אפיזודות לאימון
    max_steps = None  # מגבלת צעדים לאפיזודה (None = ללא הגבלה)
    render_interval = 10  # תדירות הצגת התקדמות
    
    print(f'\nמתחיל אימון למשך {episodes} אפיזודות...')
    
    # אימון הסוכן
    episode_rewards = agent.train(
        episodes=episodes,
        max_steps=max_steps,
        render_interval=render_interval
    )
    
    # הצגת תוצאות האימון
    agent.plot_results(episode_rewards)
    
    print('\nהאימון הושלם בהצלחה!')
    
    # בדיקת ביצועי הסוכן
    print('\nבודק ביצועים על סט הבדיקה...')
    test_profits = agent.test(episodes=5)
    
    # שמירת תוצאות
    results_file = os.path.join(results_dir, f'{symbol}_rl_results.txt')
    with open(results_file, 'w') as f:
        f.write(f'סיכום תוצאות אימון עבור {symbol}:\n')
        f.write(f'מספר אפיזודות: {episodes}\n')
        f.write(f'תגמול ממוצע: {np.mean(episode_rewards):.2f}\n')
        f.write(f'רווח ממוצע בבדיקה: {np.mean(test_profits):.2f}%\n')
    
    print(f'\nהתוצאות נשמרו ב-{results_file}')
    
except FileNotFoundError:
    print(f'שגיאה: קובץ הנתונים לא נמצא ב-{price_file}')
except Exception as e:
    print(f'שגיאה במהלך האימון: {e}')
