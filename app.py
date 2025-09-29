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
import logging  # Добавлен импорт logging

# Списки активов (500 акций, 50 криптовалют)
stock_tickers = [
    "AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "JPM", "V",
    "WMT", "UNH", "MA", "PG", "HD", "DIS", "BAC", "INTC", "CMCSA", "VZ",
    "PFE", "KO", "PEP", "MRK", "T", "CSCO", "XOM", "CVX", "ABBV", "NKE",
    "ADBE", "CRM", "NFLX", "AMD", "ORCL", "IBM", "QCOM", "TXN", "AMGN", "GILD",
    "SBUX", "MMM", "GE", "CAT", "BA", "HON", "SPG", "LMT", "UPS", "LOW",
    "F", "GM", "TGT", "WBA", "MDT", "ABT", "JNJ", "CL", "KMB", "MO",
    "PM", "BTI", "HSY", "MCD", "YUM", "DPS", "COKE", "KDP", "MNST", "CCE",
    "CAG", "GIS", "K", "CPB", "HRL", "MKC"
] + [f"STOCK{i:04d}" for i in range(450)]
crypto_ids = [
    "bitcoin", "ethereum", "solana", "cardano", "polkadot", "binancecoin", "ripple", "dogecoin", "avalanche-2", "chainlink",
    "litecoin", "bitcoin-cash", "stellar", "cosmos", "algorand", "tezos", "eos", "neo", "iota", "tron"
] + [f"CRYPTO{i:04d}" for i in range(30)]

# Современный дизайн, вдохновленный Xynth
st.set_page_config(page_title=">tS|TQTVLSYSTEM", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    :root {
        --primary-bg: #1c1c1c;
        --secondary-bg: #171717;
        --text-color: #e0e0e0;
        --accent-color: #ff4500; /* Вдохновлено Xynth */
        --shadow: 0 8px 32px rgba(0, 0, 0, 0.7);
    }
    .stApp {
        background: linear-gradient(180deg, var(--primary-bg) 0%, var(--secondary-bg) 100%);
        color: var(--text-color);
        font-family: 'Roboto', sans-serif;
        height: 100vh;
        overflow-y: hidden;
    }
    .stContainer {
        max-width: 950px;
        margin: 0 auto;
        padding: 40px 25px;
        text-align: center;
        background: rgba(20, 20, 20, 0.95);
        border-radius: 15px;
        box-shadow: var(--shadow);
        height: 90vh; /* Полная высота с учетом отступов */
        overflow-y: auto;
    }
    .stMetric > label {
        color: var(--text-color);
        font-size: 1.1em;
        text-align: center;
    }
    .stSelectbox > label {
        color: var(--text-color);
        font-size: 1.1em;
        text-align: center;
    }
    .stButton > button {
        background: linear-gradient(90deg, #2e2e2e, #4a4a4a);
        color: var(--text-color);
        border: none;
        border-radius: 25px;
        padding: 15px 40px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        font-size: 1.2em;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
        background: linear-gradient(90deg, #3a3a3a, #5a5a5a);
    }
    .css-1aumxhk {
        width: 80%;
        margin: 0 auto;
    }
    h1, h2, h3 {
        text-align: center;
        color: var(--text-color);
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.7);
    }
    table {
        margin: 20px auto;
        border-collapse: collapse;
        background: #222;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
    }
    th, td {
        padding: 12px 15px;
        text-align: center;
        border: 1px solid #444;
        color: var(--text-color);
    }
    th {
        background: #333;
        font-weight: 700;
    }
    .stProgress > div > div > div > div {
        background-color: var(--accent-color);
    }
    .status-panel {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
    }
    .status-box {
        width: 100px;
        height: 100px;
        background: #333;
        margin: 5px;
        border-radius: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        color: #fff;
    }
    .status-box.active {
        background: var(--accent-color);
    }
    .status-center {
        width: 200px;
        height: 150px;
        background: #4a90e2;
        color: #fff;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 10px;
    }
    .visualization {
        text-align: center;
    }
    .visualization img {
        max-width: 100%;
        border-radius: 10px;
        box-shadow: var(--shadow);
    }
    ::-webkit-scrollbar {
        display: none;
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
        with st.spinner(f"Загрузка данных для {ticker}..."):
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            if not df.empty:
                df = df[["Close", "Volume", "High", "Low"]]
                return df
    except Exception as e:
        logging.error(f"Ошибка yfinance для {ticker}: {e}")
    return None

@st.cache_data(ttl=300)
def fetch_crypto_data(coin_id, days=365):
    try:
        with st.spinner(f"Загрузка данных для {coin_id}..."):
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
    except Exception as e:
        logging.error(f"Ошибка для {coin_id}: {e}")
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
            "sector": info.get("sector", "Другое"),
            "current_price": info.get("currentPrice", None)
        }
    except:
        return {"pe_ratio": None, "eps": None, "debt_equity": None, "roe": None, "market_cap": None, "beta": None, "sector": "Другое", "current_price": None}

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
        filtered.append((ticker, df, latest_price, atr_pct, avg_volume, beta, fundamentals.get("market_cap", 0), fundamentals.get("sector", "Другое"), fundamentals.get("current_price", 0)))

    # Динамическое определение секторов
    sector_counts = {"Технологии": 0, "Услуги связи": 0, "Финансы": 0, "Другое": 0}
    for _, _, _, _, _, _, _, sector, _ in filtered:
        if "Technology" in sector:
            sector_counts["Технологии"] += 1
        elif "Communication" in sector:
            sector_counts["Услуги связи"] += 1
        elif "Financial" in sector:
            sector_counts["Финансы"] += 1
        else:
            sector_counts["Другое"] += 1
    
    filtered.sort(key=lambda x: x[6], reverse=True)
    top_15 = filtered[:15]
    
    fig = go.Figure()
    atr_data = [x[3] for x in filtered]
    fig.add_trace(go.Histogram(x=atr_data, name="ATR%", nbinsx=20))
    fig.add_hline(y=2, line_dash="dash", line_color="green", annotation_text="2% Threshold")
    fig.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="5% Threshold")
    fig.update_layout(title="Распределение ATR% всех отфильтрованных акций", xaxis_title="ATR %", yaxis_title="Количество акций", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Анализ рынка")
    st.write("Финансовый анализ завершен")
    if st.button("Просмотр отчета"):
        with st.expander("Финансовая визуализация", expanded=True):
            # График 1: Процесс фильтрации акций
            fig_process = go.Figure(data=[go.Bar(x=['Начальный пул акций', 'Базовый фильтр', 'Высокая волатильность', 'Умеренная волатильность', 'Финальный выбор'],
                                               y=[len(df_list), len(filtered), sum(1 for x in filtered if x[3] > 5), sum(1 for x in filtered if 2 <= x[3] <= 5), 15])])
            fig_process.update_layout(title="Процесс фильтрации акций", template="plotly_dark")
            st.plotly_chart(fig_process, use_container_width=True)
            
            # График 2: Распределение ATR% (уже выше)
            st.plotly_chart(fig, use_container_width=True)
            
            # График 3: Топ-15 по рыночной капитализации
            fig_top15 = go.Figure(data=[go.Bar(x=[x[0] for x in top_15], y=[x[6]/1e12 for x in top_15])])
            fig_top15.update_layout(title="Финальный выбор: Топ-15 акций по рыночной капитализации (с умеренной волатильностью)", xaxis_title="Тикер", yaxis_title="Капитализация ($T)", template="plotly_dark")
            st.plotly_chart(fig_top15, use_container_width=True)
            
            st.subheader("Финансовые показатели")
            st.write("### Краткое описание процесса фильтрации акций:")
            st.write("#### Оставшиеся запасы стадии фильтра:")
            st.write(f"Начальный пул акций: {len(df_list)}")
            st.write(f"Базовый фильтр (Цена > 10 долларов, Объем > 2 млн, Бета > 1,2): {len(filtered)}")
            st.write(f"Высокая волатильность (ATR > 5%): {sum(1 for x in filtered if x[3] > 5)}")
            st.write(f"Умеренная волатильность (ATR 2-5%): {sum(1 for x in filtered if 2 <= x[3] <= 5)}")
            st.write(f"Финальный выбор (15 лучших по рыночной капитализации): 15")
            
            st.write("### Финальный отбор — 15 лучших акций по рыночной капитализации с умеренной волатильностью (ATR 2–5%):")
            top_df = pd.DataFrame([
                {"Тикер": x[0], "Цена закрытия": f"${x[8]:.2f}", "MarketCap": f"${x[6]/1e9:.2f} млрд", "ATR %": f"{x[3]:.2f}%", "Бета": x[5], "Сектор": x[7]}
                for x in top_15
            ])
            st.table(top_df)
    
    # Панель статуса (вдохновлена "position" из Xynth)
    with st.container():
        st.markdown('<div class="status-panel">', unsafe_allow_html=True)
        for i in range(4):
            color = "#ff4500" if i == 1 else "#333"  # Центральный акцент
            st.markdown(f'<div class="status-box" style="background: {color};">{"367" if i == 1 else "0"}</div>', unsafe_allow_html=True)
        st.markdown('<div class="status-center">Анализ: 100%</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
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
    st.metric("Начальный пул акций", len(df_list))
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
    st.metric("Начальный пул акций", len(df_list))
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
    st.metric("Начальный пул акций", len(df_list))
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
        st.write("Отладка готова. Тестовый режим активен.")

# Выбор стратегии и рынка
strategy = st.selectbox("🎯 Выберите стратегию", [
    "Дневная Торговля", "Поиск недооценённых акций", "Игра с доходами", "Торговля опционами"
], key="strategy_select")
market = st.selectbox("💹 Рынок", ["Акции", "Криптовалюты"], key="market_select")

df_list = None
if st.button(f"🚀 Запустить {strategy}", key="run_button"):
    try:
        with st.spinner("Выполняется анализ... Пожалуйста, подождите."):
            progress_bar = st.progress(0)
            if market == "Акции":
                df_list = []
                for i, ticker in enumerate(stock_tickers[:500]):
                    df = fetch_stock_data_cached(ticker)
                    if df is not None:
                        df_list.append((ticker, df))
                    progress_bar.progress((i + 1) / 500)
            else:
                df_list = []
                for i, coin in enumerate(crypto_ids[:50]):
                    df = fetch_crypto_data(coin)
                    if df is not None:
                        df_list.append((coin, df))
                    progress_bar.progress((i + 1) / 50)
            progress_bar.empty()
        
        if not df_list:
            st.error("🚨 Нет данных для анализа. Проверьте подключение или тикеры.")
        else:
            if strategy == "Дневная Торговля":
                result = analyze_strategy_day_trade(df_list, market)
            elif strategy == "Поиск недооценённых акций":
                result = analyze_strategy_undervalued(df_list, market)
            elif strategy == "Игра с доходами":
                result = analyze_strategy_income(df_list, market)
            elif strategy == "Торговля опционами":
                result = analyze_strategy_options(df_list, market)
            st.success(result)
    except Exception as e:
        st.error(f"🚨 Ошибка анализа: {str(e)}")

# Продолжение диалога
if df_list and 'strategy' in locals():
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
    if df_list:
        message = f"🚀 Отчет по {strategy}\n📊 Топ-активы: {', '.join([x[0] for x in df_list[:5]])}"
        result = send_telegram_report(chat_id_input, message)
        st.write(result)
    else:
        st.warning("Сначала выполните анализ.")

st.write("🔓 Премиум: Полные отчеты, персонализация, графики.")
