import streamlit as st
import pandas as pd
import requests
import ta
from datetime import datetime, timedelta
import yfinance as yf  # Fallback для акций
import numpy as np
from telegram import Bot  # Синхронный Bot без async
import time  # Для кэширования

# API ключ Alpha Vantage и Telegram токен из секретов Streamlit
ALPHA_VANTAGE_API_KEY = st.secrets.get("ALPHA_VANTAGE_API_KEY", "NFNQC9SQK6XF7CY3")
TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", None)

# Кэш для данных (чтобы не запрашивать заново)
@st.cache_data(ttl=300)  # Кэш на 5 минут
def fetch_stock_data_cached(ticker, use_alpha=True):
    if use_alpha:
        # Попытка Alpha Vantage
        try:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            if "Error Message" in data or "Note" in data.get("Error Message", ""):
                st.warning(f"Alpha Vantage ошибка для {ticker}: {data.get('Note', 'Rate limit?')}")
                return None
            if "Time Series (Daily)" in data:
                df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index").astype(float)
                df.index = pd.to_datetime(df.index)
                df = df.rename(columns={"4. close": "Close", "5. volume": "Volume"})
                return df[["Close", "Volume"]].sort_index()
        except Exception as e:
            st.warning(f"Ошибка Alpha Vantage для {ticker}: {str(e)}")
    
    # Fallback на yfinance
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        if not df.empty:
            df = df[["Close", "Volume"]]
            return df
    except Exception as e:
        st.warning(f"Ошибка yfinance для {ticker}: {str(e)}")
    return None

@st.cache_data(ttl=300)
def fetch_stock_quote_cached(ticker):
    # Bid/Ask через yfinance (fallback, так как Alpha может быть лимитирован)
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        bid = info.get("bid", None)
        ask = info.get("ask", None)
        if bid and ask:
            return float(bid), float(ask)
        return None, None
    except:
        # Fallback на Alpha
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            if "Error Message" in data:
                return None, None
            if "Global Quote" in data:
                quote = data["Global Quote"]
                return float(quote.get("08. bid", 0)), float(quote.get("09. ask", 0))
        except:
            return None, None

# Функция для крипты (без изменений)
@st.cache_data(ttl=300)
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

# Функции для анализа (без изменений, кроме debug)
def resample_to_7h(df):
    df_7h = df.resample('7H').agg({'Close': 'last', 'Volume': 'sum'})
    return df_7h.dropna()

def calculate_gann_angles(df):
    if len(df) < 2:
        return None
    price_diff = df['Close'].diff().iloc[-1]
    time_diff = 1
    slope = price_diff / time_diff
    if abs(slope) > 0.5:
        return "Сильный тренд"
    elif abs(slope) > 0.2:
        return "Умеренный тренд"
    else:
        return "Слабый тренд"

def analyze_trend(df, bid=None, ask=None):
    if df is None or len(df) < 14:
        return "Неизвестно", 0
    
    df_7h = resample_to_7h(df)
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['CCI'] = ta.trend.CCIIndicator(df['Close'], df['Close'], df['Close'], window=20).cci()
    df['EMA50'] = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
    df['EMA200'] = ta.trend.EMAIndicator(df['Close'], window=200).ema_indicator()
    df['MACD'] = ta.trend.MACD(df['Close']).macd_diff()
    df['Volume_MA'] = df['Volume'].rolling(window=10).mean()
    gann_trend = calculate_gann_angles(df_7h)
    
    latest_rsi = df['RSI'].iloc[-1]
    latest_cci = df['CCI'].iloc[-1]
    latest_ema50 = df['EMA50'].iloc[-1]
    latest_ema200 = df['EMA200'].iloc[-1]
    latest_macd = df['MACD'].iloc[-1]
    latest_volume = df['Volume'].iloc[-1]
    volume_ma = df['Volume_MA'].iloc[-1]
    
    score = 0
    confirmations = 0
    trend = "Распределение"
    
    if latest_rsi > 70 and latest_cci > 100:
        trend = "Восходящий тренд"
        confirmations += 1
        score += 0.3
    elif latest_rsi < 30 and latest_cci < -100:
        trend = "Нисходящий тренд"
        confirmations += 1
        score += 0.3
    
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
    
    if latest_macd > 0 and trend == "Восходящий тренд":
        confirmations += 1
        score += 0.2
    elif latest_macd < 0 and trend == "Нисходящий тренд":
        confirmations += 1
        score += 0.2
    
    if latest_volume > volume_ma * 1.5:
        if trend == "Восходящий тренд":
            confirmations += 1
        trend = "Накопление"
        score += 0.2
    
    if bid and ask and bid > 0 and ask > 0:
        spread = ask - bid
        if spread < df['Close'].iloc[-1] * 0.01:
            if trend == "Восходящий тренд":
                confirmations += 1
            score += 0.2
    
    if gann_trend == "Сильный тренд" and trend in ["Восходящий тренд", "Нисходящий тренд"]:
        confirmations += 1
        score += 0.2
    
    if confirmations < 3:
        trend = "Неопределенно"
        score = max(score - 0.3, 0)
    
    return trend, score

# Синхронная отправка в Telegram (без async)
def send_telegram_report(chat_id, message):
    if not TELEGRAM_BOT_TOKEN:
        return "Токен бота не загружен из секретов."
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=chat_id, text=message)
        return "Сообщение отправлено успешно!"
    except Exception as e:
        return f"Ошибка отправки: {str(e)} (проверьте токен и Chat ID)"

# Streamlit приложение
st.title(">tS|TQTVLSYSTEM")
st.subheader("Анализ трендов и лучших активов")

# Отладка (показать статус)
with st.expander("Отладка: Статус API и токена"):
    st.write(f"**Alpha Vantage ключ загружен**: {'Да' if ALPHA_VANTAGE_API_KEY else 'Нет'}")
    st.write(f"**Telegram токен загружен**: {'Да' if TELEGRAM_BOT_TOKEN else 'Нет'} (не показываем значение для безопасности)")
    if st.button("Тест Alpha Vantage (1 запрос)"):
        test_df = fetch_stock_data_cached("AAPL")
        st.write(f"Тест AAPL: {'Успех' if test_df is not None else 'Ошибка'}")

# Выбор рынка
market = st.selectbox("Выберите рынок", ["Акции", "Криптовалюты"])
st.write("Бесплатный уровень: просмотр тренда рынка. Премиум: топ-активы и отчеты в Telegram (скоро).")

# Списки активов
stock_tickers = ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN"]
crypto_ids = ["bitcoin", "ethereum", "solana", "cardano", "polkadot"]

# Анализ
if market == "Акции":
    assets = stock_tickers
    data_fetcher = lambda x: fetch_stock_data_cached(x)
    quote_fetcher = fetch_stock_quote_cached
else:
    assets = crypto_ids
    data_fetcher = fetch_crypto_data
    quote_fetcher = lambda x: (None, None)

# Расчет трендов
trend_scores = []
successful_fetches = 0
for asset in assets:
    df = data_fetcher(asset)
    if df is not None:
        successful_fetches += 1
    bid, ask = quote_fetcher(asset)
    if df is not None:
        trend, score = analyze_trend(df, bid, ask)
        trend_scores.append((asset, trend, score))
    time.sleep(1)  # Пауза для API-лимитов

st.info(f"Успешно загружено данных: {successful_fetches}/{len(assets)} активов")

# Агрегация тренда
if trend_scores:
    market_trend = max(set([x[1] for x in trend_scores]), key=[x[1] for x in trend_scores].count)
    st.success(f"**Тренд рынка**: {market_trend}")
else:
    st.error("**Тренд рынка**: Не удалось определить (проверьте отладку выше). Для акций — лимит Alpha Vantage? Попробуйте крипту.")

# Премиум: Топ-активы
if st.button("Показать топ-активы (Премиум)"):
    if trend_scores:
        top_assets = sorted(trend_scores, key=lambda x: x[2], reverse=True)[:5]
        st.write("**Топ-активы**:")
        for asset, trend, score in top_assets:
            st.write(f"- {asset}: {trend} (Скор: {score:.2f})")
    else:
        st.warning("Нет данных для топ-активов.")

# Telegram
chat_id_input = st.text_input("Введите ваш Telegram Chat ID (для теста)", value="370110317")
if st.button("Отправить отчет в Telegram (Премиум)"):
    if trend_scores:
        top_assets = sorted(trend_scores, key=lambda x: x[2], reverse=True)[:3]
        message = f"🚀 >tS|TQTVLSYSTEM Отчет\nРынок: {market}\nТренд: {market_trend}\nТоп-активы: {', '.join([x[0] for x in top_assets])}\nВремя: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        result = send_telegram_report(chat_id_input, message)
        st.write(result)
    else:
        st.warning("Нет данных для отчета.")

st.write("**Примечание**: Подробная аналитика и отчеты в Telegram доступны в Премиум-уровне (скоро).")
