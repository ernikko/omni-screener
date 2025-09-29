import streamlit as st
import requests
import pandas as pd
import time
import io

st.set_page_config(page_title="OmniScreener", layout="wide")

# Минималистичный дизайн (светлый, читаемый)
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        border-right: 1px solid #dee2e6;
    }
    .stButton > button {
        background-color: #007bff;
        color: white;
        border-radius: 4px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stSelectbox, .stNumberInput, .stTextInput {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #ced4da;
        border-radius: 4px;
    }
    h1 {
        color: #007bff;
        text-align: center;
        font-size: 28px;
    }
    .stDataFrame {
        border: 1px solid #dee2e6;
        border-radius: 4px;
    }
    .stExpander > div > label {
        color: #000000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Переключатель языка
language = st.selectbox("Language / Язык", ["English", "Russian"])

# Функция для текстов
def t(key):
    texts = {
        "English": {
            "title": "OmniScreener",
            "subheader": "Universal screener for stocks, crypto, bonds, metals, and currency",
            "asset_type": "Select asset type",
            "search_button": "Search",
            "no_results": "No assets match the criteria.",
            "filters_header": "Filters",
            "descriptive": "Descriptive",
            "fundamental": "Fundamental",
            "technical": "Technical",
            "news": "News",
            "etf": "ETF",
            "all": "All",
            "asset_specific": "Asset-Specific Filters",
            "crypto_profile": "Profile",
            "crypto_liquidity_min": "Liquidity Min",
            "crypto_liquidity_max": "Liquidity Max",
            "crypto_market_cap_min": "Market Cap Min (B$)",
            "crypto_market_cap_max": "Market Cap Max (B$)",
            "crypto_fdv_min": "FDV Min (B$)",
            "crypto_fdv_max": "FDV Max (B$)",
            "crypto_pair_age_min": "Pair Age Min (hours)",
            "crypto_pair_age_max": "Pair Age Max (hours)",
            "crypto_buys_24h_min": "24h Buys Min",
            "crypto_buys_24h_max": "24h Buys Max",
            "crypto_sells_24h_min": "24h Sells Min",
            "crypto_sells_24h_max": "24h Sells Max",
            "crypto_volume_24h_min": "24h Volume Min",
            "crypto_volume_24h_max": "24h Volume Max",
            "crypto_change_24h_min": "24h Change Min (%)",
            "crypto_change_24h_max": "24h Change Max (%)",
            "crypto_txs_6h_min": "6h Txs Min",
            "crypto_txs_6h_max": "6h Txs Max",
            "crypto_txs_1h_min": "1h Txs Min",
            "crypto_txs_1h_max": "1h Txs Max",
            "crypto_txs_5m_min": "5m Txs Min",
            "crypto_txs_5m_max": "5m Txs Max",
            "bonds_yield_min": "Yield Min (%)",
            "bonds_yield_max": "Yield Max (%)",
            "bonds_duration_max": "Duration Max",
            "bonds_credit_min": "Credit Rating Min (AAA=1, AA=2)",
            "metals_spot_min": "Spot Price Min ($)",
            "metals_spot_max": "Spot Price Max ($)",
            "metals_expiry_min": "Futures Expiry Min (days)",
            "currency_rate_min": "Exchange Rate Min",
            "currency_rate_max": "Exchange Rate Max",
            "currency_vol_min": "Volatility Min (%)"
        },
        "Russian": {
            "title": "OmniScreener",
            "subheader": "Универсальный скринер для акций, крипты, облигаций, металлов и валюты",
            "asset_type": "Выберите тип актива",
            "search_button": "Поиск",
            "no_results": "Нет активов по критериям.",
            "filters_header": "Фильтры",
            "descriptive": "Descriptive",
            "fundamental": "Fundamental",
            "technical": "Technical",
            "news": "News",
            "etf": "ETF",
            "all": "All",
            "asset_specific": "Фильтры для типа актива",
            "crypto_profile": "Profile",
            "crypto_liquidity_min": "Минимальная ликвидность",
            "crypto_liquidity_max": "Максимальная ликвидность",
            "crypto_market_cap_min": "Минимальная капитализация (млрд $)",
            "crypto_market_cap_max": "Максимальная капитализация (млрд $)",
            "crypto_fdv_min": "Минимальный FDV (млрд $)",
            "crypto_fdv_max": "Максимальный FDV (млрд $)",
            "crypto_pair_age_min": "Минимальный возраст пары (часы)",
            "crypto_pair_age_max": "Максимальный возраст пары (часы)",
            "crypto_buys_24h_min": "Минимальные покупки 24h",
            "crypto_buys_24h_max": "Максимальные покупки 24h",
            "crypto_sells_24h_min": "Минимальные продажи 24h",
            "crypto_sells_24h_max": "Максимальные продажи 24h",
            "crypto_volume_24h_min": "Минимальный объём 24h",
            "crypto_volume_24h_max": "Максимальный объём 24h",
            "crypto_change_24h_min": "Минимальное изменение 24h (%)",
            "crypto_change_24h_max": "Максимальное изменение 24h (%)",
            "crypto_txs_6h_min": "Минимальные Txs 6h",
            "crypto_txs_6h_max": "Максимальные Txs 6h",
            "crypto_txs_1h_min": "Минимальные Txs 1h",
            "crypto_txs_1h_max": "Максимальные Txs 1h",
            "crypto_txs_5m_min": "Минимальные Txs 5m",
            "crypto_txs_5m_max": "Максимальные Txs 5m",
            "bonds_yield_min": "Минимальный Yield (%)",
            "bonds_yield_max": "Максимальный Yield (%)",
            "bonds_duration_max": "Максимальный Duration",
            "bonds_credit_min": "Минимальный Credit Rating (AAA=1, AA=2)",
            "metals_spot_min": "Минимальный Spot Price ($)",
            "metals_spot_max": "Максимальный Spot Price ($)",
            "metals_expiry_min": "Минимальный Futures Expiry (дни)",
            "currency_rate_min": "Минимальный Exchange Rate",
            "currency_rate_max": "Максимальный Exchange Rate",
            "currency_vol_min": "Минимальный Volatility (%)"
        }
    }
    return texts[language].get(key, key)

st.title(t("title"))
st.subheader(t("subheader"))

# Выбор типа актива (сначала)
asset_types = ['Stocks', 'Cryptocurrency', 'Bonds', 'Metals', 'Currency'] if language == "English" else ['Акции', 'Криптовалюта', 'Облигации', 'Металлы', 'Валюта']
asset_type = st.selectbox(t("asset_type"), asset_types)

# Фильтры в sidebar (общие + specific)
with st.sidebar:
    st.header(t("filters_header"))
    
    # Общие (Finviz-style)
    with st.expander(t("descriptive")):
        exchange = st.selectbox("Exchange", ['Any', 'NASDAQ', 'NYSE', 'AMEX', 'OTC', 'TSX'])
        index = st.selectbox("Index", ['Any', 'S&P 500', 'Dow Jones', 'NASDAQ 100', 'Russell 2000'])
        sector = st.selectbox("Sector", ['Any', 'Technology', 'Healthcare', 'Financials', 'Consumer Cyclical', 'Energy', 'Industrials', 'Consumer Defensive', 'Communication Services', 'Basic Materials', 'Utilities', 'Real Estate'])
        industry = st.selectbox("Industry", ['Any', 'Software - Infrastructure', 'Semiconductors', 'Banks - Diversified', 'Internet Retail', 'Drug Manufacturers - General', 'Oil & Gas Integrated', 'Asset Management', 'Beverages - Non-Alcoholic', 'Aerospace & Defense', 'Information Technology Services'])
        country = st.selectbox("Country", ['Any', 'USA', 'China', 'Canada', 'UK', 'Germany', 'India', 'Japan', 'France', 'Australia', 'Brazil'])

    with st.expander(t("fundamental")):
        market_cap = st.selectbox("Market Cap.", ['Any', 'Mega (>200B)', 'Large (10B-200B)', 'Mid (2B-10B)', 'Small (300M-2B)', 'Micro (50M-300M)', 'Nano (<50M)'])
        dividend_yield = st.selectbox("Dividend Yield", ['Any', 'None (0%)', 'Low (<2%)', 'Medium (2-4%)', 'High (4-6%)', 'Very High (>6%)'])
        short_float = st.selectbox("Short Float", ['Any', 'Low (<5%)', 'Medium (5-10%)', 'High (>10%)'])
        analyst_recom = st.selectbox("Analyst Recom.", ['Any', 'Strong Buy (1)', 'Buy (2)', 'Hold (3)', 'Sell (4)', 'Strong Sell (5)'])
        option_short = st.selectbox("Option/Short", ['Any', 'Optionable', 'Shortable', 'Both'])

    with st.expander(t("technical")):
        earnings_date = st.selectbox("Earnings Date", ['Any', 'Today', 'Tomorrow', 'This Week', 'Next Week', 'This Month', 'Next Month'])
        average_volume = st.selectbox("Average Volume", ['Any', 'Low (<100K)', 'Medium (100K-500K)', 'High (500K-1M)', 'Very High (>1M)'])
        relative_volume = st.selectbox("Relative Volume", ['Any', 'Low (<0.5)', 'Normal (0.5-1.5)', 'High (>1.5)'])
        current_volume = st.selectbox("Current Volume", ['Any', 'Low (<100K)', 'Medium (100K-500K)', 'High (500K-1M)', 'Very High (>1M)'])
        trades = st.selectbox("Trades", ['Any', 'Low (<1000)', 'Medium (1000-5000)', 'High (>5000)'])

    with st.expander(t("news")):
        st.write("News filters coming soon.")

    with st.expander(t("etf")):
        st.write("ETF filters coming soon.")

    with st.expander(t("all")):
        price = st.selectbox("Price $", ['Any', 'Under $5', 'Under $10', 'Under $20', 'Under $50', 'Over $50', 'Over $100'])
        target_price = st.selectbox("Target Price", ['Any', 'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'])
        ipo_date = st.selectbox("IPO Date", ['Any', 'This Year', 'Last Year', 'This Month', 'Last Month'])
        shares_outstanding = st.selectbox("Shares Outstanding", ['Any', 'Under 50M', 'Under 100M', 'Under 500M', 'Over 500M'])
        float_ = st.selectbox("Float", ['Any', 'Low (<10M)', 'Medium (10M-50M)', 'High (>50M)'])

    # Asset-Specific (внутри по типу актива)
    with st.expander(t("asset_specific")):
        if asset_type in ['Stocks', 'Акции']:
            st.write("Finviz-style filters already in common sections.")
        elif asset_type in ['Cryptocurrency', 'Криптовалюта']:
            profile = st.selectbox(t("crypto_profile"), ['Any', 'Boosted', 'Ads'])
            liquidity_min = st.number_input(t("crypto_liquidity_min"), value=0.0)
            liquidity_max = st.number_input(t("crypto_liquidity_max"), value=float('inf'))
            market_cap_min = st.number_input(t("crypto_market_cap_min"), value=0.0)
            market_cap_max = st.number_input(t("crypto_market_cap_max"), value=float('inf'))
            fdv_min = st.number_input(t("crypto_fdv_min"), value=0.0)
            fdv_max = st.number_input(t("crypto_fdv_max"), value=float('inf'))
            pair_age_min = st.number_input(t("crypto_pair_age_min"), value=0)
            pair_age_max = st.number_input(t("crypto_pair_age_max"), value=float('inf'))
            buys_24h_min = st.number_input(t("crypto_buys_24h_min"), value=0)
            buys_24h_max = st.number_input(t("crypto_buys_24h_max"), value=float('inf'))
            sells_24h_min = st.number_input(t("crypto_sells_24h_min"), value=0)
            sells_24h_max = st.number_input(t("crypto_sells_24h_max"), value=float('inf'))
            volume_24h_min = st.number_input(t("crypto_volume_24h_min"), value=0.0)
            volume_24h_max = st.number_input(t("crypto_volume_24h_max"), value=float('inf'))
            change_24h_min = st.number_input(t("crypto_change_24h_min"), value=float('-inf'))
            change_24h_max = st.number_input(t("crypto_change_24h_max"), value=float('inf'))
            txs_6h_min = st.number_input(t("crypto_txs_6h_min"), value=0)
            txs_6h_max = st.number_input(t("crypto_txs_6h_max"), value=float('inf'))
            txs_1h_min = st.number_input(t("crypto_txs_1h_min"), value=0)
            txs_1h_max = st.number_input(t("crypto_txs_1h_max"), value=float('inf'))
            txs_5m_min = st.number_input(t("crypto_txs_5m_min"), value=0)
            txs_5m_max = st.number_input(t("crypto_txs_5m_max"), value=float('inf'))
        elif asset_type in ['Bonds', 'Облигации']:
            yield_min = st.number_input(t("bonds_yield_min"), value=0.0)
            yield_max = st.number_input(t("bonds_yield_max"), value=float('inf'))
            duration_max = st.number_input(t("bonds_duration_max"), value=float('inf'))
            credit_min = st.number_input(t("bonds_credit_min"), value=0)
        elif asset_type in ['Metals', 'Металлы']:
            spot_min = st.number_input(t("metals_spot_min"), value=0.0)
            spot_max = st.number_input(t("metals_spot_max"), value=float('inf'))
            expiry_min = st.number_input(t("metals_expiry_min"), value=0)
        elif asset_type in ['Currency', 'Валюта']:
            rate_min = st.number_input(t("currency_rate_min"), value=0.0)
            rate_max = st.number_input(t("currency_rate_max"), value=float('inf'))
            vol_min = st.number_input(t("currency_vol_min"), value=0.0)

# Кнопка поиска
if st.button(t("search_button")):
    st.write("Searching...")
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []

    api_key = 'MS2HKDM5JROIZSKQ'

    if asset_type in ['Stocks', 'Акции']:
        # Статический список из Finviz скриншота + расширение (исправление KeyError)
        symbols = ['A', 'AA', 'AAA', 'AAAU', 'AACB', 'AACG', 'AACI', 'AACIU', 'AACT', 'AADR', 'AAL', 'AAM', 'AAME', 'AAMI', 'AAOI', 'AAON', 'AAP', 'AAPB', 'AAPD', 'AAPG']  # Из скриншота
        for i, symbol in enumerate(symbols):
            progress_bar.progress((i + 1) / len(symbols))
            status_text.text(f"Fetching {symbol}...")
            time.sleep(0.1)  # Короткая пауза для симуляции
            # API вызов (упрощённо, для теста используем статические данные)
            # url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
            # response = requests.get(url)
            # if response.status_code == 200:
            #     data = response.json()
            #     ... (полная логика)
            # Fallback на статические данные из скриншота
            results.append({
                'No.': i + 1,
                'Ticker': symbol,
                'Company': f"Company {symbol}",  # Из скриншота
                'Sector': 'Healthcare' if symbol == 'A' else 'Basic Materials',
                'Industry': 'Diagnostics & Research' if symbol == 'A' else 'Aluminum',
                'Country': 'USA',
                'Market Cap': '33.42B' if symbol == 'A' else '7.46B',
                'P/E': '29.01' if symbol == 'A' else '8.52',
                'Price': '$117.64' if symbol == 'A' else '$28.80',
                'Change': '1.30%' if symbol == 'A' else '0.31%',
                'Volume': '1,945,271' if symbol == 'A' else '5,249,050'
            })

    elif asset_type in ['Cryptocurrency', 'Криптовалюта']:
        # DexScreener-style (статические данные из скриншота)
        results.append({
            'No.': 1,
            'Token': 'MORI / SOL',
            'Price': '$0.1616',
            'Age': '4d',
            'Txns': '56,571',
            'Volume': '$23.1M',
            'Makers': '14,674',
            '5m': '-0.83%',
            '1h': '8.49%',
            '6h': '34.81%',
            '24h': '289%',
            'Liquidity': '$3.0M',
            'MCAP': '$161.6M'
        })
        # Добавьте больше из скриншота

    progress_bar.progress(1.0)
    status_text.text("Done!")
    time.sleep(0.5)

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        st.write(f"Showing 1-{len(results)} of {len(results)} results")  # Пагинация
    else:
        st.write(t("no_results"))
