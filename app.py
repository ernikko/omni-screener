import streamlit as st
import pandas as pd
import requests
import ta
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np
from telegram import Bot
import time

# API ключ и Telegram токен
ALPHA_VANTAGE_API_KEY = st.secrets.get("ALPHA_VANTAGE_API_KEY", "NFNQC9SQK6XF7CY3")
TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", None)

# Кэширование данных
@st.cache_data(ttl=300)
def fetch_stock_data_cached(ticker, use_alpha=True):
    if use_alpha:
        try:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=compact&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            if "Error Message" in data or "Note" in data.get("Error Message", ""):
                st.warning(f"Alpha Vantage ошибка для {ticker}: {data.get('Note', 'Rate limit?')}")
                return None
            if "Time Series (Daily)" in data:
                df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index").astype(float)
                df.index = pd.to_datetime(df.index)
                df = df.rename(columns={"4. close": "Close", "5. volume": "Volume", "2. high": "High", "3. low": "Low"})
                return df[["Close", "Volume", "High", "Low"]].sort_index()[-30:]  # 1 месяц
        except Exception as e:
            st.warning(f"Ошибка Alpha Vantage для {ticker}: {str(e)}")
    
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1mo")
        if not df.empty:
            df = df[["Close", "Volume", "High", "Low"]]
            return df
    except Exception as e:
        st.warning(f"Ошибка yfinance для {ticker}: {str(e)}")
    return None

@st.cache_data(ttl=300)
def fetch_stock_quote_cached(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        bid = info.get("bid", None)
        ask = info.get("ask", None)
        if bid and ask:
            return float(bid), float(ask)
        return None, None
    except:
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

@st.cache_data(ttl=300)
def fetch_crypto_data(coin_id, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame({
            'Date': pd.to_datetime([x[0]/1000 for x in data['prices']], unit='s'),
            'Close': [x[1] for x in data['prices']],
            'Volume': [x[1] for x in data['total_volumes']],
            'High': [x[1] for x in data['prices']],  # Приблизительно (CoinGecko не дает High/Low)
            'Low': [x[1] for x in data['prices']]
        })
        df.set_index('Date', inplace=True)
        return df
    return None

def resample_to_7h(df):
    df_7h = df.resample('7H').agg({'Close': 'last', 'Volume': 'sum', 'High': 'max', 'Low': 'min'})
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
    if df is None or len(df) < 30:
        return "Неизвестно", 0, []
    
    df_7h = resample_to_7h(df)
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['CCI'] = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close'], window=20).cci()
    df['EMA50'] = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
    df['EMA100'] = ta.trend.EMAIndicator(df['Close'], window=100).ema_indicator()
    df['MACD'] = ta.trend.MACD(df['Close']).macd_diff()
    df['Volume_MA'] = df['Volume'].rolling(window=10).mean()
    df['Stochastic'] = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close']).stoch()
    df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = ta.volatility.BollingerBands(df['Close']).bollinger_hband(), ta.volatility.BollingerBands(df['Close']).bollinger_mavg(), ta.volatility.BollingerBands(df['Close']).bollinger_lband()
    df['VWAP'] = ta.volume.VolumeWeightedAveragePrice(df['High'], df['Low'], df['Close'], df['Volume']).volume_weighted_average_price()
    df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
    gann_trend = calculate_gann_angles(df_7h)
    
    latest_rsi = df['RSI'].iloc[-1]
    latest_cci = df['CCI'].iloc[-1]
    latest_ema50 = df['EMA50'].iloc[-1]
    latest_ema100 = df['EMA100'].iloc[-1]
    latest_macd = df['MACD'].iloc[-1]
    latest_volume = df['Volume'].iloc[-1]
    volume_ma = df['Volume_MA'].iloc[-1]
    latest_stoch = df['Stochastic'].iloc[-1]
    latest_price = df['Close'].iloc[-1]
    latest_bb_upper = df['BB_Upper'].iloc[-1]
    latest_bb_lower = df['BB_Lower'].iloc[-1]
    latest_vwap = df['VWAP'].iloc[-1]
    latest_atr = df['ATR'].iloc[-1]
    
    score = 0
    confirmations = 0
    trend = "Распределение"
    debug_info = []
    
    if latest_rsi > 70 and latest_cci > 100:
        trend = "Восходящий тренд"
        confirmations += 1
        score += 0.2
        debug_info.append(f"RSI={latest_rsi:.2f}>70, CCI={latest_cci:.2f}>100: Восходящий")
    elif latest_rsi < 30 and latest_cci < -100:
        trend = "Нисходящий тренд"
        confirmations += 1
        score += 0.2
        debug_info.append(f"RSI={latest_rsi:.2f}<30, CCI={latest_cci:.2f}<-100: Нисходящий")
    
    if latest_ema50 > latest_ema100:
        if trend == "Восходящий тренд":
            confirmations += 1
        trend = "Восходящий тренд"
        score += 0.2
        debug_info.append(f"EMA50={latest_ema50:.2f}>EMA100={latest_ema100:.2f}: Восходящий")
    elif latest_ema50 < latest_ema100:
        if trend == "Нисходящий тренд":
            confirmations += 1
        trend = "Нисходящий тренд"
        score += 0.2
        debug_info.append(f"EMA50={latest_ema50:.2f}<EMA100={latest_ema100:.2f}: Нисходящий")
    
    if latest_macd > 0 and trend == "Восходящий тренд":
        confirmations += 1
        score += 0.15
        debug_info.append(f"MACD={latest_macd:.2f}>0: Восходящий")
    elif latest_macd < 0 and trend == "Нисходящий тренд":
        confirmations += 1
        score += 0.15
        debug_info.append(f"MACD={latest_macd:.2f}<0: Нисходящий")
    
    if latest_volume > volume_ma * 1.5:
        if trend == "Восходящий тренд":
            confirmations += 1
        trend = "Накопление"
        score += 0.15
        debug_info.append(f"Volume={latest_volume:.2f}>1.5*MA={volume_ma:.2f}: Накопление")
    
    if bid and ask and bid > 0 and ask > 0:
        spread = ask - bid
        if spread < latest_price * 0.01:
            if trend == "Восходящий тренд":
                confirmations += 1
            score += 0.15
            debug_info.append(f"Bid/Ask спред={spread:.2f}<1% цены: Восходящий")
    
    if gann_trend == "Сильный тренд" and trend in ["Восходящий тренд", "Нисходящий тренд"]:
        confirmations += 1
        score += 0.15
        debug_info.append(f"Gann: {gann_trend}")
    
    if latest_stoch > 80:
        if trend == "Восходящий тренд":
            confirmations += 1
        trend = "Восходящий тренд"
        score += 0.1
        debug_info.append(f"Stochastic={latest_stoch:.2f}>80: Восходящий")
    elif latest_stoch < 20:
        if trend == "Нисходящий тренд":
            confirmations += 1
        trend = "Нисходящий тренд"
        score += 0.1
        debug_info.append(f"Stochastic={latest_stoch:.2f}<20: Нисходящий")
    
    if latest_price > latest_bb_upper:
        if trend == "Восходящий тренд":
            confirmations += 1
        trend = "Восходящий тренд"
        score += 0.1
        debug_info.append(f"Price={latest_price:.2f}>BB_Upper={latest_bb_upper:.2f}: Восходящий")
    elif latest_price < latest_bb_lower:
        if trend == "Нисходящий тренд":
            confirmations += 1
        trend = "Нисходящий тренд"
        score += 0.1
        debug_info.append(f"Price={latest_price:.2f}<BB_Lower={latest_bb_lower:.2f}: Нисходящий")
    
    if latest_price > latest_vwap:
        if trend == "Восходящий тренд":
            confirmations += 1
        score += 0.1
        debug_info.append(f"Price={latest_price:.2f}>VWAP={latest_vwap:.2f}: Восходящий")
    elif latest_price < latest_vwap:
        if trend == "Нисходящий тренд":
            confirmations += 1
        score += 0.1
        debug_info.append(f"Price={latest_price:.2f}<VWAP={latest_vwap:.2f}: Нисходящий")
    
    if confirmations < 3:
        trend = "Неопределенно"
        score = max(score - 0.2, 0)
        debug_info.append(f"Подтверждений={confirmations}<3: Неопределенно")
    
    return trend, score, debug_info

def send_telegram_report(chat_id, message):
    if not TELEGRAM_BOT_TOKEN:
        return "Ошибка: Токен бота не загружен (проверьте secrets в Streamlit)."
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.get_me()  # Проверка токена
        bot.send_message(chat_id=chat_id, text=message)
        return "Сообщение отправлено успешно!"
    except Exception as e:
        return f"Ошибка отправки: {str(e)} (проверьте токен или Chat ID)"

# Streamlit приложение
st.title(">tS|TQTVLSYSTEM")
st.subheader("Анализ трендов и лучших активов")

# Отладка
with st.expander("Отладка: Статус API и токена"):
    st.write(f"**Alpha Vantage ключ**: {'Загружен' if ALPHA_VANTAGE_API_KEY else 'Не загружен'}")
    st.write(f"**Telegram токен**: {'Загружен' if TELEGRAM_BOT_TOKEN else 'Не загружен'}")
    if TELEGRAM_BOT_TOKEN:
        try:
            bot = Bot(token=TELEGRAM_BOT_TOKEN)
            bot_info = bot.get_me()
            st.write(f"**Бот активен**: @{bot_info.username}")
        except Exception as e:
            st.error(f"**Ошибка проверки бота**: {str(e)}")
    if st.button("Тест Alpha Vantage (1 запрос)"):
        test_df = fetch_stock_data_cached("AAPL")
        st.write(f"Тест AAPL: {'Успех' if test_df is not None else 'Ошибка'}")

# Выбор рынка
market = st.selectbox("Выберите рынок", ["Акции", "Криптовалюты"])
st.write("Бесплатный уровень: просмотр тренда рынка. Премиум: топ-активы и отчеты в Telegram (скоро).")

# Списки активов (расширенные)
stock_tickers = [
    "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "JPM", "V",
    "WMT", "UNH", "MA", "PG", "HD", "DIS", "BAC", "INTC", "CMCSA", "VZ",
    "PFE", "KO", "PEP", "MRK", "T", "CSCO", "XOM", "CVX", "ABBV", "NKE",
    "ADBE", "CRM", "NFLX", "AMD", "ORCL", "IBM", "QCOM", "TXN", "AMGN", "GILD",
    "SBUX", "MMM", "GE", "CAT", "BA", "HON", "SPG", "LMT", "UPS", "LOW"
]
crypto_ids = [
    "bitcoin", "ethereum", "solana", "cardano", "polkadot", "binancecoin", "ripple", "dogecoin", "avalanche-2", "chainlink",
    "litecoin", "bitcoin-cash", "stellar", "cosmos", "algorand", "tezos", "eos", "neo", "iota", "tron",
    "vechain", "theta-token", "dash", "zcash", "monero", "maker", "compound-governance-token", "aave", "uniswap", "pancakeswap-token",
    "sushi", "yearn-finance", "curve-dao-token", "synthetix-network-token", "1inch", "basic-attention-token", "enjincoin", "decentraland", "the-graph", "axie-infinity",
    "chiliz", "hedera-hashgraph", "quant-network", "filecoin", "arweave", "flow", "internet-computer", "elrond-erd-2", "kava", "kusama"
]

# Анализ
if market == "Акции":
    assets = stock_tickers
    data_fetcher = lambda x: fetch_stock_data_cached(x)
    quote_fetcher = fetch_stock_quote_cached
else:
    assets = crypto_ids
    data_fetcher = fetch_crypto_data
    quote_fetcher = lambda x: (None, None)

trend_scores = []
successful_fetches = 0
debug_trends = []
for asset in assets[:50]:  # Ограничим 50 для скорости
    df = data_fetcher(asset)
    if df is not None:
        successful_fetches += 1
    bid, ask = quote_fetcher(asset)
    if df is not None:
        trend, score, debug_info = analyze_trend(df, bid, ask)
        trend_scores.append((asset, trend, score))
        debug_trends.append((asset, debug_info))
    time.sleep(0.2)  # Пауза для API

st.info(f"Успешно загружено данных: {successful_fetches}/{min(len(assets), 50)} активов")

with st.expander("Отладка: Индикаторы по активам"):
    for asset, debug_info in debug_trends:
        st.write(f"**{asset}**:")
        for info in debug_info:
            st.write(f"- {info}")

if trend_scores:
    market_trend = max(set([x[1] for x in trend_scores]), key=[x[1] for x in trend_scores].count)
    st.success(f"**Тренд рынка**: {market_trend}")
else:
    st.error("**Тренд рынка**: Не удалось определить (проверьте отладку).")

if st.button("Показать топ-активы (Премиум)"):
    if trend_scores:
        top_assets = sorted(trend_scores, key=lambda x: x[2], reverse=True)[:10]  # Топ-10
        st.write("**Топ-активы**:")
        for asset, trend, score in top_assets:
            st.write(f"- {asset}: {trend} (Скор: {score:.2f})")
    else:
        st.warning("Нет данных для топ-активов.")

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
