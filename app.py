import streamlit as st
import requests
import pandas as pd
import time  # Для пауз в API

# Дизайн: Добавляем CSS для красивого вида
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
    .stSelectbox {
        background-color: #ffffff;
    }
    h1 {
        color: #007bff;
        text-align: center;
    }
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title('OmniScreener')
st.subheader('Универсальный скринер для акций, крипты, облигаций, металлов и валюты')

# Выбор типа актива
asset_type = st.selectbox('Выберите тип актива', ['Акции', 'Криптовалюта', 'Облигации', 'Металлы', 'Валюта'])

# Расширенные фильтры (как в Finviz и DexScreener)
with st.sidebar:
    st.header('Фильтры (как в Finviz/DexScreener)')
    exchange = st.text_input('Exchange (e.g., NASDAQ)')
    index = st.text_input('Index (e.g., S&P 500)')
    sector = st.text_input('Sector (e.g., Technology)')
    industry = st.text_input('Industry (e.g., Software)')
    country = st.text_input('Country (e.g., USA)')
    min_market_cap = st.number_input('Min Market Cap (B$)', value=0.0)
    max_market_cap = st.number_input('Max Market Cap (B$)', value=float('inf'))
    min_div_yield = st.number_input('Min Dividend Yield (%)', value=0.0)
    max_short_float = st.number_input('Max Short Float (%)', value=float('inf'))
    analyst_recom = st.number_input('Analyst Recom (1-5)', value=0.0)
    option_short = st.checkbox('Option/Short Available')
    earnings_date = st.text_input('Earnings Date (YYYY-MM-DD)')
    min_avg_volume = st.number_input('Min Average Volume', value=0)
    min_rel_volume = st.number_input('Min Relative Volume', value=0.0)
    min_current_volume = st.number_input('Min Current Volume', value=0)
    min_trades = st.number_input('Min Trades', value=0)
    min_price = st.number_input('Min Price ($)', value=0.0)
    max_price = st.number_input('Max Price ($)', value=float('inf'))
    target_price = st.number_input('Target Price ($)', value=0.0)
    ipo_date = st.text_input('IPO Date (YYYY-MM-DD)')
    min_shares_out = st.number_input('Min Shares Outstanding', value=0)
    min_float = st.number_input('Min Float', value=0)
    min_volume_24h = st.number_input('Min 24h Volume (для крипты)', value=0.0)  # DexScreener
    min_txns_24h = st.number_input('Min 24h Txns (для крипты)', value=0)
    min_liquidity = st.number_input('Min Liquidity (для крипты)', value=0.0)
    min_fdv = st.number_input('Min FDV (для крипты)', value=0.0)
    min_change_24h = st.number_input('Min 24h Change (%)', value=float('-inf'))
    max_change_24h = st.number_input('Max 24h Change (%)', value=float('inf'))
    max_ps = st.number_input('Max P/S', value=float('inf'))
    max_pb = st.number_input('Max P/B', value=float('inf'))
    min_roe = st.number_input('Min ROE (%)', value=float('-inf'))
    min_margin = st.number_input('Min Operating Margin (%)', value=float('-inf'))
    max_peg = st.number_input('Max PEG', value=float('inf'))

if st.button('Поиск активов'):
    results = []

    if asset_type == 'Акции':
        # Полный динамический список акций (используем Alpha Vantage SEARCH для всех; лимит, так что пауза)
        api_key = 'MS2HKDM5JROIZSKQ'
        search_url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}'
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.text.splitlines()
            symbols = [line.split(',')[0] for line in data[1:]]  # Все тикеры из listing (10k+)
        else:
            symbols = []  # Fallback
        for symbol in symbols[:100]:  # Ограничим на 100 для теста, чтобы избежать лимита; удалите для полного
            time.sleep(12)  # Пауза 12 сек для 5 запросов/мин
            url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'MarketCapitalization' in data:
                    market_cap = float(data.get('MarketCapitalization', 0)) / 1e9
                    if min_market_cap <= market_cap <= max_market_cap:
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
                        if (ps < max_ps and pb < max_pb and roe > min_roe and margin > min_margin and peg < max_peg and div_yield > min_div_yield and short_float < max_short_float and avg_volume > min_avg_volume and rel_volume > min_rel_volume and current_volume > min_current_volume and min_price <= price <= max_price):
                            results.append({
                                'Актив': symbol,
                                'Капитализация ($B)': market_cap,
                                'P/S': ps,
                                'P/B': pb,
                                'ROE (%)': roe,
                                'Маржа (%)': margin,
                                'PEG': peg,
                                'Dividend Yield (%)': div_yield,
                                'Short Float (%)': short_float,
                                'Avg Volume': avg_volume,
                                'Rel Volume': rel_volume,
                                'Current Volume': current_volume,
                                'Price': price,
                                'Сигнал': 'Недооценён (покупка)' if ps < 2 else 'Переоценён (продажа)'
                            })

    elif asset_type == 'Криптовалюта':
        # Полный динамический список от CoinGecko (5000+)
        all_data = []
        for page in range(1, 21):  # До 5000, как на Bitget/DexScreener
            url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={page}'
            data = requests.get(url).json()
            all_data.extend(data)
        for coin in all_data:
            market_cap = coin.get('market_cap', 0) / 1e9
            if min_market_cap <= market_cap <= max_market_cap:
                change_24h = coin.get('price_change_percentage_24h', 0)
                volume_24h = coin.get('total_volume', 0)
                liquidity = coin.get('high_24h', 0) - coin.get('low_24h', 0)  # Упрощённо
                fdv = coin.get('fully_diluted_valuation', 0) / 1e9
                if volume_24h > min_volume_24h and liquidity > min_liquidity and fdv > min_fdv and min_change_24h <= change_24h <= max_change_24h:
                    results.append({
                        'Актив': coin['symbol'].upper(),
                        'Капитализация ($B)': market_cap,
                        '24h Change (%)': change_24h,
                        '24h Volume': volume_24h,
                        'Liquidity': liquidity,
                        'FDV ($B)': fdv,
                        'Сигнал': 'Недооценён (покупка)' if change_24h < 0 else 'Переоценён (продажа)'
                    })

    # Аналогично для других (расширьте как в предыдущем коде, с паузами)

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.write('Нет активов по критериям.')
