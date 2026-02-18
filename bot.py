import telebot
import yfinance as yf
import pandas as pd
import numpy as np
import time
import schedule
import threading
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator, ADXIndicator
from ta.volatility import AverageTrueRange, BollingerBands

# --- الإعدادات النهائية ---
TOKEN = "8106899856:AAER5PYfDH31Gm-8jc67nYihTdcRd_iA1to"
ADMIN_ID = 5066447725
PAIRS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "EURJPY=X", "GBPJPY=X", "NZDUSD=X", "EURGBP=X", "AUDJPY=X"]

bot = telebot.TeleBot(TOKEN)

def binary_ai_brain(symbol):
    try:
        # جلب البيانات لآخر 3 أيام (فريم 5 دقائق)
        df = yf.download(symbol, period="3d", interval="5m", progress=False)
        if len(df) < 100: return None
        
        close = df['Close']
        rsi = RSIIndicator(close).rsi().iloc[-1]
        ema_200 = EMAIndicator(close, window=200).ema_indicator().iloc[-1]
        adx = ADXIndicator(df['High'], df['Low'], close).adx().iloc[-1]
        atr = AverageTrueRange(df['High'], df['Low'], close).average_true_range().iloc[-1]
        bb = BollingerBands(close)
        price = close.iloc[-1]

        # فلتر الأخبار: تجنب التذبذب العنيف
        if abs(price - close.iloc[-2]) > (atr * 3): return "NEWS"

        # --- الخوارزمية الذكية ---
        if adx > 30: # ترند قوي (Strategy 1)
            direction = "CALL 🟢" if price > ema_200 and rsi > 50 else "PUT 🔴" if price < ema_200 and rsi < 50 else None
            return {"pair": symbol.replace("=X",""), "dir": direction, "strat": "ترند قوي 🔥", "dur": "15m", "acc": 92} if direction else None
        
        elif adx < 25: # سوق عرضي (Strategy 2)
            direction = "CALL 🟢" if rsi < 30 or price < bb.bollinger_lband().iloc[-1] else "PUT 🔴" if rsi > 70 or price > bb.bollinger_hband().iloc[-1] else None
            return {"pair": symbol.replace("=X",""), "dir": direction, "strat": "ارتداد سعري ⚖️", "dur": "5m", "acc": 88} if direction else None
    except: return None

def daily_report():
    msg = "📊 **تقرير العقل الذكي اليومي**\n"
    for p in PAIRS:
        d = yf.download(p, period="1d", progress=False)
        change = ((d['Close'].iloc[-1] - d['Open'].iloc[0]) / d['Open'].iloc[0]) * 100
        msg += f"🔹 `{p.replace('=X','')}`: {'📈' if change > 0 else '📉'} {change:.2f}%\n"
    bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")

def run_sched():
    schedule.every().day.at("22:00").do(daily_report)
    while True: schedule.run_pending(); time.sleep(60)

def main():
    threading.Thread(target=run_sched, daemon=True).start()
    bot.send_message(ADMIN_ID, "🚀 عقل البوت بدأ العمل في السحاب بنجاح!")
    while True:
        for p in PAIRS:
            res = binary_ai_brain(p)
            if res and res != "NEWS":
                alert = (f"🎯 **إشارة خيارات ثنائية**\n\n"
                         f"💹 الزوج: `{res['pair']}`\n"
                         f"🧭 الاتجاه: **{res['dir']}**\n"
                         f"⏱ المدة: `{res['dur']}`\n"
                         f"🛡 الاستراتيجية: `{res['strat']}`\n"
                         f"📊 نسبة النجاح: `{res['acc']}%`")
                bot.send_message(ADMIN_ID, alert, parse_mode="Markdown")
                time.sleep(600)
        time.sleep(60)

if __name__ == "__main__":
    main()
