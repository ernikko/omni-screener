import streamlit as st
import requests
import pandas as pd
import time  # Для пауз в API
import io  # Для парсинга CSV

# Дизайн: Темная тема как DexScreener (черный фон, белый текст, синие акценты)
st.markdown("""
<style>
    .stApp {
        background-color: #121212;
        color: #ffffff;
    }
    .sidebar .sidebar-content {
        background-color: #1e1e1e;
        border-right: 1px solid #333333;
    }
    .stButton > button {
        background-color: #1f77b4;
        color: #ffffff;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
        border: none;
    }
    .stButton > button:hover {
        background-color: #155e8d;
    }
    .stSelectbox, .stNumberInput, .stTextInput {
        background-color: #1e1e1e;
        color: #ffffff;
        border: 1px solid #333333;
        border-radius: 4px;
        padding: 5px;
    }
    .stCheckbox label {
        color: #ffffff;
    }
    h1 {
        color: #ffffff;
        text-align: center;
        font-size: 32px;
        margin-bottom: 20px;
    }
    .stDataFrame {
        border: none;
        overflow: auto;
        font-size: 12px;
    }
    .stDataFrame table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }
    .stDataFrame th {
        background-color: #1e1e1e;
        color: #ffffff;
        padding: 8px;
        text-align: left;
        border-bottom: 1px solid #333333;
        position: sticky;
        top: 0;
        z-index: 2;
    }
    .stDataFrame td {
        padding: 8px;
        border-bottom: 1px solid #333333;
        color: #ffffff;
    }
    .stExpander {
        background-color: #1e1e1e;
        border: 1px solid #333333;
        border-radius: 4px;
    }
    .stExpander > div > label {
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Переключатель языка
language = st.selectbox("Select Language / Выберите язык", ["English", "Russian"])

# Функция для текстов по языку
def t(key):
    texts = {
        "English": {
            "title": "OmniScreener",
            "subheader": "Universal screener for stocks, crypto, bonds, metals, and currency",
            "asset_type": "Select asset type",
            "search_button": "Search assets",
            "no_results": "No assets match the criteria.",
            "filters_header": "Filters",
            "descriptive": "Descriptive",
            "fundamental": "Fundamental",
            "technical": "Technical",
            "news": "News",
            "etf": "ETF",
            "all": "All",
            "exchange": "Exchange",
            "index": "Index",
            "sector": "Sector",
            "industry": "Industry",
            "country": "Country",
            "market_cap": "Market Cap",
            "dividend_yield": "Dividend Yield",
            "short_float": "Short Float",
            "analyst_recom": "Analyst Recom",
            "option_short": "Option/Short",
            "earnings_date": "Earnings Date",
            "average_volume": "Average Volume",
            "relative_volume": "Relative Volume",
            "current_volume": "Current Volume",
            "trades": "Trades",
            "price": "Price",
            "target_price": "Target Price",
            "ipo_date": "IPO Date",
            "shares_outstanding": "Shares Outstanding",
            "float": "Float"
        },
        "Russian": {
            "title": "OmniScreener",
            "subheader": "Универсальный скринер для акций, крипты, облигаций, металлов и валюты",
            "asset_type": "Выберите тип актива",
            "search_button": "Поиск активов",
            "no_results": "Нет активов по критериям.",
            "filters_header": "Фильтры",
            "descriptive": "Descriptive",
            "fundamental": "Fundamental",
            "technical": "Technical",
            "news": "News",
            "etf": "ETF",
            "all": "All",
            "exchange": "Exchange",
            "index": "Index",
            "sector": "Sector",
            "industry": "Industry",
            "country": "Country",
            "market_cap": "Market Cap",
            "dividend_yield": "Dividend Yield",
            "short_float": "Short Float",
            "analyst_recom": "Analyst Recom",
            "option_short": "Option/Short",
            "earnings_date": "Earnings Date",
            "average_volume": "Average Volume",
            "relative_volume": "Relative Volume",
            "current_volume": "Current Volume",
            "trades": "Trades",
            "price": "Price",
            "target_price": "Target Price",
            "ipo_date": "IPO Date",
            "shares_outstanding": "Shares Outstanding",
            "float": "Float"
        }
    }
    return texts[language].get(key, key)

st.subheader(t('subheader'))

# Выбор типа актива
asset_types = ['Stocks', 'Cryptocurrency', 'Bonds', 'Metals', 'Currency'] if language == "English" else ['Акции', 'Криптовалюта', 'Облигации', 'Металлы', 'Валюта']
asset_type = st.selectbox(t('asset_type'), asset_types)

# Фильтры в sidebar с expander
with st.sidebar:
    st.header(t('filters_header'))
    
    with st.expander(t('descriptive')):
        exchange = st.selectbox(t('exchange'), ['Any', 'NASDAQ', 'NYSE', 'AMEX', 'OTC', 'TSX'])
        index = st.selectbox(t('index'), ['Any', 'S&P 500', 'Dow Jones', 'NASDAQ 100'])
        sector = st.selectbox(t('sector'), ['Any', 'Technology', 'Healthcare', 'Financials', 'Consumer Cyclical', 'Energy', 'Industrials', 'Consumer Defensive', 'Communication Services', 'Basic Materials', 'Utilities', 'Real Estate'])
        industry = st.selectbox(t('industry'), ['Any', 'Software - Infrastructure', 'Semiconductors', 'Banks - Diversified', 'Internet Retail', 'Drug Manufacturers - General', 'Oil & Gas Integrated', 'Asset Management', 'Beverages - Non-Alcoholic', 'Aerospace & Defense', 'Information Technology Services'])
        country = st.selectbox(t('country'), ['Any', 'USA', 'China', 'Canada', 'UK', 'Germany', 'India', 'Japan', 'France', 'Australia', 'Brazil'])

    with st.expander(t('fundamental')):
        market_cap = st.selectbox(t('market_cap'), ['Any', 'Mega (>200B)', 'Large (10B-200B)', 'Mid (2B-10B)', 'Small (300M-2B)', 'Micro (50M-300M)', 'Nano (<50M)'])
        dividend_yield = st.selectbox(t('dividend_yield'), ['Any', 'None (0%)', 'Low (<2%)', 'Medium (2-4%)', 'High (4-6%)', 'Very High (>6%)'])
        short_float = st.selectbox(t('short_float'), ['Any', 'Low (<5%)', 'Medium (5-10%)', 'High (>10%)'])
        analyst_recom = st.selectbox(t('analyst_recom'), ['Any', 'Strong Buy (1)', 'Buy (2)', 'Hold (3)', 'Sell (4)', 'Strong Sell (5)'])
        option_short = st.selectbox(t('option_short'), ['Any', 'Optionable', 'Shortable'])

    with st.expander(t('technical')):
        earnings_date = st.selectbox(t('earnings_date'), ['Any', 'Today', 'Tomorrow', 'This Week', 'Next Week', 'This Month', 'Next Month'])
        average_volume = st.selectbox(t('average_volume'), ['Any', 'Low (<100K)', 'Medium (100K-500K)', 'High (500K-1M)', 'Very High (>1M)'])
        relative_volume = st.selectbox(t('relative_volume'), ['Any', 'Low (<0.5)', 'Normal (0.5-1.5)', 'High (>1.5)'])
        current_volume = st.selectbox(t('current_volume'), ['Any', 'Low (<100K)', 'Medium (100K-500K)', 'High (500K-1M)', 'Very High (>1M)'])
        trades = st.selectbox(t('trades'), ['Any', 'Low (<1000)', 'Medium (1000-5000)', 'High (>5000)'])

    with st.expander(t('news')):
        pass  # Пустой, как в Finviz (добавьте позже)

    with st.expander(t('etf')):
        pass  # Пустой

    with st.expander(t('all')):
        price = st.selectbox(t('price'), ['Any', 'Under $5', 'Under $10', 'Under $20', 'Under $50', 'Over $50', 'Over $100'])
        target_price = st.selectbox(t('target_price'), ['Any', 'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'])
        ipo_date = st.selectbox(t('ipo_date'), ['Any', 'This Year', 'Last Year', 'This Month', 'Last Month'])
        shares_outstanding = st.selectbox(t('shares_outstanding'), ['Any', 'Under 50M', 'Under 100M', 'Under 500M', 'Over 500M'])
        float_ = st.selectbox(t('float'), ['Any', 'Low (<10M)', 'Medium (10M-50M)', 'High (>50M)'])

if st.button(t('search_button')):
    results = []

    api_key = 'MS2HKDM5JROIZSKQ'

    if asset_type in ['Stocks', 'Акции']:
        # Полный список акций от Alpha Vantage
        search_url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'
        response = requests.get(search_url)
        if response.status_code == 200:
            csv_data = io.StringIO(response.text)
            df = pd.read_csv(csv_data)
            symbols = df['symbol'].tolist()[:100]  # Ограничим на 100 для теста
        else:
            symbols = []
            st.error("Error fetching stock list.")
        for symbol in symbols:
            time.sleep(12)  # Пауза для лимита 5/мин
            url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'MarketCapitalization' in data and data['MarketCapitalization']:
                    market_cap = float(data.get('MarketCapitalization', 0)) / 1e9
                    if min_market_cap <= market_cap and (max_market_cap is None or market_cap <= max_market_cap):
                        ps = float(data.get('PriceToSalesRatioTTM', float('inf')))
                        pb = float(data.get('PriceToBookRatio', float('inf')))
                        roe = float(data.get('ReturnOnEquityTTM', 0)) * 100
                        margin = float(data.get('OperatingMarginTTM', 0)) * 100
                        peg = float(data.get('PEGRatio', float('inf')))
                        div_yield = float(data.get('DividendYield', 0)) * 100
                        short_float = float(data.get('ShortPercentOfFloat', float('inf')))
                        avg_volume = int(data.get('AverageVolume', 0))
                        rel_volume = float(data.get('RelativeVolume', 1.0))
                        current_volume = int(data.get('CurrentVolume', 0))
                        price = float(data.get('Price', 0))
                        if (max_ps is None or ps < max_ps) and (max_pb is None or pb < max_pb) and roe > min_roe and margin > min_margin and (max_peg is None or peg < max_peg) and div_yield > min_div_yield and (max_short_float is None or short_float < max_short_float) and avg_volume > min_avg_volume and rel_volume > min_rel_volume and current_volume > min_current_volume and min_price <= price and (max_price is None or price <= max_price):
                            results.append({
                                'Asset' if language == "English" else 'Актив': symbol,
                                'Market Cap ($B)' if language == "English" else 'Капитализация ($B)': market_cap,
                                'P/S': ps,
                                'P/B': pb,
                                'ROE (%)': roe,
                                'Margin (%)' if language == "English" else 'Маржа (%)': margin,
                                'PEG': peg,
                                'Dividend Yield (%)': div_yield,
                                'Short Float (%)': short_float,
                                'Avg Volume': avg_volume,
                                'Rel Volume': rel_volume,
                                'Current Volume': current_volume,
                                'Price': price,
                                'Signal' if language == "English" else 'Сигнал': 'Undervalued (Buy)' if ps < 2 else 'Overvalued (Sell)' if language == "English" else 'Недооценён (покупка)' if ps < 2 else 'Переоценён (продажа)'
                            })

    elif asset_type in ['Cryptocurrency', 'Криптовалюта']:
        # Полный список от CoinGecko
        all_data = []
        for page in range(1, 21):
            url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={page}'
            data = requests.get(url).json()
            all_data.extend(data)
        for coin in all_data:
            market_cap = coin.get('market_cap', 0) / 1e9
            if min_market_cap <= market_cap and (max_market_cap is None or market_cap <= max_market_cap):
                change_24h = coin.get('price_change_percentage_24h') or 0
                volume_24h = coin.get('total_volume', 0)
                liquidity = (coin.get('high_24h', 0) - coin.get('low_24h', 0)) or 0
                fdv = (coin.get('fully_diluted_valuation', 0) / 1e9) or 0
                price = coin.get('current_price', 0)
                if volume_24h > min_volume_24h and liquidity > min_liquidity and fdv > min_fdv and (min_change_24h is None or change_24h >= min_change_24h) and (max_change_24h is None or change_24h <= max_change_24h) and min_price <= price and (max_price is None or price <= max_price):
                    results.append({
                        'Asset' if language == "English" else 'Актив': coin['symbol'].upper(),
                        'Market Cap ($B)' if language == "English" else 'Капитализация ($B)': market_cap,
                        '24h Change (%)': change_24h,
                        '24h Volume': volume_24h,
                        'Liquidity': liquidity,
                        'FDV ($B)': fdv,
                        'Price': price,
                        'Signal' if language == "English" else 'Сигнал': 'Undervalued (Buy)' if change_24h < 0 else 'Overvalued (Sell)' if language == "English" else 'Недооценён (покупка)' if change_24h < 0 else 'Переоценён (продажа)'
                    })

    # Аналогично для других типов (расширьте как нужно)

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.write(t('no_results'))
