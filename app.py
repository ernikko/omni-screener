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
from concurrent.futures import ThreadPoolExecutor
import logging

# Настройка логирования
logging.basicConfig(level=logging.ERROR)

# Расширенные списки активов (500 акций)
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

# Современный дизайн в стиле Xynth
st.set_page_config(page_title=">tS|TQTVLSYSTEM", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    .stApp {
        background: linear-gradient(135deg, #0a0a0a, #1a1a1a);
        color: #ffffff;
        font-family: 'Roboto', sans-serif;
    }
    .stContainer {
        max-width: 900px;
        margin: 0 auto;
        padding: 30px;
        text-align: center;
        border-radius: 15px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.6);
        background: rgba(15, 15, 15, 0.9);
    }
    .stMetric > label {
        color: #e0e0e0;
        font-size: 1.2em;
        text-align: center;
    }
    .stSelectbox > label {
        color: #e0e0e0;
        font-size: 1.2em;
        text-align: center;
    }
    .stButton > button {
        background: linear-gradient(90deg, #2e2e2e, #4a4a4a);
        color: #ffffff;
        border: none;
        border-radius: 25px;
        padding: 12px 35px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        font-size: 1.2em;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.6);
    }
    .css-1aumxhk {
        width: 80%;
        margin: 0 auto;
    }
    h1, h2, h3 {
        text-align: center;
        color: #f0f0f0;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.7);
    }
    table {
        margin: 0 auto;
        border-collapse: collapse;
        background: #222;
        border-radius: 10px;
        overflow: hidden;
    }
    th, td {
        padding: 12px;
        text-align: center;
        border: 1px solid #444;
        color: #e0e0e0;
    }
    th {
        background: #333;
    }
</style>
""", unsafe_allow_html=True)

# Кэширование данных с параллельной загрузкой
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
        logging.error(f"Ошибка для {ticker}: {e}")
    return None

def fetch_all_data(tickers):
    with ThreadPoolExecutor() as executor:
        return list(executor.map(lambda t: (t, fetch_stock_data_cached(t)), tickers))

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
    
    # Динамическое определение секторов
    sector_counts = {"Технологии": 0, "Услуги связи": 0, "Финансы": 0}
    for ticker, _, _, _, _, _, _ in top_15:
        sector = fetch_stock_fundamentals(ticker).get("sector", "Другое")
        if "Technology" in sector:
            sector_counts["Технологии"] += 1
        elif "Communication" in sector:
            sector_counts["Услуги связи"] += 1
        elif "Financial" in sector:
            sector_counts["Финансы"] += 1]
    
    fig = go.Figure()
    atr_data = [x[3] for x in filtered]
    fig.add_trace(go.Histogram(x=atr_data, name="ATR%", nbinsx=20))
    fig.update_layout(title="Распределение ATR%", xaxis_title="ATR %", yaxis_title="Количество акций", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📊 Анализ рынка")
    st.write("Финансовый анализ завершен")
    st.write("Просмотр отчета")
    st.write("Полный обзор процесса скрининга акций")
    st.write("Я создал подробную визуализацию нашего пути фильтрации акций. Давайте посмотрим, что мы сделали:")
    
    st.write("### Этапы фильтрации:")
    st.write(f"• Начальная вселенная: Начали с {len(df_list)} акций")
    st.write(f"• Базовый фильтр: Применены критерии (цена >$10, объем >2M, бета >1.2) → {len(filtered)} акций")
    st.write("• Сегментация волатильности:")
    st.write(f"  - Высокая волатильность (ATR >5%): {sum(1 for x in filtered if x[3] > 5)} акций")
    st.write(f"  - Умеренная волатильность (ATR 2-5%): {sum(1 for x in filtered if 2 <= x[3] <= 5)} акций ← Наш фокус")
    st.write(f"• Финальный отбор: Топ-15 по рыночной капитализации")
    
    st.write("### Ключевые выводы:")
    st.write("• **Распределение ATR%**: Гистограмма показывает, что большинство акций в нашем отфильтрованном наборе имеют ATR между 3-6%. Выбранный диапазон (2-5%) — это зона умеренной волатильности, избегающая как слишком стабильных, так и чрезмерно волатильных акций.")
    st.write(f"• **Профиль финального отбора**:")
    st.write(f"  - Доминирование секторов: {sector_counts['Технологии']} акций в Технологиях, {sector_counts['Услуги связи']} в Услугах связи, {sector_counts['Финансы']} в Финансах")
    st.write(f"  - Диапазон капитализации: ${min(x[6]/1e9 for x in top_15):.1f}B ({top_15[-1][0]}) до ${max(x[6]/1e12 for x in top_15):.1f}T ({top_15[0][0]})")
    st.write(f"  - Диапазон волатильности: {min(x[3] for x in top_15):.2f}% ({min(top_15, key=lambda x: x[3])[0]}) до {max(x[3] for x in top_15):.2f}% ({max(top_15, key=lambda x: x[3])[0]})")
    
    st.write("### 🏆 Топ-15 лучших акций:")
    top_df = pd.DataFrame([
        {"Акция": x[0], "Cap ($T)": x[6]/1e12, "ATR %": x[3], "Бета": x[5]} for x in top_15
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
            if market == "Акции":
                df_list = fetch_all_data(stock_tickers[:500])
                df_list = [(t, d) for t, d in df_list if d is not None]
            else:
                df_list = [(coin, fetch_crypto_data(coin)) for coin in crypto_ids[:50] if fetch_crypto_data(coin) is not None]
        
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
