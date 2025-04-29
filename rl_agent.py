import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from trading_env import TradingEnvironment

class RLTradingAgent:
    """
    סוכן למידת חיזוק למסחר בשוק ההון
    מימוש פשוט של אלגוריתם Q-Learning
    """
    
    def __init__(self, env, learning_rate=0.001, discount_factor=0.95, exploration_rate=1.0, 
                 exploration_decay=0.995, min_exploration_rate=0.01):
        self.env = env
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.exploration_decay = exploration_decay
        self.min_exploration_rate = min_exploration_rate
        
        # יצירת טבלת Q פשוטה (נשתמש בגישה מופשטת יותר בהמשך)
        # במקום טבלה מלאה, נשתמש במודל רשת עצבית בגרסה המתקדמת
        self.q_table = {}
        
    def _get_state_key(self, state):
        """
        המרת מצב למפתח שניתן להשתמש בו בטבלת Q
        בגרסה מתקדמת יותר נשתמש ברשת עצבית במקום
        """
        # פישוט המצב למספר קטן של תכונות מרכזיות
        # במימוש מלא נשתמש בכל המידע מהמצב
        
        # לדוגמה: נשתמש רק במחיר הסגירה, RSI, ו-MACD
        if len(state.shape) > 2:  # אם המצב הוא מערך תלת-ממדי
            state = state[0]  # לקחת רק את החלון האחרון
            
        # נניח שהעמודות הרלוונטיות נמצאות במיקומים הבאים
        # (במימוש אמיתי נצטרך לוודא את המיקומים המדויקים)
        close_idx = 4  # מחיר סגירה
        rsi_idx = 20   # RSI (לדוגמה)
        macd_idx = 25  # MACD (לדוגמה)
        
        # לקיחת הערך האחרון בחלון
        last_idx = -1
        
        # דיסקרטיזציה של הערכים
        close_discrete = int(state[last_idx, close_idx] * 10)
        rsi_discrete = int(state[last_idx, rsi_idx] * 10) if state.shape[1] > rsi_idx else 0
        macd_discrete = int(state[last_idx, macd_idx] * 10) if state.shape[1] > macd_idx else 0
        
        # יצירת מפתח
        return (close_discrete, rsi_discrete, macd_discrete)
    
    def choose_action(self, state):
        """
        בחירת פעולה בהתאם למדיניות אפסילון-חמדנית
        """
        # אקספלורציה - בחירת פעולה אקראית
        if np.random.random() < self.exploration_rate:
            return self.env.action_space.sample()
        
        # אקספלויטציה - בחירת הפעולה הטובה ביותר לפי טבלת Q
        state_key = self._get_state_key(state)
        
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.env.action_space.n)
            
        return np.argmax(self.q_table[state_key])
    
    def update_q_table(self, state, action, reward, next_state, done):
        """
        עדכון טבלת Q בהתאם לנוסחת Q-Learning
        """
        state_key = self._get_state_key(state)
        next_state_key = self._get_state_key(next_state)
        
        # יצירת ערכים התחלתיים אם המצב לא קיים בטבלה
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.env.action_space.n)
            
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.env.action_space.n)
        
        # חישוב ערך Q חדש
        current_q = self.q_table[state_key][action]
        
        # אם המשחק הסתיים, אין מצב הבא
        if done:
            max_next_q = 0
        else:
            max_next_q = np.max(self.q_table[next_state_key])
        
        # נוסחת עדכון Q-Learning
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        
        # עדכון הערך בטבלה
        self.q_table[state_key][action] = new_q
        
        # עדכון שיעור האקספלורציה
        if done:
            self.exploration_rate = max(self.min_exploration_rate, 
                                       self.exploration_rate * self.exploration_decay)
    
    def train(self, episodes=1000, max_steps=None, render_interval=100):
        """
        אימון הסוכן
        """
        episode_rewards = []
        
        for episode in range(episodes):
            state, _ = self.env.reset()
            episode_reward = 0
            done = False
            step = 0
            
            while not done:
                # בחירת פעולה
                action = self.choose_action(state)
                
                # ביצוע הפעולה
                next_state, reward, done, _, info = self.env.step(action)
                
                # עדכון טבלת Q
                self.update_q_table(state, action, reward, next_state, done)
                
                # עדכון המצב והתגמול המצטבר
                state = next_state
                episode_reward += reward
                step += 1
                
                # הגבלת מספר הצעדים
                if max_steps and step >= max_steps:
                    break
            
            # שמירת התגמול המצטבר
            episode_rewards.append(episode_reward)
            
            # הצגת התקדמות
            if episode % render_interval == 0:
                print(f"אפיזודה {episode}/{episodes}, תגמול: {episode_reward:.2f}, "
                      f"אקספלורציה: {self.exploration_rate:.4f}, רווח: {info['total_profit_percent']:.2f}%")
        
        return episode_rewards
    
    def test(self, episodes=10):
        """
        בדיקת ביצועי הסוכן
        """
        total_profits = []
        
        for episode in range(episodes):
            state, _ = self.env.reset()
            done = False
            
            while not done:
                # בחירת הפעולה הטובה ביותר (ללא אקספלורציה)
                state_key = self._get_state_key(state)
                
                if state_key in self.q_table:
                    action = np.argmax(self.q_table[state_key])
                else:
                    action = 0  # החזקה כברירת מחדל
                
                # ביצוע הפעולה
                state, _, done, _, info = self.env.step(action)
            
            # הצגת תוצאות
            print(f"אפיזודה {episode+1}/{episodes}, רווח: {info['total_profit_percent']:.2f}%")
            total_profits.append(info['total_profit_percent'])
        
        # סיכום תוצאות
        avg_profit = np.mean(total_profits)
        print(f"\nרווח ממוצע: {avg_profit:.2f}%")
        
        return total_profits
    
    def plot_results(self, episode_rewards):
        """
        הצגת תוצאות האימון
        """
        plt.figure(figsize=(10, 6))
        plt.plot(episode_rewards)
        plt.title('תגמול מצטבר לאורך האימון')
        plt.xlabel('אפיזודה')
        plt.ylabel('תגמול מצטבר')
        plt.grid(True)
        plt.savefig('/home/ubuntu/rl_trading_system/results/training_rewards.png')
        plt.close()
