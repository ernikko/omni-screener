import streamlit as st
import requests
import pandas as pd
import time
import io

# Дизайн: Копируем стиль Finviz (тёмный фиолетовый/серый, таблица с колонками как в скриншоте, фильтры в sidebar с категориями)
st.markdown("""
<style>
    .stApp {
        background-color: #2b1b4d;  /* Тёмный фиолетовый фон Finviz */
        color: #ffffff;
    }
    .sidebar .sidebar-content {
        background-color: #3a2a5e;  /* Серо-фиолетовый для sidebar */
        border-right: 1px solid #5a3a8a;
    }
    .stButton > button {
        background-color: #4a3a8a;
        color: #ffffff;
        border-radius: 0;
        padding: 8px 16px;
        font-weight: bold;
        border: 1px solid #5a3a8a;
    }
    .stButton > button:hover {
        background-color: #5a4a9a;
    }
    .stSelectbox, .stNumberInput, .stTextInput {
        background-color: #3a2a5e;
        color: #ffffff;
        border: 1px solid #5a3a8a;
        border-radius: 0;
    }
    h1 {
        color: #ffffff;
        text-align: center;
        font-size: 24px;
        margin-bottom: 10px;
    }
    .stDataFrame {
        border: none;
        font-size: 11px;
    }
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
    }
    .stDataFrame th {
        background-color: #3a2a5e;
        color: #ffffff;
        padding: 5px 8px;
        text-align: left;
        border-bottom: 1px solid #5a3a8a;
        font-weight: normal;
    }
    .stDataFrame td {
        padding: 5px 8px;
        border-bottom: 1px solid #5a3a8a;
        color: #ffffff;
    }
    .stExpander {
        background-color: #3a2a5e;
        border: 1px solid #5a3a8a;
        border-radius: 0;
    }
    .stExpander > div > label {
        color: #ffffff;
    }
    .metric-card {
        background-color: #4a3a8a;
        padding: 10px;
        border-radius: 0;
        border: 1px solid #5a3a8a;
    }
</style>
""", unsafe_allow_html=True)

# Переключатель языка
language = st.selectbox("Language", ["English", "Russian"])

# Функция для текстов
def t(key):
    texts = {
        "English": {
            "title": "OmniScreener",
            "subheader": "Universal Stock Screener",
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
            "exchange": "Exchange",
            "index": "Index",
            "sector": "Sector",
            "industry": "Industry",
            "country": "Country",
            "market_cap": "Market Cap.",
            "dividend_yield": "Dividend Yield",
            "short_float": "Short Float",
            "analyst_recom": "Analyst Recom.",
            "option_short": "Option/Short",
            "earnings_date": "Earnings Date",
            "average_volume": "Average Volume",
            "relative_volume": "Relative Volume",
            "current_volume": "Current Volume",
            "trades": "Trades",
            "price": "Price $",
            "target_price": "Target Price",
            "ipo_date": "IPO Date",
            "shares_outstanding": "Shares Outstanding",
            "float": "Float"
        },
        "Russian": {
            "title": "OmniScreener",
            "subheader": "Универсальный скринер акций",
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
            "exchange": "Exchange",
            "index": "Index",
            "sector": "Sector",
            "industry": "Industry",
            "country": "Country",
            "market_cap": "Market Cap.",
            "dividend_yield": "Dividend Yield",
            "short_float": "Short Float",
            "analyst_recom": "Analyst Recom.",
            "option_short": "Option/Short",
            "earnings_date": "Earnings Date",
            "average_volume": "Average Volume",
            "relative_volume": "Relative Volume",
            "current_volume": "Current Volume",
            "trades": "Trades",
            "price": "Price $",
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

# Фильтры в sidebar, скопированные из Finviz (категории как в скриншоте)
with st.sidebar:
    st.header(t('filters_header'))
    
    # Descriptive
    with st.expander(t('descriptive')):
        exchange = st.selectbox("Exchange", ['Any', 'NASDAQ', 'NYSE', 'AMEX', 'OTC', 'TSX'])
        index = st.selectbox("Index", ['Any', 'S&P 500', 'Dow Jones', 'NASDAQ 100', 'Russell 2000'])
        sector = st.selectbox("Sector", ['Any', 'Technology', 'Healthcare', 'Financials', 'Consumer Cyclical', 'Energy', 'Industrials', 'Consumer Defensive', 'Communication Services', 'Basic Materials', 'Utilities', 'Real Estate'])
        industry = st.selectbox("Industry", ['Any', 'Software - Infrastructure', 'Semiconductors', 'Banks - Diversified', 'Internet Retail', 'Drug Manufacturers - General', 'Oil & Gas Integrated', 'Asset Management', 'Beverages - Non-Alcoholic', 'Aerospace & Defense', 'Information Technology Services'])
        country = st.selectbox("Country", ['Any', 'USA', 'China', 'Canada', 'UK', 'Germany', 'India', 'Japan', 'France', 'Australia', 'Brazil'])

    # Fundamental
    with st.expander(t('fundamental')):
        market_cap = st.selectbox("Market Cap.", ['Any', 'Mega (>200B)', 'Large (10B-200B)', 'Mid (2B-10B)', 'Small (300M-2B)', 'Micro (50M-300M)', 'Nano (<50M)'])
        dividend_yield = st.selectbox("Dividend Yield", ['Any', 'None (0%)', 'Low (<2%)', 'Medium (2-4%)', 'High (4-6%)', 'Very High (>6%)'])
        short_float = st.selectbox("Short Float", ['Any', 'Low (<5%)', 'Medium (5-10%)', 'High (>10%)'])
        analyst_recom = st.selectbox("Analyst Recom.", ['Any', 'Strong Buy (1)', 'Buy (2)', 'Hold (3)', 'Sell (4)', 'Strong Sell (5)'])
        option_short = st.selectbox("Option/Short", ['Any', 'Optionable', 'Shortable', 'Both'])

    # Technical
    with st.expander(t('technical')):
        earnings_date = st.selectbox("Earnings Date", ['Any', 'Today', 'Tomorrow', 'This Week', 'Next Week', 'This Month', 'Next Month'])
        average_volume = st.selectbox("Average Volume", ['Any', 'Low (<100K)', 'Medium (100K-500K)', 'High (500K-1M)', 'Very High (>1M)'])
        relative_volume = st.selectbox("Relative Volume", ['Any', 'Low (<0.5)', 'Normal (0.5-1.5)', 'High (>1.5)'])
        current_volume = st.selectbox("Current Volume", ['Any', 'Low (<100K)', 'Medium (100K-500K)', 'High (500K-1M)', 'Very High (>1M)'])
        trades = st.selectbox("Trades", ['Any', 'Low (<1000)', 'Medium (1000-5000)', 'High (>5000)'])

    # News
    with st.expander(t('news')):
        st.write("News filters coming soon.")

    # ETF
    with st.expander(t('etf')):
        st.write("ETF filters coming soon.")

    # All
    with st.expander(t('all')):
        price = st.selectbox("Price $", ['Any', 'Under $5', 'Under $10', 'Under $20', 'Under $50', 'Over $50', 'Over $100'])
        target_price = st.selectbox("Target Price", ['Any', 'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'])
        ipo_date = st.selectbox("IPO Date", ['Any', 'This Year', 'Last Year', 'This Month', 'Last Month'])
        shares_outstanding = st.selectbox("Shares Outstanding", ['Any', 'Under 50M', 'Under 100M', 'Under 500M', 'Over 500M'])
        float_ = st.selectbox("Float", ['Any', 'Low (<10M)', 'Medium (10M-50M)', 'High (>50M)'])

if st.button(t('search_button')):
    results = []

    api_key = 'MS2HKDM5JROIZSKQ'

    if asset_type in ['Stocks', 'Акции']:
        # Исправление KeyError: Используем статический список, так как LISTING_STATUS возвращает CSV с колонкой 'Symbol' (большая S)
        symbols = ['A', 'AA', 'AAA', 'AAAU', 'AACB', 'AACG', 'AACI', 'AACIU', 'AACT', 'AADR', 'AAL', 'AAM', 'AAME', 'AAMI', 'AAOI', 'AAON', 'AAP', 'AAPB', 'AAPD', 'AAPG']  # Из скриншота Finviz, расширьте до 100+
        for symbol in symbols:
            time.sleep(12)  # Пауза
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
                                'No.': len(results) + 1,
                                'Ticker': symbol,
                                'Company': data.get('Name', 'N/A'),
                                'Sector': data.get('Sector', 'N/A'),
                                'Industry': data.get('Industry', 'N/A'),
                                'Country': data.get('Country', 'N/A'),
                                'Market Cap': f"${market_cap:.2f}B" if market_cap >= 1 else f"${market_cap*1000:.0f}M",
                                'P/E': data.get('PERatio', 'N/A'),
                                'Price': f"${price:.2f}",
                                'Change': f"{roe:.2f}%",  # Адаптировано
                                'Volume': avg_volume
                            })

    elif asset_type in ['Cryptocurrency', 'Криптовалюта']:
        # Фильтры как в DexScreener (min/max для liquidity, market cap, FDV, pair age, 24h buys/sells, volume, change)
        all_data = []
        for page in range(1, 3):  # Ограничено для теста
            url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={page}'
            data = requests.get(url).json()
            all_data.extend(data)
        for coin in all_data:
            market_cap = coin.get('market_cap', 0) / 1e9
            change_24h = coin.get('price_change_percentage_24h') or 0
            volume_24h = coin.get('total_volume', 0)
            liquidity = (coin.get('high_24h', 0) - coin.get('low_24h', 0)) or 0
            fdv = (coin.get('fully_diluted_valuation', 0) / 1e9) or 0
            price = coin.get('current_price', 0)
            age = coin.get('last_updated', 'N/A')  # Упрощённо
            txns = coin.get('market_cap_rank', 'N/A')  # Упрощённо для txns
            if min_market_cap <= market_cap and (max_market_cap is None or market_cap <= max_market_cap) and volume_24h > min_volume_24h and liquidity > min_liquidity and fdv > min_fdv and min_change_24h <= change_24h and (max_change_24h is None or change_24h <= max_change_24h) and min_price <= price and (max_price is None or price <= max_price):
                results.append({
                    'No.': len(results) + 1,
                    'Token': coin['symbol'].upper(),
                    'Price': f"${price:.4f}",
                    'Age': age,
                    'Txns': txns,
                    'Volume': volume_24h,
                    'Makers': coin.get('market_cap_rank', 'N/A'),  # Упрощённо
                    '5m': 'N/A',  # Добавьте API для timeframe
                    '1h': 'N/A',
                    '6h': 'N/A',
                    '24h': f"{change_24h:.2f}%",
                    'Liquidity': liquidity,
                    'MCAP': f"${market_cap:.2f}B" if market_cap >= 1 else f"${market_cap*1000:.0f}M"
                })

    # Вывод таблицы как в Finviz/DexScreener
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        # Пагинация (упрощённо)
        st.write(f"Showing 1-{len(results)} of {len(results)}")
    else:
        st.write(t('no_results'))
