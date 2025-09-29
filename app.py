import streamlit as st
import requests
import pandas as pd
import json

st.title('OmniScreener: Аналог Finviz для всех активов')

# Выбор типа актива
asset_type = st.selectbox('Выберите тип актива', ['Акции', 'Криптовалюта', 'Облигации', 'Металлы', 'Валюта'])

# Общие фильтры (адаптированы под активы)
min_market_cap = st.number_input('Минимальная капитализация (млрд $)', value=10.0)
max_ps = st.number_input('Максимум P/S', value=2.0)
max_pb = st.number_input('Максимум P/B', value=4.0)
min_roe = st.number_input('Минимум ROE (%)', value=10.0)
min_margin = st.number_input('Минимум операционная маржа (%)', value=10.0)
max_peg = st.number_input('Максимум PEG', value=2.0)

if st.button('Поиск активов'):
    results = []

    if asset_type == 'Акции':
        # Расширенный статический список (S&P 500 + common NASDAQ/NYSE/AMEX, ~500; добавьте больше из CSV)
        symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK.B', 'JPM', 'V', 'UNH', 'MA', 'HD', 'PG', 'DIS', 'BAC', 'KO', 'WMT', 'MRK', 'PFE', 'CMCSA', 'VZ', 'INTC', 'CSCO', 'CVX', 'XOM', 'T', 'PEP', 'ADBE', 'NFLX', 'ABT', 'CRM', 'AMD', 'TMO', 'LIN', 'ACN', 'TXN', 'MCD', 'IBM', 'ORCL', 'CAT', 'GE', 'HON', 'RTX', 'NKE', 'UPS', 'PM', 'NEE', 'SPGI', 'MDT', 'QCOM', 'GS', 'LOW', 'MS', 'BKNG', 'BLK', 'UNP', 'TJX', 'ETN', 'COP', 'SYK', 'ISRG', 'REGN', 'PLD', 'MMC', 'GILD', 'LRCX', 'ADP', 'AMGN', 'PGR', 'CB', 'MDLZ', 'DE', 'FI', 'KLAC', 'BMY', 'ZTS', 'PANW', 'BSX', 'SBUX', 'NOW', 'INTU', 'MO', 'CME', 'EOG', 'BDX', 'SLB', 'ICE', 'CL', 'DUK', 'SO', 'SHW', 'WM', 'FCX', 'TGT', 'APD', 'ITW', 'HUM', 'EMR', 'PH', 'CSX', 'ECL', 'FDX', 'MAR', 'AON', 'PYPL', 'USB', 'TRI', 'PNC', 'LMT', 'AIG', 'PCAR', 'MMM', 'GM', 'F', 'CARR', 'NSC', 'JCI', 'TRV', 'COF', 'CPRT', 'OXY', 'LHX', 'MCHP', 'STZ', 'WMB', 'AFL', 'ADSK', 'ROST', 'AZO', 'SPG', 'TDG', 'FTNT', 'KMB', 'SRE', 'GIS', 'AJG', 'TEL', 'CCI', 'D', 'AEP', 'KDP', 'TT', 'IDXX', 'EXC', 'HCA', 'NEM', 'PCG', 'KHC', 'CTVA', 'GEV', 'O', 'PayX', 'RSG', 'DLR', 'COR', 'CTAS', 'A', 'IR', 'MNST', 'YUM', 'MPWR', 'VRSK', 'CNC', 'IQV', 'GPN', 'KMI', 'EA', 'MRNA', 'VLO', 'XEL', 'SYY', 'KR', 'ROK', 'PPG', 'HES', 'MSCI', 'DOW', 'FAST', 'VMC', 'WST', 'PWR', 'ANSS', 'MLM', 'FANG', 'LYB', 'HAL', 'EFX', 'DLTR', 'ALGN', 'DFS', 'INVH', 'STE', 'SBAC', 'MTD', 'HIG', 'RMD', 'MTB', 'ALB', 'WEC', 'DVN', 'TROW', 'FLT', 'VLTO', 'FTV', 'GWW', 'WAB', 'IFF', 'HPE', 'ILMN', 'VRSN', 'AWK', 'IRM', 'GRMN', 'BR', 'DOV', 'AXON', 'EBAY', 'LVS', 'NTAP', 'TSCO', 'STT', 'BALL', 'WY', 'ARE', 'HUBB', 'AVY', 'J', 'PPL', 'HOLX', 'LH', 'TSN', 'COO', 'FICO', 'CBOE', 'TYL', 'WAT', 'OMC', 'MKC', 'TDY', 'BRO', 'IEX', 'CMS', 'TER', 'TXT', 'CNP', 'PKG', 'SWKS', 'DG', 'ATO', 'EXPE', 'JBL', 'FSLR', 'LPLA', 'CAG', 'MAS', 'SJM', 'CF', 'MOH', 'JBHT', 'INCY', 'CINF', 'CRL', 'RJF', 'IPG', 'JKHY', 'LW', 'EXPD', 'CHRW', 'SYF', 'NVR', 'PTC', 'TECH', 'LKQ', 'TRMB', 'HII', 'AOS', 'FFIV', 'GEN', 'UHS', 'NDSN', 'HRL', 'PNR', 'SWK', 'ALLE', 'PODD', 'REG', 'ROL', 'ENPH', 'WRB', 'BBWI', 'BXP', 'IP', 'FDS', 'POOL', 'SNA', 'CPAY', 'MAA', 'VTRS', 'KEY', 'BG', 'DPZ', 'PKG', 'NI', 'DRI', 'AKAM', 'LNT', 'EVRG', 'HST', 'NTNX', 'TAP', 'CPT', 'KMX', 'KIM', 'DOC', 'JNPR', 'UDR', 'AMCR', 'GL', 'WPC', 'HUBS', 'QRVO', 'CDAY', 'ACM', 'MOS', 'AIZ', 'CTLT', 'CRUS', 'RL', 'HSY', 'WRK', 'AAL', 'APA', 'ETSY', 'IVZ', 'BIO', 'MHK', 'CPB', 'NCLH', 'PNW', 'HAS', 'FRT', 'RHI', 'HUN', 'TPR', 'NWSA', 'DVA', 'UAA', 'ZION', 'FOX', 'NWS', 'IPGP', 'UA', 'BEN', 'PARA', 'CMA', 'GNRC', 'DXC', 'ALK', 'RLGY', 'LUMN', 'FMC', 'SLGN', 'SEE', 'LEG', 'HBI', 'XRAY', 'WHR', 'CCK', 'NWL', 'KSS', 'AAP', 'LNC', 'NRG', 'AEE', 'WDC', 'AIZ', 'COTY', 'MRO', 'NOV', 'PRGO', 'HP', 'PENN', 'PVH', 'SEDG', 'CAR', 'WOLF', 'JWN', 'HII', 'MOS', 'VFC', 'BWA', 'GAP', 'NCLH', 'UA', 'UAA', 'ALB', 'GNRC', 'DXC', 'ALK', 'LNC', 'LUMN', 'MHK', 'IVZ', 'CMA', 'ZION', 'PARA', 'NWS', 'NWSA', 'FOX', 'DISH', 'IPGP', 'BEN'  # Полный S&P + NASDAQ/AMEX, ~500; для полного добавьте CSV load
        ]
        api_key = 'MS2HKDM5JROIZSKQ'
        for symbol in symbols:
            url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'MarketCapitalization' in data:
                    market_cap = float(data.get('MarketCapitalization', 0)) / 1e9
                    ps = float(data.get('PriceToSalesRatioTTM', float('inf')))
                    pb = float(data.get('PriceToBookRatio', float('inf')))
                    roe = float(data.get('ReturnOnEquityTTM', 0)) * 100
                    margin = float(data.get('OperatingMarginTTM', 0)) * 100
                    peg = float(data.get('PEGRatio', float('inf')))
                    if market_cap > min_market_cap and ps < max_ps and pb < max_pb and roe > min_roe and margin > min_margin and peg < max_peg:
                        results.append({
                            'Актив': symbol,
                            'Капитализация ($B)': market_cap,
                            'P/S': ps,
                            'P/B': pb,
                            'ROE (%)': roe,
                            'Маржа (%)': margin,
                            'PEG': peg,
                            'Сигнал': 'Недооценён (покупка)' if ps < 2 else 'Переоценён (продажа)'
                        })

    elif asset_type == 'Криптовалюта':
        # Полный динамический список от CoinGecko (loop по pages для тысяч монет, как на DexScreener/Bitget; max 5000+)
        all_data = []
        for page in range(1, 21):  # 20 pages по 250 = 5000 монет; увеличьте для больше
            url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={page}'
            data = requests.get(url).json()
            all_data.extend(data)
        for coin in all_data:
            market_cap = coin.get('market_cap', 0) / 1e9
            ps_analog = coin.get('price_change_percentage_24h', float('inf'))
            if market_cap > min_market_cap and ps_analog < max_ps:
                results.append({
                    'Актив': coin['symbol'].upper(),
                    'Капитализация ($B)': market_cap,
                    'Изменение 24h (%)': coin.get('price_change_percentage_24h', 'N/A'),
                    'Сигнал': 'Недооценён (покупка)' if coin.get('price_change_percentage_24h', 0) < 0 else 'Переоценён (продажа)'
                })

    elif asset_type == 'Облигации':
        # Расширенный список облигаций ETF (~100 от ETFDB/Yahoo, для всех облигаций — тысячи, но API лимит; добавьте search)
        symbols = ['VCIT', 'TLT', 'VGIT', 'GOVT', 'IEF', 'SCHI', 'BIV', 'BND', 'AGG', 'BOND', 'LQD', 'HYG', 'JNK', 'TIP', 'SHY', 'IEI', 'MBB', 'MUB', 'TFI', 'VTEB', 'SPIB', 'IGSB', 'BKLN', 'FLRN', 'FLOT', 'EMB', 'VWOB', 'PCY', 'PFF', 'PFXF', 'PFFD', 'USIG', 'IGIB', 'USHY', 'SHYG', 'SJNK', 'HYLB', 'BSV', 'ISTB', 'ICSH', 'NEAR', 'GSY', 'JPST', 'JMST', 'MINT', 'FALN', 'ANGL', 'QLTA', 'QUAL', 'CRED', 'IG', 'SKOR', 'SLQD', 'ALQD', 'FLCB', 'FLCO', 'LKOR', 'JIGB', 'JCPB', 'JPIE', 'JPIE', 'BBSA', 'JPMB', 'BBMC', 'BBSC', 'TECB', 'FDIV', 'NUSA', 'NUAG', 'NUBD', 'NURE', 'NUMG', 'NUMV', 'NULG', 'NULV', 'ESGU', 'ESGD', 'ESGE', 'LDEM', 'ESML', 'SUSL', 'SUSA', 'SUSB', 'SUSC', 'XT', 'DMXF', 'EMXF', 'CRBN', 'KRBN', 'GRNB', 'KGRN', 'ACSI', 'SHE', 'NZAC', 'NZUS', 'NZRO']  # Топ ~100; для тысяч — добавьте API search
        api_key = 'MS2HKDM5JROIZSKQ'
        for symbol in symbols:
            url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'MarketCapitalization' in data:
                    market_cap = float(data.get('MarketCapitalization', 0)) / 1e9
                    yield_rate = float(data.get('DividendYield', 0)) * 100  # Адаптировано для облигаций
                    if market_cap > min_market_cap and yield_rate > min_margin:
                        results.append({
                            'Актив': symbol,
                            'Капитализация ($B)': market_cap,
                            'Yield (%)': yield_rate,
                            'Сигнал': 'Недооценён (покупка)' if yield_rate > 4 else 'Переоценён (продажа)'
                        })

    elif asset_type == 'Металлы':
        # Расширенный список фьючерсов металлов (все основные + вариации, ~50; для тысяч — добавьте commodity API)
        symbols = ['GC=F', 'SI=F', 'PL=F', 'PA=F', 'HG=F', 'ALI=F', 'LA=F', 'NI=F', 'SN=F', 'ZS=F', 'AL=F', 'CU=F', 'ZN=F', 'PB=F', 'AU=F', 'RH=F', 'RU=F', 'IR=F', 'SB=F', 'CC=F', 'KC=F', 'OJ=F', 'CT=F', 'LB=F', 'LBS=F', 'LBR=F', 'HO=F', 'RB=F', 'CL=F', 'NG=F', 'BZ=F', 'ZM=F', 'ZL=F', 'ZW=F', 'ZR=F', 'ZC=F', 'ZS=F', 'KE=F', 'YO=F', 'RR=F', 'GF=F', 'HE=F', 'LE=F', 'LBS=F', 'LBR=F']  # Полный commodities metals
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            price = info.get('regularMarketPrice', 0)
            change = info.get('regularMarketChangePercent', 0)
            market_cap_analog = info.get('marketCap', 0) / 1e9 if 'marketCap' in info else float('inf')  # Адаптировано
            if market_cap_analog > min_market_cap and change < 0:
                results.append({
                    'Актив': symbol,
                    'Цена': price,
                    'Изменение (%)': change,
                    'Сигнал': 'Недооценён (покупка)'
                })

    elif asset_type == 'Валюта':
        # Расширенный список forex пар (все основные + экзотика, ~50; для сотен — добавьте loop по API)
        symbols = ['EURUSD=X', 'USDJPY=X', 'GBPUSD=X', 'AUDUSD=X', 'USDCAD=X', 'USDCHF=X', 'NZDUSD=X', 'EURJPY=X', 'GBPJPY=X', 'EURGBP=X', 'AUDJPY=X', 'USDRUB=X', 'USDINR=X', 'USDBRL=X', 'USDMXN=X', 'USDZAR=X', 'USDCNY=X', 'USDHKD=X', 'USDSGD=X', 'USDTRY=X', 'USDKRW=X', 'USDTHB=X', 'USDSEK=X', 'USDNOK=X', 'USDDKK=X', 'USDPLN=X', 'USDCZK=X', 'USDHUF=X', 'USDILS=X', 'USDPHP=X', 'USDMYR=X', 'USDTWD=X', 'USDIDR=X', 'USDPKR=X', 'USDBDT=X', 'USDSAR=X', 'USDAED=X', 'USDKWD=X', 'USDBHD=X', 'USDOMR=X', 'USDQAR=X', 'USDCOP=X', 'USDCLP=X', 'USDARS=X', 'USDPEN=X', 'USDUYU=X', 'USDBOB=X', 'USDCRC=X', 'USDPYG=X']
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            price = info.get('regularMarketPrice', 0)
            change = info.get('regularMarketChangePercent', 0)
            if change < 0:
                results.append({
                    'Актив': symbol,
                    'Цена': price,
                    'Изменение (%)': change,
                    'Сигнал': 'Недооценён (покупка)'
                })

    # Вывод результатов
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df)
    else:
        st.write('Нет активов по критериям.')
