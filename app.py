import streamlit as st
import pandas as pd
import requests
import ta
from datetime import datetime, timedelta
import os
from telegram import Bot
import asyncio
import numpy as np

# API ключ Alpha Vantage и Telegram токен из секретов Streamlit
ALPHA_VANTAGE_API_KEY = st.secrets.get("ALPHA_VANTAGE_API_KEY", "NFNQC9SQK6XF7CY3")
TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", None)

# Функция для получения данных по акциям через Alpha Vantage
def fetch_stock_data(ticker):
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if "Time Series (Daily)" in data:
            df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index").astype(float)
            df.index = pd.to_datetime(df.index)
            df = df.rename(columns={"4. close": "Close", "5. volume": "Volume"})
            return df[["Close", "Volume"]]
        return None
    except:
        return None

# Функция для получения bid/ask по акциям
def fetch_stock_quote(ticker):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if "Global Quote" in data:
            quote = data["Global Quote"]
            return float(quote.get("08. bid", 0)), float(quote.get("09. ask", 0))
        return None, None
    except:
        return None, None

# Функция для получения данных по криптовалютам через CoinGecko
def fetch_crypto_data(coin_id, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame({
            'Date': pd.to_datetime([x[0]/1000 for x in data['prices']], unit='s'),
            'Close': [x[1] for x in data['prices']],
            'Volume': [x[1] for x in data['total_volumes']]
        })
        df.set_index('Date', inplace=True)
        return df
    return None

# Функция для ресемплинга данных на 7-часовой таймфрейм
def resample_to_7h(df):
    df_7h = df.resample('7H').agg({'Close': 'last', 'Volume': 'sum'})
    return df_7h.dropna()

# Функция для расчета углов Ганна (упрощенно)
def calculate_gann_angles(df):
    if len(df) < 2:
        return None
    price_diff = df['Close'].diff().iloc[-1]
    time_diff = 1  # Один 7-часовой период
    slope = price_diff / time_diff
    if abs(slope) > 0.5:
        return "Сильный тренд"
    elif abs(slope) > 0.2:
        return "Умеренный тренд"
    else:
        return "Слабый тренд"

# Функция для анализа тренда и расчета скора
def analyze_trend(df, bid=None, ask=None):
    if df is None or len(df) < 14:
        return "Неизвестно", 0
    
    # Ресемплинг на 7-часовой таймфрейм
    df_7h = resample_to_7h(df)
    
    # Расчет индикаторов
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['CCI'] = ta.trend.CCIIndicator(df['Close'], df['Close'], df['Close'], window=20).cci()
    df['EMA50'] = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
    df['EMA200'] = ta.trend.EMAIndicator(df['Close'], window=200).ema_indicator()
    df['MACD'] = ta.trend.MACD(df['Close']).macd_diff()
    df['Volume_MA'] = df['Volume'].rolling(window=10).mean()
    gann_trend = calculate_gann_angles(df_7h)
    
    # Последние значения
    latest_rsi = df['RSI'].iloc[-1]
    latest_cci = df['CCI'].iloc[-1]
    latest_ema50 = df['EMA50'].iloc[-1]
    latest_ema200 = df['EMA200'].iloc[-1]
    latest_macd = df['MACD'].iloc[-1]
    latest_volume = df['Volume'].iloc[-1]
    volume_ma = df['Volume_MA'].iloc[-1]
    
    # Логика тренда
    score = 0
    confirmations = 0
    trend = "Распределение"  # По умолчанию
    
    # RSI и CCI
    if latest_rsi > 70 and latest_cci > 100:
        trend = "Восходящий тренд"
        confirmations += 1
        score += 0.3
    elif latest_rsi < 30 and latest_cci < -100:
        trend = "Нисходящий тренд"
        confirmations += 1
        score += 0.3
    
    # Пересечение EMA
    if latest_ema50 > latest_ema200:
        if trend == "Восходящий тренд":
            confirmations += 1
        trend = "Восходящий тренд"
        score += 0.3
    elif latest_ema50 < latest_ema200:
        if trend == "Нисходящий тренд":
            confirmations += 1
        trend = "Нисходящий тренд"
        score += 0.3
    
    # MACD
    if latest_macd > 0 and trend == "Восходящий тренд":
        confirmations += 1
        score += 0.2
    elif latest_macd < 0 and trend == "Нисходящий тренд":
        confirmations += 1
        score += 0.2
    
    # Объем
    if latest_volume > volume_ma * 1.5:
        if trend == "Восходящий тренд":
            confirmations += 1
        trend = "Накопление"
        score += 0.2
    
    # Bid/Ask (для акций)
    if bid and ask and bid > 0 and ask > 0:
        spread = ask - bid
        if spread < df['Close'].iloc[-1] * 0.01:  # Узкий спред указывает на спрос
            if trend == "Восходящий тренд":
                confirmations += 1
            score += 0.2
    
    # Углы Ганна
    if gann_trend == "Сильный тренд" and trend in ["Восходящий тренд", "Нисходящий тренд"]:
        confirmations += 1
        score += 0.2
    
    # Требуется минимум 3 подтверждения
    if confirmations < 3:
        trend = "Неопределенно"
        score = max(score - 0.3, 0)
    
    return trend, score

# Асинхронная функция для отправки сообщения в Telegram через @ern1kko_bot
async def send_telegram_report(chat_id, message):
    if TELEGRAM_BOT_TOKEN:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=chat_id, text=message)
    else:
        st.write("Токен Telegram-бота не настроен.")

# Streamlit приложение
st.title(">tS|TQTVLSYSTEM")
st.subheader("Анализ трендов и лучших активов")

# Выбор рынка
market = st.selectbox("Выберите рынок", ["Акции", "Криптовалюты"])
st.write("Бесплатный уровень: просмотр тренда рынка. Премиум: топ-активы и отчеты в Telegram (скоро).")

# Списки активов
stock_tickers = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"]
crypto_ids = ["bitcoin", "ethereum", "solana", "cardano", "polkadot"]

# Анализ тренда рынка
if market == "Акции":
    assets = stock_tickers
    data_fetcher = fetch_stock_data
    quote_fetcher = fetch_stock_quote
else:
    assets = crypto_ids
    data_fetcher = fetch_crypto_data
    quote_fetcher = lambda x: (None, None)  # Нет bid/ask для криптовалют в бесплатном API

# Расчет общего тренда рынка
trend_scores = []
for asset in assets:
    df = data_fetcher(asset)
    bid, ask = quote_fetcher(asset)
    if df is not None:
        trend, score = analyze_trend(df, bid, ask)
        trend_scores.append((asset, trend, score))

# Агрегация тренда рынка
if trend_scores:
    market_trend = max(set([x[1] for x in trend_scores]), key=[x[1] for x in trend_scores].count)
    st.write(f"**Тренд рынка**: {market_trend}")
else:
    st.write("**Тренд рынка**: Не удалось определить (данные недоступны)")

# Премиум-функция: топ-активы
if st.button("Показать топ-активы (Премиум)"):
    st.write("Премиум-функция: Топ-5 активов на основе анализа тренда.")
    if trend_scores:
        top_assets = sorted(trend_scores, key=lambda x: x[2], reverse=True)[:5]
        st.write("**Топ-активы**:")
        for asset, trend, score in top_assets:
            st.write(f"- {asset}: {trend} (Скор: {score:.2f})")
    else:
        st.write("Данные для топ-активов недоступны.")

# Отправка отчета в Telegram
chat_id_input = st.text_input("Введите ваш Telegram Chat ID (для теста)")
if st.button("Отправить отчет в Telegram (Премиум)"):
    st.write("Премиум-функция: Ежедневный отчет о тренде рынка.")
    if trend_scores and TELEGRAM_BOT_TOKEN and chat_id_input:
        top_assets = sorted(trend_scores, key=lambda x: x[2], reverse=True)[:3]
        message = f"Рынок: {market}\nТренд: {market_trend}\nТоп-активы: {', '.join([x[0] for x in top_assets])}"
        asyncio.run(send_telegram_report(chat_id_input, message))
        st.write("Отчет отправлен в Telegram (@ern1kko_bot).")
    else:
        st.write("Настройте токен Telegram-бота в секретах Streamlit или введите Chat ID.")

st.write("**Примечание**: Подробная аналитика и отчеты в Telegram доступны в Премиум-уровне (скоро).")
