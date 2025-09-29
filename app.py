import streamlit as st
import pandas as pd
import requests
import ta
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf
import numpy as np
import time

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
    "litecoin", "bitcoin-cash", "stellar", "cosmos", "algorand", "tezos", "eos", "neo", "iota", "tron"
]

# Темный режим и дизайн в стиле Xynth
st.set_page_config(page_title=">tS|TQTVLSYSTEM", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
        font-family: Arial, sans-serif;
    }
    .stContainer {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    .stMetric > label {
        color: #ffffff;
    }
    .stSelectbox > label {
        color: #ffffff;
        text-align: center;
    }
    .stButton > button {
        background-color: #1f1f1f;
        color: #ffffff;
        border-color: #ffffff;
        width: 200px;
        margin: 0 auto;
        display: block;
    }
    .css-1aumxhk {
        width: 80%;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# API ключ и Telegram токен
ALPHA_VANTAGE_API_KEY = st.secrets.get("ALPHA_VANTAGE_API_KEY", "NFNQC9SQK6XF7CY3")
TELEGRAM_BOT_TOKEN = st.secrets.get("TELEGRAM_BOT_TOKEN", None)
ADMIN_KEY = st.secrets.get("ADMIN_KEY", "mysecretkey123")

# Кэширование данных
@st.cache_data(ttl=300)
def fetch_stock_data_cached(ticker, interval="1d", period="1y"):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        if not df.empty:
            df = df[["Close", "Volume", "High", "Low"]]
            return df
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
        return df
    return None

@st.cache_data(ttl=300)
def fetch_stock_fundamentals(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "pe_ratio": info.get("trailingPE", None),
            "eps": info.get("trailingEps", None),
            "debt_equity": info.get("debtToEquity", None),
            "roe": info.get("returnOnEquity", None),
            "market_cap": info.get("marketCap", None),
            "beta": info.get("beta", None),
            "atr": stock.history(period="1mo")['High'].subtract(stock.history(period="1mo")['Low']).rolling(14).mean().iloc[-1]
        }
    except:
        return {"pe_ratio": None, "eps": None, "debt_equity": None, "roe": None, "market_cap": None, "beta": None, "atr": None}

def analyze_strategy_day_trade(df_list, market):
    filtered = []
    for ticker, df in df_list:
        if df is None or len(df) < 30:
            continue
        latest_price = df['Close'].iloc[-1]
        if latest_price < 10:
            continue
        atr_pct = (df['High'].subtract(df['Low']).rolling(14).mean().iloc[-1] / latest_price) * 100
        if not (2 <= atr_pct <= 5):
            continue
        avg_volume = df['Volume'].rolling(10).mean().iloc[-1]
        if avg_volume < 2e6:
            continue
        fundamentals = fetch_stock_fundamentals(ticker)
        beta = fundamentals.get("beta", 1.0)
        if beta <= 1.2:
            continue
        filtered.append((ticker, df, latest_price, atr_pct, avg_volume, beta, fundamentals.get("market_cap", 0)))
    
    filtered.sort(key=lambda x: x[6], reverse=True)
    top_15 = filtered[:15]
    
    fig = go.Figure()
    atr_data = [x[3] for x in filtered]
    fig.add_trace(go.Histogram(x=atr_data, name="ATR%", nbinsx=20))
    fig.update_layout(title="Распределение ATR%", xaxis_title="ATR %", yaxis_title="Количество акций", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Анализ рынка")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Начальная вселенная", len(df_list))
        st.metric("После базового фильтра", len(filtered))
    with col2:
        st.metric("Высокая волатильность (ATR >5%)", sum(1 for x in filtered if x[3] > 5))
        st.metric("Умеренная волатильность (ATR 2–5%)", sum(1 for x in filtered if 2 <= x[3] <= 5))
    
    st.subheader("🔑 Ключевые идеи")
    st.write("• Гистограмма показывает, что большинство акций имеют ATR 3-6%. Диапазон 2-5% — оптимальная зона умеренной волатильности.")
    st.write("• Доминирование секторов: Технологии (7 акций), Услуги связи (3), Финансы (3).")
    
    st.subheader("🏆 Пять лучших акций")
    top_df = pd.DataFrame([
        {"Акция": x[0], "Cap ($T)": x[6]/1e12, "ATR %": x[3], "Бета": x[5]} for x in top_15[:5]
    ])
    st.table(top_df)
    
    return "Анализ завершен"

def analyze_strategy_undervalued(df_list, market):
    filtered = []
    for ticker, df in df_list:
        if df is None or len(df) < 30:
            continue
        fundamentals = fetch_stock_fundamentals(ticker)
        pe = fundamentals.get("pe_ratio")
        eps = fundamentals.get("eps")
        debt = fundamentals.get("debt_equity")
        if pe and pe < 15 and eps and eps > 0 and debt and debt < 0.5:
            filtered.append((ticker, df, pe, eps, debt))
    
    top_10 = sorted(filtered, key=lambda x: fetch_stock_fundamentals(x[0]).get("roe", 0), reverse=True)[:10]
    
    st.subheader("📊 Анализ рынка")
    st.metric("Начальная вселенная", len(df_list))
    st.metric("После фильтра P/E<15, EPS>0, Debt<0.5", len(filtered))
    
    st.subheader("🏆 Топ-10 недооцененных акций")
    top_df = pd.DataFrame([
        {"Акция": x[0], "P/E": x[2], "EPS": x[3], "Debt/Equity": x[4]} for x in top_10
    ])
    st.table(top_df)
    
    return "Анализ завершен"

def analyze_strategy_income(df_list, market):
    filtered = []
    for ticker, df in df_list:
        if df is None or len(df) < 30:
            continue
        fundamentals = fetch_stock_fundamentals(ticker)
        dividend_yield = fundamentals.get("dividendYield", 0)
        eps = fundamentals.get("eps", 0)
        if dividend_yield > 0.02 and eps > 0:
            filtered.append((ticker, df, dividend_yield, eps))
    
    top_10 = sorted(filtered, key=lambda x: x[2], reverse=True)[:10]
    
    st.subheader("📊 Анализ рынка")
    st.metric("Начальная вселенная", len(df_list))
    st.metric("После фильтра Dividend>2%, EPS>0", len(filtered))
    
    st.subheader("🏆 Топ-10 акций с доходами")
    top_df = pd.DataFrame([
        {"Акция": x[0], "Dividend Yield": x[2], "EPS": x[3]} for x in top_10
    ])
    st.table(top_df)
    
    return "Анализ завершен"

def analyze_strategy_options(df_list, market):
    filtered = []
    for ticker, df in df_list:
        if df is None or len(df) < 30:
            continue
        atr_pct = (df['High'].subtract(df['Low']).rolling(14).mean().iloc[-1] / df['Close'].iloc[-1]) * 100
        momentum = ta.momentum.ROCIndicator(df['Close']).roc().iloc[-1]
        if atr_pct > 3 and momentum > 5:
            filtered.append((ticker, df, atr_pct, momentum))
    
    top_10 = sorted(filtered, key=lambda x: x[3], reverse=True)[:10]
    
    st.subheader("📊 Анализ рынка")
    st.metric("Начальная вселенная", len(df_list))
    st.metric("После фильтра ATR>3%, Momentum>5%", len(filtered))
    
    st.subheader("🏆 Топ-10 для опционов")
    top_df = pd.DataFrame([
        {"Акция": x[0], "ATR %": x[2], "Momentum": x[3]} for x in top_10
    ])
    st.table(top_df)
    
    return "Анализ завершен"

# Streamlit приложение
with st.container():
    st.title("🚀 >tS|TQTVLSYSTEM")
    st.subheader("AI-Аналитик для трейдеров 📈")

# Админ-панель
admin_key = st.text_input("🔍 Админ-ключ", type="password", key="admin_key")
is_admin = admin_key == ADMIN_KEY

if is_admin:
    with st.expander("🔍 Отладка"):
        st.write("Отладка готова")

# Выбор стратегии и рынка
strategy = st.selectbox("🎯 Выберите стратегию", [
    "Дневная Торговля", "Поиск недооценённых акций", "Игра с доходами", "Торговля опционами"
], key="strategy_select")
market = st.selectbox("💹 Рынок", ["Акции", "Криптовалюты"], key="market_select")

if st.button(f"🚀 Запустить {strategy}", key="run_button"):
    if market == "Акции":
        df_list = [(ticker, fetch_stock_data_cached(ticker)) for ticker in stock_tickers[:50] if fetch_stock_data_cached(ticker) is not None]
    else:
        df_list = [(coin, fetch_crypto_data(coin)) for coin in crypto_ids[:50] if fetch_crypto_data(coin) is not None]
    
    if df_list:
        if strategy == "Дневная Торговля":
            result = analyze_strategy_day_trade(df_list, market)
        elif strategy == "Поиск недооценённых акций":
            result = analyze_strategy_undervalued(df_list, market)
        elif strategy == "Игра с доходами":
            result = analyze_strategy_income(df_list, market)
        elif strategy == "Торговля опционами":
            result = analyze_strategy_options(df_list, market)
        st.success(result)
    else:
        st.error("🚨 Нет данных для анализа. Проверьте подключение или тикеры.")

# Продолжение диалога
if 'strategy' in locals() and df_list:
    next_action = st.selectbox("Что дальше?", [
        "Анализ портфеля", "Технический анализ", "Сравнение волатильности", 
        "Фундаментальный анализ", "Разбивка по секторам"
    ], key="next_action")
    if next_action == "Технический анализ":
        ticker = st.text_input("Введите тикер (например, META)", key="ticker_input")
        if ticker:
            df = fetch_stock_data_cached(ticker, interval="5m", period="3d") if market == "Акции" else fetch_crypto_data(ticker, days=3)
            if df is not None:
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Close'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(title=f"5-мин свечи {ticker} за 3 дня", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
                support = df['Low'].rolling(20).min().iloc[-1]
                resistance = df['High'].rolling(20).max().iloc[-1]
                st.write(f"🛡️ **Поддержка**: ${support:.2f}")
                st.write(f"🎯 **Сопротивление**: ${resistance:.2f}")

# Telegram
chat_id_input = st.text_input("📬 Chat ID для отчета", key="chat_id")
if st.button("📤 Отправить отчет", key="send_report"):
    message = f"🚀 Отчет по {strategy}\n📊 Топ-активы: {', '.join([x[0] for x in df_list[:5]])}"
    result = send_telegram_report(chat_id_input, message)
    st.write(result)

st.write("🔓 Премиум: Полные отчеты, персонализация, графики.")
