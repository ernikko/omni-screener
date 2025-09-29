import streamlit as st
import pandas as pd
import requests
import ta
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np
import time

# API ключ и Telegram токен
ALPHA_VANTAGE_API_KEY = st.secrets.get("ALPHA_VANTAGE_API_KEY", "NFNQC9SQK6XF7CY3")
TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", None)
ADMIN_KEY = st.secrets.get("ADMIN_KEY", "mysecretkey123")  # Установите в secrets

# Кэширование данных
@st.cache_data(ttl=300)
def fetch_stock_data_cached(ticker, use_alpha=True):
    if use_alpha:
        try:
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            if "Error Message" in data or "Note" in data.get("Error Message", ""):
                st.warning(f"Alpha Vantage ошибка для {ticker}: {data.get('Note', 'Rate limit?')}")
                return None
            if "Time Series (Daily)" in data:
                df = pd.DataFrame.from_dict(data["Time Series (Daily)"], orient="index").astype(float)
                df.index = pd.to_datetime(df.index)
                df = df.rename(columns={"4. close": "Close", "5. volume": "Volume", "2. high": "High", "3. low": "Low"})
                return df[["Close", "Volume", "High", "Low"]].sort_index()
        except Exception as e:
            st.warning(f"Ошибка Alpha Vantage для {ticker}: {str(e)}")
    
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y", interval="1d")
        if not df.empty:
            df = df[["Close", "Volume", "High", "Low"]]
            return df
        else:
            st.warning(f"Нет данных для {ticker} в yfinance")
            return None
    except Exception as e:
        st.warning(f"Ошибка yfinance для {ticker}: {str(e)}")
    return None

@st.cache_data(ttl=300)
def fetch_stock_data_7h(ticker):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="60d", interval="1h")
        if not df.empty:
            df = df[["Close", "Volume", "High", "Low"]]
            df_7h = df.resample('7H').agg({'Close': 'last', 'Volume': 'sum', 'High': 'max', 'Low': 'min'}).dropna()
            return df_7h
        else:
            st.warning(f"Нет 7H данных для {ticker} в yfinance")
            return None
    except Exception as e:
        st.warning(f"Ошибка yfinance (7H) для {ticker}: {str(e)}")
    return None

@st.cache_data(ttl=300)
def fetch_stock_quote_cached(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        bid = info.get("bid", None)
        ask = info.get("ask", None)
        pe_ratio = info.get("trailingPE", None)
        eps = info.get("trailingEps", None)
        if bid and ask:
            return float(bid), float(ask), pe_ratio, eps
        return None, None, None, None
    except:
        try:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url)
            data = response.json()
            if "Error Message" in data:
                return None, None, None, None
            if "Global Quote" in data:
                quote = data["Global Quote"]
                return float(quote.get("08. bid", 0)), float(quote.get("09. ask", 0)), None, None
        except:
            return None, None, None, None

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

def calculate_fibonacci_levels(df):
    high = df['High'].max()
    low = df['Low'].min()
    diff = high - low
    levels = {
        "23.6%": high - 0.236 * diff,
        "38.2%": high - 0.382 * diff,
        "50%": high - 0.5 * diff,
        "61.8%": high - 0.618 * diff
    }
    latest_price = df['Close'].iloc[-1]
    if latest_price > levels["23.6%"]:
        return "Восходящий (выше 23.6%)"
    elif latest_price < levels["61.8%"]:
        return "Нисходящий (ниже 61.8%)"
    return None

def analyze_trend(df, df_7h, bid=None, ask=None, pe_ratio=None, eps=None):
    if df is None or len(df) < 30 or df_7h is None or len(df_7h) < 10:
        return "Неизвестно", 0, [], None
    
    # Индикаторы на 1D
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['CCI'] = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close'], window=20).cci()
    df['EMA50'] = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
    df['EMA200'] = ta.trend.EMAIndicator(df['Close'], window=200).ema_indicator()
    df['MACD'] = ta.trend.MACD(df['Close']).macd_diff()
    df['Volume_MA'] = df['Volume'].rolling(window=10).mean()
    df['Stochastic'] = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close']).stoch()
    df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = ta.volatility.BollingerBands(df['Close']).bollinger_hband(), ta.volatility.BollingerBands(df['Close']).bollinger_mavg(), ta.volatility.BollingerBands(df['Close']).bollinger_lband()
    df['VWAP'] = ta.volume.VolumeWeightedAveragePrice(df['High'], df['Low'], df['Close'], df['Volume']).volume_weighted_average_price()
    df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range()
    df['ADX'] = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close']).adx()
    df['Momentum'] = ta.momentum.ROCIndicator(df['Close']).roc()
    df['OBV'] = ta.volume.OnBalanceVolumeIndicator(df['Close'], df['Volume']).on_balance_volume()
    df['Ichimoku_Conversion'] = ta.trend.IchimokuIndicator(df['High'], df['Low']).ichimoku_conversion_line()
    df['Ichimoku_Base'] = ta.trend.IchimokuIndicator(df['High'], df['Low']).ichimoku_base_line()
    
    # Индикаторы на 7H
    df_7h['RSI_7h'] = ta.momentum.RSIIndicator(df_7h['Close'], window=14).rsi()
    df_7h['Stochastic_7h'] = ta.momentum.StochasticOscillator(df_7h['High'], df_7h['Low'], df_7h['Close']).stoch()
    
    latest_rsi = df['RSI'].iloc[-1] if not df['RSI'].isna().iloc[-1] else 50
    latest_cci = df['CCI'].iloc[-1] if not df['CCI'].isna().iloc[-1] else 0
    latest_ema50 = df['EMA50'].iloc[-1] if not df['EMA50'].isna().iloc[-1] else df['Close'].iloc[-1]
    latest_ema200 = df['EMA200'].iloc[-1] if not df['EMA200'].isna().iloc[-1] else df['Close'].iloc[-1]
    latest_macd = df['MACD'].iloc[-1] if not df['MACD'].isna().iloc[-1] else 0
    latest_volume = df['Volume'].iloc[-1]
    volume_ma = df['Volume_MA'].iloc[-1] if not df['Volume_MA'].isna().iloc[-1] else latest_volume
    latest_stoch = df['Stochastic'].iloc[-1] if not df['Stochastic'].isna().iloc[-1] else 50
    latest_price = df['Close'].iloc[-1]
    latest_bb_upper = df['BB_Upper'].iloc[-1] if not df['BB_Upper'].isna().iloc[-1] else latest_price
    latest_bb_lower = df['BB_Lower'].iloc[-1] if not df['BB_Lower'].isna().iloc[-1] else latest_price
    latest_vwap = df['VWAP'].iloc[-1] if not df['VWAP'].isna().iloc[-1] else latest_price
    latest_atr = df['ATR'].iloc[-1] if not df['ATR'].isna().iloc[-1] else 0
    latest_adx = df['ADX'].iloc[-1] if not df['ADX'].isna().iloc[-1] else 25
    latest_momentum = df['Momentum'].iloc[-1] if not df['Momentum'].isna().iloc[-1] else 0
    latest_obv = df['OBV'].iloc[-1] if not df['OBV'].isna().iloc[-1] else 0
    latest_ichimoku_conv = df['Ichimoku_Conversion'].iloc[-1] if not df['Ichimoku_Conversion'].isna().iloc[-1] else latest_price
    latest_ichimoku_base = df['Ichimoku_Base'].iloc[-1] if not df['Ichimoku_Base'].isna().iloc[-1] else latest_price
    latest_rsi_7h = df_7h['RSI_7h'].iloc[-1] if not df_7h['RSI_7h'].isna().iloc[-1] else 50
    latest_stoch_7h = df_7h['Stochastic_7h'].iloc[-1] if not df_7h['Stochastic_7h'].isna().iloc[-1] else 50
    
    gann_trend = calculate_gann_angles(df_7h)
    fib_trend = calculate_fibonacci_levels(df)
    
    score = 0
    confirmations = 0
    trend = "Распределение"
    entry_signal = None
    debug_info = []
    
    # Технические индикаторы (1D)
    if latest_rsi > 70 and latest_cci > 100:
        trend = "Восходящий тренд"
        confirmations += 1
        score += 0.15
        debug_info.append(f"RSI={latest_rsi:.2f}>70, CCI={latest_cci:.2f}>100: Восходящий")
    elif latest_rsi < 30 and latest_cci < -100:
        trend = "Нисходящий тренд"
        confirmations += 1
        score += 0.15
        debug_info.append(f"RSI={latest_rsi:.2f}<30, CCI={latest_cci:.2f}<-100: Нисходящий")
    
    if latest_ema50 > latest_ema200:
        if trend == "Восходящий тренд":
            confirmations += 1
        trend = "Восходящий тренд"
        score += 0.15
        debug_info.append(f"EMA50={latest_ema50:.2f}>EMA200={latest_ema200:.2f}: Восходящий")
    elif latest_ema50 < latest_ema200:
        if trend == "Нисходящий тренд":
            confirmations += 1
        trend = "Нисходящий тренд"
        score += 0.15
        debug_info.append(f"EMA50={latest_ema50:.2f}<EMA200={latest_ema200:.2f}: Нисходящий")
    
    if latest_macd > 0 and trend == "Восходящий тренд":
        confirmations += 1
        score += 0.1
        debug_info.append(f"MACD={latest_macd:.2f}>0: Восходящий")
    elif latest_macd < 0 and trend == "Нисходящий тренд":
        confirmations += 1
        score += 0.1
        debug_info.append(f"MACD={latest_macd:.2f}<0: Нисходящий")
    
    if latest_volume > volume_ma * 1.5:
        if trend == "Восходящий тренд":
            confirmations += 1
        trend = "Накопление"
        score += 0.1
        debug_info.append(f"Volume={latest_volume:.2f}>1.5*MA={volume_ma:.2f}: Накопление")
    
    if bid and ask and bid > 0 and ask > 0:
        spread = ask - bid
        if spread < latest_price * 0.01:
            if trend == "Восходящий тренд":
                confirmations += 1
            score += 0.1
            debug_info.append(f"Bid/Ask спред={spread:.2f}<1% цены: Восходящий")
    
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
    
    if latest_adx > 25:
        if trend in ["Восходящий тренд", "Нисходящий тренд"]:
            confirmations += 1
        score += 0.1
        debug_info.append(f"ADX={latest_adx:.2f}>25: Сильный тренд")
    
    if latest_momentum > 0:
        if trend == "Восходящий тренд":
            confirmations += 1
        score += 0.1
        debug_info.append(f"Momentum={latest_momentum:.2f}>0: Восходящий")
    elif latest_momentum < 0:
        if trend == "Нисходящий тренд":
            confirmations += 1
        score += 0.1
        debug_info.append(f"Momentum={latest_momentum:.2f}<0: Нисходящий")
    
    if latest_obv > df['OBV'].iloc[-2]:
        if trend == "Восходящий тренд":
            confirmations += 1
        score += 0.1
        debug_info.append(f"OBV={latest_obv:.2f} растет: Восходящий")
    elif latest_obv < df['OBV'].iloc[-2]:
        if trend == "Нисходящий тренд":
            confirmations += 1
        score += 0.1
        debug_info.append(f"OBV={latest_obv:.2f} падает: Нисходящий")
    
    if latest_price > latest_ichimoku_conv and latest_price > latest_ichimoku_base:
        if trend == "Восходящий тренд":
            confirmations += 1
        score += 0.1
        debug_info.append(f"Price={latest_price:.2f}>Ichimoku Conv={latest_ichimoku_conv:.2f}, Base={latest_ichimoku_base:.2f}: Восходящий")
    
    if fib_trend:
        if fib_trend.startswith("Восходящий") and trend == "Восходящий тренд":
            confirmations += 1
        elif fib_trend.startswith("Нисходящий") and trend == "Нисходящий тренд":
            confirmations += 1
        score += 0.05
        debug_info.append(f"Fibonacci: {fib_trend}")
    
    if pe_ratio and pe_ratio < 15:
        if trend == "Восходящий тренд":
            confirmations += 1
        score += 0.05
        debug_info.append(f"P/E={pe_ratio:.2f}<15: Недооценка")
    if eps and eps > 0:
        if trend == "Восходящий тренд":
            confirmations += 1
        score += 0.05
        debug_info.append(f"EPS={eps:.2f}>0: Положительная прибыль")
    
    # Точка входа на 7H
    if latest_rsi_7h > 70 and latest_stoch_7h > 80:
        entry_signal = f"Покупка (RSI_7h={latest_rsi_7h:.2f}>70, Stochastic_7h={latest_stoch_7h:.2f}>80)"
        debug_info.append(entry_signal)
    elif latest_rsi_7h < 30 and latest_stoch_7h < 20:
        entry_signal = f"Продажа (RSI_7h={latest_rsi_7h:.2f}<30, Stochastic_7h={latest_stoch_7h:.2f}<20)"
        debug_info.append(entry_signal)
    
    if gann_trend == "Сильный тренд" and trend in ["Восходящий тренд", "Нисходящий тренд"]:
        confirmations += 1
        score += 0.1
        debug_info.append(f"Gann (7H): {gann_trend}")
    
    # Цель и стоп-лосс
    target = latest_price + latest_atr * 2 if latest_atr else latest_price * 1.05
    stop_loss = latest_price - latest_atr * 1.5 if latest_atr else latest_price * 0.95
    
    if confirmations < 3:
        trend = "Неизвестно"
        score = 0
        debug_info.append(f"Подтверждений={confirmations}<3: Неизвестно")
    elif confirmations >= 4:
        score += 0.2
    
    return trend, score, debug_info, entry_signal, target, stop_loss

def send_telegram_report(chat_id, message):
    if not TELEGRAM_BOT_TOKEN:
        return "Ошибка: Токен бота не загружен (проверьте secrets в Streamlit)."
    try:
        response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe")
        if not response.json().get("ok"):
            return f"Ошибка: Недействительный токен ({response.json().get('description')})"
        response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", params={
            "chat_id": chat_id,
            "text": message
        })
        if response.json().get("ok"):
            return "Сообщение отправлено успешно!"
        return f"Ошибка отправки: {response.json().get('description')}"
    except Exception as e:
        return f"Ошибка отправки: {str(e)} (проверьте токен или Chat ID)"

# Streamlit приложение
st.title(">tS|TQTVLSYSTEM")
st.subheader("Анализ трендов и лучших сделок")

# Админ-панель
admin_key = st.text_input("Админ-ключ (для отладки)", type="password")
is_admin = admin_key == ADMIN_KEY

if is_admin:
    with st.expander("Отладка: Статус API и токена"):
        st.write(f"**Alpha Vantage ключ**: {'Загружен' if ALPHA_VANTAGE_API_KEY else 'Не загружен'}")
        st.write(f"**Telegram токен**: {'Загружен' if TELEGRAM_BOT_TOKEN else 'Не загружен'}")
        if TELEGRAM_BOT_TOKEN:
            try:
                response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe")
                if response.json().get("ok"):
                    st.write(f"**Бот активен**: @{response.json()['result']['username']}")
                else:
                    st.error(f"**Ошибка проверки бота**: {response.json().get('description')}")
            except Exception as e:
                st.error(f"**Ошибка проверки бота**: {str(e)}")
        if st.button("Тест Alpha Vantage (1 запрос)"):
            test_df = fetch_stock_data_cached("AAPL")
            st.write(f"Тест AAPL: {'Успех' if test_df is not None else 'Ошибка'}")

# Выбор рынка
market = st.selectbox("Выберите рынок", ["Акции", "Криптовалюты"])
st.write("Бесплатный уровень: просмотр тренда рынка. Премиум: топ-активы и отчеты в Telegram (скоро).")

# Списки активов
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
    data_fetcher = fetch_stock_data_cached
    data_fetcher_7h = fetch_stock_data_7h
    quote_fetcher = fetch_stock_quote_cached
else:
    assets = crypto_ids
    data_fetcher = lambda x: fetch_stock_data_cached(x, use_alpha=False)  # Для крипты используем yfinance, если возможно
    data_fetcher_7h = fetch_stock_data_7h
    quote_fetcher = lambda x: (None, None, None, None)

trend_scores = []
successful_fetches = 0
debug_trends = []
market_confirmations = []
for asset in assets[:50]:
    df = data_fetcher(asset)
    df_7h = data_fetcher_7h(asset)
    if df is not None and df_7h is not None:
        successful_fetches += 1
    bid, ask, pe_ratio, eps = quote_fetcher(asset)
    if df is not None and df_7h is not None:
        trend, score, debug_info, entry_signal, target, stop_loss = analyze_trend(df, df_7h, bid, ask, pe_ratio, eps)
        trend_scores.append((asset, trend, score, entry_signal, target, stop_loss, debug_info))
        debug_trends.append((asset, debug_info, entry_signal))
        market_confirmations.append(trend)
    else:
        debug_trends.append((asset, [f"Ошибка загрузки данных для {asset}"], None))
    time.sleep(0.2)

st.info(f"Успешно загружено данных: {successful_fetches}/{min(len(assets), 50)} активов")

# Тренд рынка
if trend_scores:
    market_trend = max(set([x[1] for x in trend_scores]), key=[x[1] for x in trend_scores].count)
    confirmation_count = sum(1 for x in trend_scores if x[1] == market_trend)
    st.success(
        f"🚀 **Тренд рынка**: {market_trend} 📈\n"
        f"📊 Подтверждено {confirmation_count} активами с 3+ индикаторами (EMA50>EMA200, RSI>70 и др.).\n"
        f"💡 **Рекомендация**: {'Ищите возможности для покупок в активах с сильным импульсом.' if market_trend == 'Восходящий тренд' else 'Рассмотрите продажи или хеджирование.'}"
    )
else:
    st.error("**Тренд рынка**: Не удалось определить (проверьте отладку).")

# Админ-отладка
if is_admin:
    with st.expander("Детали тренда по активам"):
        debug_df = []
        for asset, debug_info, entry_signal in debug_trends:
            debug_df.append({
                "Актив": asset,
                "Тренд": debug_info[-1] if debug_info else "Неизвестно",
                "Индикаторы": "; ".join(debug_info[:-1]) if debug_info else "Нет данных",
                "Точка входа (7H)": entry_signal if entry_signal else "Нет сигнала"
            })
        st.dataframe(pd.DataFrame(debug_df))

# Топ-активы
if st.button("Показать топ-активы (Премиум)"):
    if trend_scores:
        top_assets = sorted([x for x in trend_scores if x[2] >= 0.4], key=lambda x: x[2], reverse=True)[:10]
        if top_assets:
            st.write("**🔥 Топ-активы для сделок**:")
            for asset, trend, score, entry_signal, target, stop_loss, debug_info in top_assets:
                confirmations = sum(1 for info in debug_info if "Восходящий" in info or "Нисходящий" in info or "Накопление" in info)
                signals = [info.split(":")[0] for info in debug_info if "Восходящий" in info or "Нисходящий" in info or "Накопление" in info]
                st.write(
                    f"🚀 **{asset}**: {trend} 📈\n"
                    f"📊 **Подтверждено**: {confirmations} индикаторов ({', '.join(signals[:3])}).\n"
                    f"🎯 **Цель**: ${target:.2f}\n"
                    f"🛑 **Стоп-лосс**: ${stop_loss:.2f}\n"
                    f"⏰ **Точка входа (7H)**: {entry_signal if entry_signal else 'Ждем сигнала'}"
                )
        else:
            st.warning("Нет активов с достаточным количеством подтверждений (нужно 4+).")
    else:
        st.warning("Нет данных для топ-активов.")

# Telegram
chat_id_input = st.text_input("Введите ваш Telegram Chat ID (отправьте /start боту @ern1kko_bot, чтобы узнать ID)", value="370110317")
if st.button("Отправить отчет в Telegram (Премиум)"):
    if trend_scores:
        top_assets = sorted([x for x in trend_scores if x[2] >= 0.4], key=lambda x: x[2], reverse=True)[:3]
        confirmation_count = sum(1 for x in trend_scores if x[1] == market_trend)
        message = (
            f"🚀 *>*tS|TQTVLSYSTEM: Отчет по рынку 📈\n"
            f"📅 *Дата*: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            f"💹 *Рынок*: {market}\n"
            f"📊 *Тренд*: {market_trend} (подтверждено {confirmation_count} активами)\n"
            f"🔥 *Топ-активы*:\n"
        )
        for i, (asset, trend, score, entry_signal, target, stop_loss, _) in enumerate(top_assets, 1):
            message += (
                f"{i}️⃣ *{asset}*: {trend} (Скор: {score:.2f})\n"
                f"   🎯 Цель: ${target:.2f}\n"
                f"   🛑 Стоп: ${stop_loss:.2f}\n"
                f"   ⏰ Точка входа: {entry_signal if entry_signal else 'Ждем сигнала'}\n"
            )
        result = send_telegram_report(chat_id_input, message)
        st.write(result)
    else:
        st.warning("Нет данных для отчета.")

st.write("**Примечание**: Подробная аналитика и отчеты в Telegram доступны в Премиум-уровне (скоро).")
