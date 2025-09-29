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
ADMIN_KEY = st.secrets.get("ADMIN_KEY", "mysecretkey123")

# Кэширование данных
@st.cache_data(ttl=300)
def fetch_stock_data_cached(ticker, use_alpha=True, interval="1d", period="1y"):
    if use_alpha and interval == "1d":
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
        df = stock.history(period=period, interval=interval)
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
def fetch_crypto_data(coin_id, days=365):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame({
            'Date': pd.to_datetime([x[0]/1000 for x in data['prices']], unit='s'),
            'Close': [x[1] for x in data['prices']],
            'Volume': [x[1] for x in data['total_volumes']],
            'High': [x[1] for x in data['prices']],
            'Low': [x[1] for x in data['prices']]
        })
        df.set_index('Date', inplace=True)
        df_7h = df.resample('7H').agg({'Close': 'last', 'Volume': 'sum', 'High': 'max', 'Low': 'min'}).dropna()
        df_1w = df.resample('1W').agg({'Close': 'last', 'Volume': 'sum', 'High': 'max', 'Low': 'min'}).dropna()
        return df, df_7h, df_1w
    return None, None, None

@st.cache_data(ttl=300)
def fetch_stock_fundamentals(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "bid": float(info.get("bid", 0)),
            "ask": float(info.get("ask", 0)),
            "pe_ratio": info.get("trailingPE", None),
            "eps": info.get("trailingEps", None),
            "debt_equity": info.get("debtToEquity", None),
            "roe": info.get("returnOnEquity", None),
            "market_cap": info.get("marketCap", None)
        }
    except:
        return {"bid": None, "ask": None, "pe_ratio": None, "eps": None, "debt_equity": None, "roe": None, "market_cap": None}

@st.cache_data(ttl=300)
def fetch_crypto_fundamentals(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        market_cap = data.get("market_data", {}).get("market_cap", {}).get("usd", None)
        tvl = data.get("market_data", {}).get("total_value_locked", {}).get("usd", None)
        return {"market_cap": market_cap, "tvl": tvl}
    return {"market_cap": None, "tvl": None}

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

def calculate_schiff_pitchfork(df):
    if len(df) < 20:
        return None, None, None
    high_idx = df['High'].iloc[-20:].idxmax()
    low_idx = df['Low'].iloc[-20:].idxmin()
    pivot_high = df['High'].loc[high_idx]
    pivot_low = df['Low'].loc[low_idx]
    median_price = (pivot_high + pivot_low) / 2
    latest_price = df['Close'].iloc[-1]
    if latest_price > median_price:
        return "Покупка (выше медианы)", median_price, latest_price
    elif latest_price < median_price:
        return "Продажа (ниже медианы)", median_price, latest_price
    return None, median_price, latest_price

def analyze_short_term(df, df_7h, fundamentals):
    if df is None or len(df) < 30 or df_7h is None or len(df_7h) < 10:
        return "Неизвестно", 0, [], None, None, None
    
    # Индикаторы
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['CCI'] = ta.trend.CCIIndicator(df['High'], df['Low'], df['Close'], window=20).cci()
    df['EMA50'] = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
    df['EMA200'] = ta.trend.EMAIndicator(df['Close'], window=200).ema_indicator()
    df['Volume_MA'] = df['Volume'].rolling(window=10).mean()
    df['Momentum'] = ta.momentum.ROCIndicator(df['Close']).roc()
    df_7h['RSI_7h'] = ta.momentum.RSIIndicator(df_7h['Close'], window=14).rsi()
    
    latest_rsi = df['RSI'].iloc[-1] if not df['RSI'].isna().iloc[-1] else 50
    latest_cci = df['CCI'].iloc[-1] if not df['CCI'].isna().iloc[-1] else 0
    latest_ema50 = df['EMA50'].iloc[-1] if not df['EMA50'].isna().iloc[-1] else df['Close'].iloc[-1]
    latest_ema200 = df['EMA200'].iloc[-1] if not df['EMA200'].isna().iloc[-1] else df['Close'].iloc[-1]
    latest_volume = df['Volume'].iloc[-1]
    volume_ma = df['Volume_MA'].iloc[-1] if not df['Volume_MA'].isna().iloc[-1] else latest_volume
    latest_momentum = df['Momentum'].iloc[-1] if not df['Momentum'].isna().iloc[-1] else 0
    latest_rsi_7h = df_7h['RSI_7h'].iloc[-1] if not df_7h['RSI_7h'].isna().iloc[-1] else 50
    latest_price = df['Close'].iloc[-1]
    latest_atr = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range().iloc[-1]
    
    gann_trend = calculate_gann_angles(df_7h)
    schiff_signal, schiff_median, schiff_price = calculate_schiff_pitchfork(df_7h)
    
    bid = fundamentals.get("bid")
    ask = fundamentals.get("ask")
    pe_ratio = fundamentals.get("pe_ratio")
    
    score = 0
    confirmations = 0
    trend = "Неизвестно"
    entry_signal = None
    debug_info = []
    
    # Краткосрочные сигналы (перепроданность → лонг, переоцененность → шорт)
    if latest_rsi < 30 and latest_cci < -100:
        trend = "Восходящий тренд"
        confirmations += 1
        score += 0.2
        debug_info.append(f"• RSI={latest_rsi:.2f}<30, CCI={latest_cci:.2f}<-100: Перепроданность")
    elif latest_rsi > 70 and latest_cci > 100:
        trend = "Нисходящий тренд"
        confirmations += 1
        score += 0.2
        debug_info.append(f"• RSI={latest_rsi:.2f}>70, CCI={latest_cci:.2f}>100: Переоцененность")
    
    if latest_price > latest_ema50 > latest_ema200:
        if trend == "Восходящий тренд":
            confirmations += 1
        trend = "Восходящий тренд"
        score += 0.2
        debug_info.append(f"• Price={latest_price:.2f}>EMA50={latest_ema50:.2f}>EMA200={latest_ema200:.2f}: Поддержка")
    elif latest_price < latest_ema50 < latest_ema200:
        if trend == "Нисходящий тренд":
            confirmations += 1
        trend = "Нисходящий тренд"
        score += 0.2
        debug_info.append(f"• Price={latest_price:.2f}<EMA50={latest_ema50:.2f}<EMA200={latest_ema200:.2f}: Сопротивление")
    
    if bid and ask and bid > 0 and ask > 0:
        spread = ask - bid
        if spread < latest_price * 0.01 and bid > ask:
            if trend == "Восходящий тренд":
                confirmations += 1
            score += 0.15
            debug_info.append(f"• Bid={bid:.2f}>Ask={ask:.2f}, спред={spread:.2f}: Спрос")
        elif spread < latest_price * 0.01 and ask > bid:
            if trend == "Нисходящий тренd":
                confirmations += 1
            score += 0.15
            debug_info.append(f"• Ask={ask:.2f}>Bid={bid:.2f}, спред={spread:.2f}: Предложение")
    
    if gann_trend == "Сильный тренd":
        if trend == "Восходящий тренd":
            confirmations += 1
        score += 0.15
        debug_info.append(f"• Gann (7H): {gann_trend}")
    elif gann_trend == "Слабый тренd" and trend == "Нисходящий тренd":
        confirmations += 1
        score += 0.15
        debug_info.append(f"• Gann (7H): {gann_trend}")
    
    if schiff_signal:
        if schiff_signal.startswith("Покупка") and trend == "Восходящий тренd":
            confirmations += 1
            score += 0.15
            debug_info.append(f"• Schiff: {schiff_signal}")
        elif schiff_signal.startswith("Продажа") and trend == "Нисходящий тренd":
            confirmations += 1
            score += 0.15
            debug_info.append(f"• Schiff: {schiff_signal}")
    
    if latest_volume > volume_ma * 1.5 and latest_momentum > 5:
        if trend == "Восходящий тренd":
            confirmations += 1
        score += 0.1
        debug_info.append(f"• Volume={latest_volume:.2f}>1.5*MA={volume_ma:.2f}, Momentum={latest_momentum:.2f}>5: Импульс роста")
    elif latest_volume > volume_ma * 1.5 and latest_momentum < -5:
        if trend == "Нисходящий тренd":
            confirmations += 1
        score += 0.1
        debug_info.append(f"• Volume={latest_volume:.2f}>1.5*MA={volume_ma:.2f}, Momentum={latest_momentum:.2f}<-5: Импульс падения")
    
    if latest_rsi_7h < 30 and trend == "Восходящий тренd":
        entry_signal = f"Лонг (RSI_7h={latest_rsi_7h:.2f}<30)"
        debug_info.append(entry_signal)
    elif latest_rsi_7h > 70 and trend == "Нисходящий тренd":
        entry_signal = f"Шорт (RSI_7h={latest_rsi_7h:.2f}>70)"
        debug_info.append(entry_signal)
    
    if pe_ratio and pe_ratio < 15 and trend == "Восходящий тренd":
        score += 0.2
        debug_info.append(f"• P/E={pe_ratio:.2f}<15: Недооценка")
    elif pe_ratio and pe_ratio > 30 and trend == "Нисходящий тренd":
        score += 0.2
        debug_info.append(f"• P/E={pe_ratio:.2f}>30: Переоценка")
    
    target = latest_price + (2 * latest_atr if latest_atr else latest_price * 0.05) if trend == "Восходящий тренd" else latest_price - (2 * latest_atr if latest_atr else latest_price * 0.05)
    stop_loss = latest_price - (1.5 * latest_atr if latest_atr else latest_price * 0.05) if trend == "Восходящий тренd" else latest_price + (1.5 * latest_atr if latest_atr else latest_price * 0.05)
    potential = ((target - latest_price) / latest_price * 100) if stop_loss and target else 5
    
    if confirmations < 3:
        trend = "Неизвестно"
        score = 0
        debug_info.append(f"Подтверждений={confirmations}<3: Неизвестно")
    elif confirmations >= 4:
        score += 0.3
    
    return trend, score, debug_info, entry_signal, target, stop_loss

def analyze_long_term(df, df_1w, fundamentals):
    if df is None or len(df) < 30 or df_1w is None or len(df_1w) < 10:
        return "Неизвестно", 0, [], None, None, None
    
    # Индикаторы
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['EMA50'] = ta.trend.EMAIndicator(df['Close'], window=50).ema_indicator()
    df['EMA200'] = ta.trend.EMAIndicator(df['Close'], window=200).ema_indicator()
    df_1w['ADX'] = ta.trend.ADXIndicator(df_1w['High'], df_1w['Low'], df_1w['Close']).adx()
    
    latest_rsi = df['RSI'].iloc[-1] if not df['RSI'].isna().iloc[-1] else 50
    latest_ema50 = df['EMA50'].iloc[-1] if not df['EMA50'].isna().iloc[-1] else df['Close'].iloc[-1]
    latest_ema200 = df['EMA200'].iloc[-1] if not df['EMA200'].isna().iloc[-1] else df['Close'].iloc[-1]
    latest_adx = df_1w['ADX'].iloc[-1] if not df_1w['ADX'].isna().iloc[-1] else 20
    latest_price = df['Close'].iloc[-1]
    latest_atr = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close']).average_true_range().iloc[-1]
    
    pe_ratio = fundamentals.get("pe_ratio")
    eps = fundamentals.get("eps")
    debt_equity = fundamentals.get("debt_equity")
    roe = fundamentals.get("roe")
    market_cap = fundamentals.get("market_cap")
    tvl = fundamentals.get("tvl")
    
    score = 0
    confirmations = 0
    trend = "Неизвестно"
    debug_info = []
    
    # Долгосрочные сигналы
    if latest_ema50 > latest_ema200:
        trend = "Восходящий тренd"
        confirmations += 1
        score += 0.2
        debug_info.append(f"• EMA50={latest_ema50:.2f}>EMA200={latest_ema200:.2f}: Долгосрочный рост")
    
    if 40 < latest_rsi < 60:
        confirmations += 1
        score += 0.2
        debug_info.append(f"• RSI={latest_rsi:.2f} в 40-60: Потенциал роста")
    
    if latest_adx > 20:
        confirmations += 1
        score += 0.2
        debug_info.append(f"• ADX={latest_adx:.2f}>20: Устойчивый тренd")
    
    if pe_ratio and pe_ratio < 15:
        confirmations += 1
        score += 0.2
        debug_info.append(f"• P/E={pe_ratio:.2f}<15: Недооценка")
    
    if eps and eps > 0:
        confirmations += 1
        score += 0.15
        debug_info.append(f"• EPS={eps:.2f}>0: Положительная прибыль")
    
    if debt_equity and debt_equity < 0.5:
        confirmations += 1
        score += 0.15
        debug_info.append(f"• Debt/Equity={debt_equity:.2f}<0.5: Низкая долговая нагрузка")
    
    if roe and roe > 0.1:
        confirmations += 1
        score += 0.15
        debug_info.append(f"• ROE={roe:.2f}>10%: Высокая рентабельность")
    
    if market_cap and tvl and market_cap / tvl < 1:
        confirmations += 1
        score += 0.2
        debug_info.append(f"• Market Cap/TVL={market_cap/tvl:.2f}<1: Недооценка (крипта)")
    
    target = latest_price + (5 * latest_atr if latest_atr else latest_price * 0.1)
    stop_loss = latest_price - (3 * latest_atr if latest_atr else latest_price * 0.05)
    potential = ((target - latest_price) / latest_price * 100) if stop_loss and target else 5
    
    if confirmations < 3:
        trend = "Неизвестно"
        score = 0
        debug_info.append(f"Подтверждений={confirmations}<3: Неизвестно")
    elif confirmations >= 4:
        score += 0.3
    
    return trend, score, debug_info, None, target, stop_loss

def send_telegram_report(chat_id, message):
    if not TELEGRAM_BOT_TOKEN:
        return "Ошибка: Токен бота не загружен (проверьте secrets в Streamlit)."
    try:
        response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe")
        if not response.json().get("ok"):
            return f"Ошибка: Недействительный токен ({response.json().get('description')})"
        response = requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", params={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        })
        if response.json().get("ok"):
            return "Сообщение отправлено успешно!"
        return f"Ошибка отправки: {response.json().get('description')}"
    except Exception as e:
        return f"Ошибка отправки: {str(e)} (проверьте токен или Chat ID)"

# Streamlit приложение
st.title("🚀 >tS|TQTVLSYSTEM")
st.subheader("Анализ трендов и лучших сделок 📈")

# Админ-панель
admin_key = st.text_input("🔍 Админ-ключ (для отладки)", type="password")
is_admin = admin_key == ADMIN_KEY

if is_admin:
    with st.expander("🔍 Отладка: Статус API и токена"):
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

# Выбор рынка и стратегии
market = st.selectbox("💹 Выберите рынок", ["Акции", "Криптовалюты"])
strategy = st.selectbox("🎯 Выберите стратегию", ["Краткосрочные спекуляции", "Долгосрочные инвестиции"])
st.write("🔓 Бесплатный уровень: просмотр тренда рынка. Премиум: топ-активы и отчеты в Telegram (скоро).")

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
    fund_fetcher = fetch_stock_fundamentals
    crypto_data = False
else:
    assets = crypto_ids
    data_fetcher = lambda x: fetch_crypto_data(x)
    fund_fetcher = fetch_crypto_fundamentals
    crypto_data = True

trend_scores = []
successful_fetches = 0
debug_trends = []
market_confirmations = []
for asset in assets[:50]:
    if crypto_data:
        df, df_7h, df_1w = data_fetcher(asset)
    else:
        df = data_fetcher(asset, interval="1d", period="1y")
        df_7h = data_fetcher(asset, interval="1h", period="60d")
        if df_7h is not None:
            df_7h = df_7h.resample('7H').agg({'Close': 'last', 'Volume': 'sum', 'High': 'max', 'Low': 'min'}).dropna()
        df_1w = data_fetcher(asset, interval="1wk", period="5y")
    fundamentals = fund_fetcher(asset)
    if df is not None and df_7h is not None and df_1w is not None:
        successful_fetches += 1
    if df is not None and df_7h is not None and df_1w is not None:
        if strategy == "Краткосрочные спекуляции":
            trend, score, debug_info, entry_signal, target, stop_loss = analyze_short_term(df, df_7h, fundamentals)
        else:
            trend, score, debug_info, entry_signal, target, stop_loss = analyze_long_term(df, df_1w, fundamentals)
        trend_scores.append((asset, trend, score, entry_signal, target, stop_loss, debug_info))
        debug_trends.append((asset, debug_info, entry_signal))
        market_confirmations.append(trend)
    else:
        debug_trends.append((asset, [f"Ошибка загрузки данных для {asset}"], None))
    time.sleep(0.2)

st.info(f"✅ Успешно загружено данных: {successful_fetches}/{min(len(assets), 50)} активов")

# Тренд рынка
if trend_scores:
    up_trend_count = sum(1 for x in trend_scores if x[1] == "Восходящий тренd")
    total_confirmed = sum(1 for x in trend_scores if x[1] != "Неизвестно")
    market_trend = "Восходящий тренd" if up_trend_count > total_confirmed / 2 else "Нисходящий тренd"
    confirmation_count = sum(1 for x in trend_scores if x[1] == market_trend)
    recommendation = (
        f"Ищите лонг-позиции в перепроданных активах с сильным импульсом." 
        if market_trend == "Восходящий тренd" else 
        f"Рассмотрите шорт-позиции в переоцененных активах или хеджирование."
    )
    st.success(
        f"🚀 **Тренд рынка**: {market_trend} {'📈' if market_trend == 'Восходящий тренd' else '📉'}\n"
        f"📊 Подтверждено {confirmation_count} активами с 3+ индикаторами.\n"
        f"💡 **Рекомендация**: {recommendation}"
    )
else:
    st.error("🚨 **Тренд рынка**: Не удалось определить (проверьте отладку).")

# Админ-отладка
if is_admin:
    with st.expander("🔍 Детали тренда по активам"):
        debug_df = []
        for asset, debug_info, entry_signal in debug_trends:
            debug_df.append({
                "Актив": asset,
                "Тренд": debug_info[-1] if debug_info else "Неизвестно",
                "Индикаторы": "; ".join(debug_info[:-1]) if debug_info else "Нет данных",
                "Точка входа": entry_signal if entry_signal else "Нет сигнала"
            })
        st.dataframe(pd.DataFrame(debug_df))

# Топ-активы
if st.button("🔥 Показать топ-активы (Премиум)"):
    if trend_scores:
        top_assets = sorted([x for x in trend_scores if x[2] >= 0.4], key=lambda x: x[2], reverse=True)[:5]
        if top_assets:
            st.write(f"🔥 **Топ-активы для {'спекуляций' if strategy == 'Краткосрочные спекуляции' else 'инвестиций'}**:")
            for asset, trend, score, entry_signal, target, stop_loss, debug_info in top_assets:
                confirmations = sum(1 for info in debug_info if any(k in info for k in ["Перепроданность", "Переоцененность", "Поддержка", "Сопротивление", "Спрос", "Предложение", "Schiff", "Gann"]))
                signals = [info.split(":")[0] for info in debug_info if any(k in info for k in ["Перепроданность", "Переоцененность", "Поддержка", "Сопротивление", "Спрос", "Предложение", "Schiff", "Gann"])]
                potential = ((target - latest_price) / latest_price * 100) if stop_loss and target else 5
                st.write(
                    f"#{'STOCKS' if market == 'Акции' else 'CRYPTO'} #HYPE\n"
                    f"🚀 **{asset}**: Классический сетап в {'лонг' if trend == 'Восходящий тренd' else 'шорт'}.\n"
                    f"• Подтверждено {confirmations} индикаторов ({', '.join(signals[:3])}).\n"
                    f"• Зона вибрации: {'Углы Ганна' if 'Gann' in ' '.join(debug_info) else 'Уровни EMA'}.\n"
                    f"🎯 **Цель**: ${target:.2f} (+{potential:.1f}% вдоль угла Ганна).\n"
                    f"🛑 **Стоп**: ${stop_loss:.2f} {'ниже EMA200' if trend == 'Восходящий тренd' else 'выше EMA50'}.\n"
                    f"⏰ **Точка входа**: {entry_signal if entry_signal else 'Ждем сигнала'}.\n"
                    f"💡 **Примечание**: Рынок манипулятивный, будьте осторожны с объемом."
                )
        else:
            st.warning("🚨 Нет активов с достаточным количеством подтверждений (нужно 4+).")
    else:
        st.warning("🚨 Нет данных для топ-активов.")

# Telegram
chat_id_input = st.text_input("📬 Введите ваш Telegram Chat ID (отправьте /start боту @ern1kko_bot, чтобы узнать ID)", value="")
if st.button("📤 Отправить отчет в Telegram (Премиум)"):
    if trend_scores and chat_id_input:
        top_assets = sorted([x for x in trend_scores if x[2] >= 0.4], key=lambda x: x[2], reverse=True)[:3]
        up_trend_count = sum(1 for x in trend_scores if x[1] == "Восходящий тренd")
        total_confirmed = sum(1 for x in trend_scores if x[1] != "Неизвестно")
        market_trend = "Восходящий тренd" if up_trend_count > total_confirmed / 2 else "Нисходящий тренd"
        confirmation_count = sum(1 for x in trend_scores if x[1] == market_trend)
        recommendation = (
            f"Ищите лонг-позиции в перепроданных активах с сильным импульсом." 
            if market_trend == "Восходящий тренd" else 
            f"Рассмотрите шорт-позиции в переоцененных активах или хеджирование."
        )
        message = (
            f"🚀 *>*tS|TQTVLSYSTEM: Отчет по рынку {'📈' if market_trend == 'Восходящий тренd' else '📉'}*\n"
            f"📅 *Дата*: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            f"💹 *Рынок*: {market}\n"
            f"📊 *Тренд*: {market_trend} (подтверждено {confirmation_count} активами)\n"
            f"💡 *Рекомендация*: {recommendation}\n"
            f"🔥 *Топ-активы*:\n"
        )
        for i, (asset, trend, score, entry_signal, target, stop_loss, debug_info) in enumerate(top_assets, 1):
            confirmations = sum(1 for info in debug_info if any(k in info for k in ["Перепроданность", "Переоцененность", "Поддержка", "Сопротивление", "Спрос", "Предложение", "Schiff", "Gann"]))
            signals = [info.split(":")[0] for info in debug_info if any(k in info for k in ["Перепроданность", "Переоцененность", "Поддержка", "Сопротивление", "Спрос", "Предложение", "Schiff", "Gann"])]
            potential = ((target - latest_price) / latest_price * 100) if stop_loss and target else 5
            message += (
                f"{i}️⃣ #{'STOCKS' if market == 'Акции' else 'CRYPTO'} #HYPE\n"
                f"🚀 *{asset}*: Классический сетап в {'лонг' if trend == 'Восходящий тренd' else 'шорт'}.\n"
                f"• Подтверждено {confirmations} индикаторов ({', '.join(signals[:3])}).\n"
                f"• Зона вибрации: {'Углы Ганна' if 'Gann' in ' '.join(debug_info) else 'Уровни EMA'}.\n"
                f"🎯 *Цель*: ${target:.2f} (+{potential:.1f}% вдоль угла Ганна).\n"
                f"🛑 *Стоп*: ${stop_loss:.2f} {'ниже EMA200' if trend == 'Восходящий тренd' else 'выше EMA50'}.\n"
                f"⏰ *Точка входа*: {entry_signal if entry_signal else 'Ждем сигнала'}.\n"
                f"💡 *Примечание*: Рынок манипулятивный, будьте осторожны с объемом.\n"
            )
        result = send_telegram_report(chat_id_input, message)
        st.write(result)
    else:
        st.warning("🚨 Введите Chat ID и убедитесь, что данные для отчета доступны.")

st.write("🔓 **Примечание**: Подробная аналитика и отчеты в Telegram доступны в Премиум-уровне (скоро).")

st.write("🔓 **Примечание**: Подробная аналитика и отчеты в Telegram доступны в Премиум-уровне (скоро).")
st.write("**Примечание**: Подробная аналитика и отчеты в Telegram доступны в Премиум-уровне (скоро).")
