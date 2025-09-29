import streamlit as st
import requests
import pandas as pd
import time  # Для пауз в API
import io  # Для парсинга CSV

# Дизайн: Улучшенный CSS для красивого вида
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6;
        color: #333333;
    }
    .sidebar .sidebar-content {
        background-color: #ffffff;
        border-right: 1px solid #ddd;
    }
    .stButton > button {
        background-color: #007bff;
        color: white;
        border-radius: 5px;
    }
    .stSelectbox, .stNumberInput, .stTextInput, .stCheckbox {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    h1 {
        color: #007bff;
        text-align: center;
    }
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 5px;
        overflow: auto;
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
            "exchange": "Exchange (e.g., NASDAQ)",
            "index": "Index (e.g., S&P 500)",
            "sector": "Sector (e.g., Technology)",
            "industry": "Industry (e.g., Software)",
            "country": "Country (e.g., USA)",
            "min_market_cap": "Min Market Cap (B$)",
            "max_market_cap": "Max Market Cap (B$)",
            "min_div_yield": "Min Dividend Yield (%)",
            "max_short_float": "Max Short Float (%)",
            "analyst_recom": "Analyst Recom (1-5)",
            "option_short": "Option/Short Available",
            "earnings_date": "Earnings Date (YYYY-MM-DD)",
            "min_avg_volume": "Min Average Volume",
            "min_rel_volume": "Min Relative Volume",
            "min_current_volume": "Min Current Volume",
            "min_trades": "Min Trades",
            "min_price": "Min Price ($)",
            "max_price": "Max Price ($)",
            "target_price": "Target Price ($)",
            "ipo_date": "IPO Date (YYYY-MM-DD)",
            "min_shares_out": "Min Shares Outstanding",
            "min_float": "Min Float",
            "min_volume_24h": "Min 24h Volume (for crypto)",
            "min_txns_24h": "Min 24h Txns (for crypto)",
            "min_liquidity": "Min Liquidity (for crypto)",
            "min_fdv": "Min FDV (for crypto)",
            "min_change_24h": "Min 24h Change (%)",
            "max_change_24h": "Max 24h Change (%)",
            "max_ps": "Max P/S",
            "max_pb": "Max P/B",
            "min_roe": "Min ROE (%)",
            "min_margin": "Min Operating Margin (%)",
            "max_peg": "Max PEG"
        },
        "Russian": {
            "title": "OmniScreener",
            "subheader": "Универсальный скринер для акций, крипты, облигаций, металлов и валюты",
            "asset_type": "Выберите тип актива",
            "search_button": "Поиск активов",
            "no_results": "Нет активов по критериям.",
            "filters_header": "Фильтры",
            "exchange": "Exchange (например, NASDAQ)",
            "index": "Index (например, S&P 500)",
            "sector": "Sector (например, Technology)",
            "industry": "Industry (например, Software)",
            "country": "Country (например, USA)",
            "min_market_cap": "Минимальная капитализация (млрд $)",
            "max_market_cap": "Максимальная капитализация (млрд $)",
            "min_div_yield": "Минимальная дивидендная доходность (%)",
            "max_short_float": "Максимум Short Float (%)",
            "analyst_recom": "Analyst Recom (1-5)",
            "option_short": "Option/Short доступны",
            "earnings_date": "Earnings Date (YYYY-MM-DD)",
            "min_avg_volume": "Минимальный Average Volume",
            "min_rel_volume": "Минимальный Relative Volume",
            "min_current_volume": "Минимальный Current Volume",
            "min_trades": "Минимальное количество Trades",
            "min_price": "Минимальная цена ($)",
            "max_price": "Максимальная цена ($)",
            "target_price": "Target Price ($)",
            "ipo_date": "IPO Date (YYYY-MM-DD)",
            "min_shares_out": "Минимальное Shares Outstanding",
            "min_float": "Минимальный Float",
            "min_volume_24h": "Минимальный 24h Volume (для крипты)",
            "min_txns_24h": "Минимальный 24h Txns (для крипты)",
            "min_liquidity": "Минимальный Liquidity (для крипты)",
            "min_fdv": "Минимальный FDV (для крипты)",
            "min_change_24h": "Минимальный 24h Change (%)",
            "max_change_24h": "Максимальный 24h Change (%)",
            "max_ps": "Максимум P/S",
            "max_pb": "Максимум P/B",
            "min_roe": "Минимум ROE (%)",
            "min_margin": "Минимум Operating Margin (%)",
            "max_peg": "Максимум PEG"
        }
    }
    return texts[language].get(key, key)

st.subheader(t('subheader'))

# Выбор типа актива
asset_type = st.selectbox(t('asset_type'), ['Акции', 'Криптовалюта', 'Облигации', 'Металлы', 'Валюта'] if language == "Russian" else ['Stocks', 'Cryptocurrency', 'Bonds', 'Metals', 'Currency'])

# Фильтры в sidebar
with st.sidebar:
    st.header(t('filters_header'))
    exchange = st.text_input(t('exchange'))
    index = st.text_input(t('index'))
    sector = st.text_input(t('sector'))
    industry = st.text_input(t('industry'))
    country = st.text_input(t('country'))
    min_market_cap = st.number_input(t('min_market_cap'), value=0.0)
    max_market_cap = st.number_input(t('max_market_cap'), value=None)
    min_div_yield = st.number_input(t('min_div_yield'), value=0.0)
    max_short_float = st.number_input(t('max_short_float'), value=None)
    analyst_recom = st.number_input(t('analyst_recom'), value=0.0)
    option_short = st.checkbox(t('option_short'))
    earnings_date = st.text_input(t('earnings_date'))
    min_avg_volume = st.number_input(t('min_avg_volume'), value=0)
    min_rel_volume = st.number_input(t('min_rel_volume'), value=0.0)
    min_current_volume = st.number_input(t('min_current_volume'), value=0)
    min_trades = st.number_input(t('min_trades'), value=0)
    min_price = st.number_input(t('min_price'), value=0.0)
    max_price = st.number_input(t('max_price'), value=None)
    target_price = st.number_input(t('target_price'), value=0.0)
    ipo_date = st.text_input(t('ipo_date'))
    min_shares_out = st.number_input(t('min_shares_out'), value=0)
    min_float = st.number_input(t('min_float'), value=0)
    min_volume_24h = st.number_input(t('min_volume_24h'), value=0.0)
    min_txns_24h = st.number_input(t('min_txns_24h'), value=0)
    min_liquidity = st.number_input(t('min_liquidity'), value=0.0)
    min_fdv = st.number_input(t('min_fdv'), value=0.0)
    min_change_24h = st.number_input(t('min_change_24h'), value=float('-inf'))
    max_change_24h = st.number_input(t('max_change_24h'), value=None)
    max_ps = st.number_input(t('max_ps'), value=None)
    max_pb = st.number_input(t('max_pb'), value=None)
    min_roe = st.number_input(t('min_roe'), value=float('-inf'))
    min_margin = st.number_input(t('min_margin'), value=float('-inf'))
    max_peg = st.number_input(t('max_peg'), value=None)

if st.button(t('search_button')):
    results = []

    api_key = 'MS2HKDM5JROIZSKQ'

    if asset_type in ['Акции', 'Stocks']:
        # Полный список акций от Alpha Vantage (CSV парсинг)
        search_url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'
        response = requests.get(search_url)
        if response.status_code == 200:
            csv_data = io.StringIO(response.text)
            df = pd.read_csv(csv_data)
            symbols = df['symbol'].tolist()[:100]  # Ограничим на 100 для теста; удалите для полного (но лимит API)
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
                                'Актив' if language == "Russian" else 'Asset': symbol,
                                'Капитализация ($B)' if language == "Russian" else 'Market Cap ($B)': market_cap,
                                'P/S': ps,
                                'P/B': pb,
                                'ROE (%)': roe,
                                'Маржа (%)' if language == "Russian" else 'Margin (%)': margin,
                                'PEG': peg,
                                'Dividend Yield (%)': div_yield,
                                'Short Float (%)': short_float,
                                'Avg Volume': avg_volume,
                                'Rel Volume': rel_volume,
                                'Current Volume': current_volume,
                                'Price': price,
                                'Сигнал' if language == "Russian" else 'Signal': 'Недооценён (покупка)' if ps < 2 else 'Переоценён (продажа)' if language == "Russian" else 'Undervalued (Buy)' if ps < 2 else 'Overvalued (Sell)'
                            })

    elif asset_type in ['Криптовалюта', 'Cryptocurrency']:
        # Полный список от CoinGecko
        all_data = []
        for page in range(1, 21):
            url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={page}'
            data = requests.get(url).json()
            all_data.extend(data)
        for coin in all_data:
            market_cap = coin.get('market_cap', 0) / 1e9
            if min_market_cap <= market_cap and (max_market_cap is None or market_cap <= max_market_cap):
                change_24h = coin.get('price_change_percentage_24h') if coin.get('price_change_percentage_24h') is not None else 0
                volume_24h = coin.get('total_volume', 0)
                liquidity = coin.get('high_24h', 0) - coin.get('low_24h', 0) if coin.get('high_24h') and coin.get('low_24h') else 0
                fdv = coin.get('fully_diluted_valuation', 0) / 1e9 if coin.get('fully_diluted_valuation') else 0
                price = coin.get('current_price', 0)
                if volume_24h > min_volume_24h and min_txns_24h == 0 and liquidity > min_liquidity and fdv > min_fdv and min_change_24h <= change_24h and (max_change_24h is None or change_24h <= max_change_24h) and min_price <= price and (max_price is None or price <= max_price):
                    results.append({
                        'Актив' if language == "Russian" else 'Asset': coin['symbol'].upper(),
                        'Капитализация ($B)' if language == "Russian" else 'Market Cap ($B)': market_cap,
                        '24h Change (%)': change_24h,
                        '24h Volume': volume_24h,
                        'Liquidity': liquidity,
                        'FDV ($B)': fdv,
                        'Price': price,
                        'Сигнал' if language == "Russian" else 'Signal': 'Недооценён (покупка)' if change_24h < 0 else 'Переоценён (продажа)' if language == "Russian" else 'Undervalued (Buy)' if change_24h < 0 else 'Overvalued (Sell)'
                    })

    # Аналогично для других типов (расширьте как нужно)

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.write(t('no_results'))
