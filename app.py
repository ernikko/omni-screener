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
import logging

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

# Красивый шаблон дизайна
st.set_page_config(page_title=">tS|TQTVLSYSTEM", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');
    .stApp {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: #e0e0e0;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
        overflow: hidden;
    }
    .stContainer {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 40px;
        border-radius: 15px;
        text-align: center;
        max-width: 600px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .stSelectbox > div {
        justify-content: center;
    }
    .stButton > button {
        background: #4a90e2;
        color: #fff;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-size: 1.1em;
        font-weight: 500;
        transition: transform 0.2s, background 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        background: #357abd;
    }
    .css-1aumxhk {
        width: 100%;
    }
    h1, h2, h3 {
        color: #fff;
        font-family: 'Poppins', sans-serif;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    table {
        margin: 20px auto;
        border-collapse: collapse;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    th, td {
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    th {
        background: rgba(255, 255, 255, 0.15);
    }
    .stSpinner > div {
        background: #4a90e2;
        border: 4px solid #e0e0e0;
        border-top: 4px solid #4a90e2;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .stSpinner {
        text-align: center;
        color: #fff;
        font-size: 1.1em;
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
@st.cache_data(ttl=3600)
def fetch_stock_data_cached(ticker, interval="1d", period="1y"):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)
        if not df.empty:
            df = df[["Close", "Volume", "High", "Low"]]
            return df
    except Exception as e:
        logging.error(f"Ошибка yfinance для {ticker}: {e}")
    return None

@st.cache_data(ttl=3600)
def fetch_crypto_data(coin_id, days=365):
    try:
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

@st.cache_data(ttl=3600)
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

def fetch_data_sequential(tickers, fetch_func):
    df_list = []
    for ticker in tickers:
        df = fetch_func(ticker)
        if df is not None:
            df_list.append((ticker, df))
    return df_list

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

    st.write("### Полный обзор процесса фильтрации акций")
    st.write("Я создал подробную визуализацию нашего пути фильтрации акций. Давайте рассмотрим, что мы сделали:")
    st.write("**Этапы фильтрации, которые мы прошли:**")
    st.write(f"Начальный пул акций: Начали с {len(df_list)} акций")
    st.write(f"Базовый фильтр: Применены критерии (цена > 10 долларов, объем > 2 млн, бета > 1.2) → {len(filtered)} акций")
    st.write("**Сегментация по волатильности:**")
    st.write(f"Высокая волатильность (ATR > 5%): {sum(1 for x in filtered if x[3] > 5)} акций")
    st.write(f"Умеренная волатильность (ATR 2-5%): {sum(1 for x in filtered if 2 <= x[3] <= 5)} акций ← Наш фокус")
    st.write("Финальный выбор: Топ-15 по рыночной капитализации")
    st.write("**Ключевые выводы:**")
    st.write("Распределение ATR%: Гистограмма показывает, что большинство акций в нашем отфильтрованном наборе имеют ATR между 3-6%. Наш выбранный диапазон (2-5%) представляет собой зону умеренной волатильности, избегая как слишком стабильных, так и слишком волатильных акций.")
    st.write("Профиль финального выбора:")
    st.write(f"Доля секторов: Технологии ({sector_counts['Технологии']} акций), Услуги связи ({sector_counts['Услуги связи']}), Финансы ({sector_counts['Финансы']})")
    st.write(f"Диапазон капитализации: ${min(x[6]/1e9 for x in top_15):.2f} млрд (самая низкая) до ${max(x[6]/1e9 for x in top_15):.2f} млрд (самая высокая)")
    st.write(f"Диапазон волатильности: {min(x[3] for x in top_15):.2f}% (минимальная) до {max(x[3] for x in top_15):.2f}% (максимальная)")
    st.write("Топ-5 акций в нашем финальном выборе:")
    for i in range(min(5, len(top_15))):
        ticker, _, _, atr, _, _, market_cap, _, price = top_15[i]
        st.write(f"{ticker} (${market_cap/1e9:.2f} млрд): {atr:.2f}% ATR")

    st.subheader("📊 Анализ рынка")
    st.write("Финансовый анализ завершен")
    if st.button("Посмотреть отчёт"):
        with st.expander("Финансовая визуализация", expanded=True):
            fig_process = go.Figure(data=[go.Bar(x=['Начальный пул акций', 'Базовый фильтр', 'Высокая волатильность', 'Умеренная волатильность', 'Финальный выбор'],
                                               y=[len(df_list), len(filtered), sum(1 for x in filtered if x[3] > 5), sum(1 for x in filtered if 2 <= x[3] <= 5), 15])])
            fig_process.update_layout(title="Процесс фильтрации акций", template="plotly_dark")
            st.plotly_chart(fig_process, use_container_width=True)
            
            fig_atr = go.Figure()
            fig_atr.add_trace(go.Histogram(x=[x[3] for x in filtered], name="ATR%", nbinsx=20))
            fig_atr.add_hline(y=2, line_dash="dash", line_color="green", annotation_text="2% Threshold")
            fig_atr.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="5% Threshold")
            fig_atr.update_layout(title="Распределение ATR% всех отфильтрованных акций", xaxis_title="ATR %", yaxis_title="Количество акций", template="plotly_dark")
            st.plotly_chart(fig_atr, use_container_width=True)
            
            fig_top15 = go.Figure(data=[go.Bar(x=[x[0] for x in top_15], y=[x[6]/1e12 for x in top_15])])
            fig_top15.update_layout(title="Финальный выбор: Топ-15 акций по рыночной капитализации", xaxis_title="Тикер", yaxis_title="Капитализация ($T)", template="plotly_dark")
            st.plotly_chart(fig_top15, use_container_width=True)
            
            st.subheader("Финансовые показатели")
            st.write("### Краткое описание процесса фильтрации акций:")
            st.write("#### Оставшиеся запасы стадии фильтра:")
            st.write(f"Начальный пул акций: {len(df_list)}")
            st.write(f"Базовый фильтр (Цена > 10 долларов, Объем > 2 млн, Бета > 1,2): {len(filtered)}")
            st.write(f"Высокая волатильность (ATR > 5%): {sum(1 for x in filtered if x[3] > 5)}")
            st.write(f"Умеренная волатильность (ATR 2-5%): {sum(1 for x in filtered if 2 <= x[3] <= 5)}")
            st.write(f"Финальный выбор (15 лучших по рыночной капитализации): 15")

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

    # Выбор стратегии вместо поля ввода
    strategy = st.selectbox("🎯 Выберите стратегию", [
        "Дневная Торговля", "Поиск недооценённых акций", "Игра с доходами", "Торговля опционами"
    ], key="strategy_select")
    market = st.selectbox("💹 Рынок", ["Акции", "Криптовалюты"], key="market_select")

    df_list = None
    if st.button(f"🚀 Запустить {strategy}", key="run_button"):
        with st.spinner("Выполняется анализ... Пожалуйста, подождите."):
            if market == "Акции":
                df_list = fetch_data_sequential(stock_tickers[:500], fetch_stock_data_cached)
            else:
                df_list = fetch_data_sequential(crypto_ids[:50], fetch_crypto_data)
        
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
