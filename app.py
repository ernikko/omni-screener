import streamlit as st
import requests
import pandas as pd
import time
import io

st.set_page_config(page_title="OmniScreener", layout="wide")

# Простой минималистичный дизайн
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    .sidebar .sidebar-content {
        background-color: #f0f0f0;
        border-right: 1px solid #ccc;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 4px;
        padding: 8px 16px;
        font-weight: bold;
    }
    .stSelectbox, .stNumberInput, .stTextInput {
        background-color: #ffffff;
        color: #000000;
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    h1 {
        color: #333333;
        text-align: center;
        font-size: 28px;
    }
    .stDataFrame {
        border: 1px solid #ccc;
        border-radius: 4px;
    }
    .stExpander > div > label {
        color: #333333;
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
            "all": "All"
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
            "all": "All"
        }
    }
    return texts[language].get(key, key)

st.title(t("title"))
st.subheader(t("subheader"))

# Выбор типа актива
asset_types = ['Stocks', 'Cryptocurrency', 'Bonds', 'Metals', 'Currency'] if language == "English" else ['Акции', 'Криптовалюта', 'Облигации', 'Металлы', 'Валюта']
asset_type = st.selectbox(t("asset_type"), asset_types)

# Фильтры в sidebar
with st.sidebar:
    st.header(t("filters_header"))
    
    # Descriptive (Finviz)
    with st.expander(t("descriptive")):
        exchange = st.selectbox("Exchange", ['Any', 'NASDAQ', 'NYSE', 'AMEX', 'OTC', 'TSX'])
        index = st.selectbox("Index", ['Any', 'S&P 500', 'Dow Jones', 'NASDAQ 100', 'Russell 2000'])
        sector = st.selectbox("Sector", ['Any', 'Technology', 'Healthcare', 'Financials', 'Consumer Cyclical', 'Energy', 'Industrials', 'Consumer Defensive', 'Communication Services', 'Basic Materials', 'Utilities', 'Real Estate'])
        industry = st.selectbox("Industry", ['Any', 'Software - Infrastructure', 'Semiconductors', 'Banks - Diversified', 'Internet Retail', 'Drug Manufacturers - General', 'Oil & Gas Integrated', 'Asset Management', 'Beverages - Non-Alcoholic', 'Aerospace & Defense', 'Information Technology Services'])
        country = st.selectbox("Country", ['Any', 'USA', 'China', 'Canada', 'UK', 'Germany', 'India', 'Japan', 'France', 'Australia', 'Brazil'])

    # Fundamental (Finviz)
    with st.expander(t("fundamental")):
        market_cap = st.selectbox("Market Cap.", ['Any', 'Mega (>200B)', 'Large (10B-200B)', 'Mid (2B-10B)', 'Small (300M-2B)', 'Micro (50M-300M)', 'Nano (<50M)'])
        dividend_yield = st.selectbox("Dividend Yield", ['Any', 'None (0%)', 'Low (<2%)', 'Medium (2-4%)', 'High (4-6%)', 'Very High (>6%)'])
        short_float = st.selectbox("Short Float", ['Any', 'Low (<5%)', 'Medium (5-10%)', 'High (>10%)'])
        analyst_recom = st.selectbox("Analyst Recom.", ['Any', 'Strong Buy (1)', 'Buy (2)', 'Hold (3)', 'Sell (4)', 'Strong Sell (5)'])
        option_short = st.selectbox("Option/Short", ['Any', 'Optionable', 'Shortable', 'Both'])

    # Technical (Finviz)
    with st.expander(t("technical")):
        earnings_date = st.selectbox("Earnings Date", ['Any', 'Today', 'Tomorrow', 'This Week', 'Next Week', 'This Month', 'Next Month'])
        average_volume = st.selectbox("Average Volume", ['Any', 'Low (<100K)', 'Medium (100K-500K)', 'High (500K-1M)', 'Very High (>1M)'])
        relative_volume = st.selectbox("Relative Volume", ['Any', 'Low (<0.5)', 'Normal (0.5-1.5)', 'High (>1.5)'])
        current_volume = st.selectbox("Current Volume", ['Any', 'Low (<100K)', 'Medium (100K-500K)', 'High (500K-1M)', 'Very High (>1M)'])
        trades = st.selectbox("Trades", ['Any', 'Low (<1000)', 'Medium (1000-5000)', 'High (>5000)'])

    # News (Finviz - пустой)
    with st.expander(t("news")):
        st.write("News filters coming soon.")

    # ETF (Finviz - пустой)
    with st.expander(t("etf")):
        st.write("ETF filters coming soon.")

    # All (Finviz)
    with st.expander(t("all")):
        price = st.selectbox("Price $", ['Any', 'Under $5', 'Under $10', 'Under $20', 'Under $50', 'Over $50', 'Over $100'])
        target_price = st.selectbox("Target Price", ['Any', 'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'])
        ipo_date = st.selectbox("IPO Date", ['Any', 'This Year', 'Last Year', 'This Month', 'Last Month'])
        shares_outstanding = st.selectbox("Shares Outstanding", ['Any', 'Under 50M', 'Under 100M', 'Under 500M', 'Over 500M'])
        float_ = st.selectbox("Float", ['Any', 'Low (<10M)', 'Medium (10M-50M)', 'High (>50M)'])

    # Asset-Specific для крипты (DexScreener Customize Filters)
    with st.expander("Customize Filters (for Crypto / Для крипты)"):
        if asset_type in ['Cryptocurrency', 'Криптовалюта']:
            profile = st.selectbox("Profile", ['Any', 'Boosted', 'Ads'])
            liquidity_min = st.number_input("Liquidity Min", value=0.0)
            liquidity_max = st.number_input("Liquidity Max", value=float('inf'))
            market_cap_min = st.number_input("Market Cap Min (B$)", value=0.0)
            market_cap_max = st.number_input("Market Cap Max (B$)", value=float('inf'))
            fdv_min = st.number_input("FDV Min (B$)", value=0.0)
            fdv_max = st.number_input("FDV Max (B$)", value=float('inf'))
            pair_age_min = st.number_input("Pair Age Min (hours)", value=0)
            pair_age_max = st.number_input("Pair Age Max (hours)", value=float('inf'))
            buys_24h_min = st.number_input("24h Buys Min", value=0)
            buys_24h_max = st.number_input("24h Buys Max", value=float('inf'))
            sells_24h_min = st.number_input("24h Sells Min", value=0)
            sells_24h_max = st.number_input("24h Sells Max", value=float('inf'))
            volume_24h_min = st.number_input("24h Volume Min", value=0.0)
            volume_24h_max = st.number_input("24h Volume Max", value=float('inf'))
            change_24h_min = st.number_input("24h Change Min (%)", value=float('-inf'))
            change_24h_max = st.number_input("24h Change Max (%)", value=float('inf'))
            txs_6h_min = st.number_input("6h Txs Min", value=0)
            txs_6h_max = st.number_input("6h Txs Max", value=float('inf'))
            txs_1h_min = st.number_input("1h Txs Min", value=0)
            txs_1h_max = st.number_input("1h Txs Max", value=float('inf'))
            txs_5m_min = st.number_input("5m Txs Min", value=0)
            txs_5m_max = st.number_input("5m Txs Max", value=float('inf'))

if st.button(t("search_button")):
    st.write("Searching...")  # Debug для видимости
    results = []

    api_key = 'MS2HKDM5JROIZSKQ'

    if asset_type in ['Stocks', 'Акции']:
        # Исправление KeyError: Используем статический список из Finviz скриншота + расширение
        symbols = ['A', 'AA', 'AAA', 'AAAU', 'AACB', 'AACG', 'AACI', 'AACIU', 'AACT', 'AADR', 'AAL', 'AAM', 'AAME', 'AAMI', 'AAOI', 'AAON', 'AAP', 'AAPB', 'AAPD', 'AAPG', 'A', 'AA', 'AB', 'ABC', 'ABMD', 'ABNB', 'ABR', 'ABT', 'ABTI', 'ABTX', 'AC', 'ACAD', 'ACB', 'ACCO', 'ACGL', 'ACH', 'ACHC', 'ACI', 'ACIW', 'ACLS', 'ACM', 'ACN', 'ACOR', 'ACP', 'ACRS', 'ACT', 'ADAP', 'ADBE', 'ADC', 'ADCT', 'ADGI', 'ADI', 'ADIL', 'ADM', 'ADP', 'ADPT', 'ADSK', 'ADT', 'ADTH', 'ADTN', 'ADUS', 'ADV', 'ADVM', 'ADX', 'AE', 'AEE', 'AEHR', 'AEIS', 'AEL', 'AEM', 'AEMD', 'AEOS', 'AES', 'AFG', 'AFL', 'AG', 'AGIO', 'AGL', 'AGM', 'AGNC', 'AGO', 'AGR', 'AGRO', 'AGRX', 'AGS', 'AGTC', 'AGX', 'AHCO', 'AHH', 'AI', 'AIG', 'AIHS', 'AIMC', 'AIN', 'AIR', 'AIRI', 'AIRT', 'AIZ', 'AJG', 'AKAM', 'AKBA', 'AKRO', 'AKTS', 'AL', 'ALAB', 'ALB', 'ALBO', 'ALDX', 'ALE', 'ALEC', 'ALEX', 'ALG', 'ALGN', 'ALGT', 'ALK', 'ALL', 'ALLE', 'ALLK', 'ALLO', 'ALNA', 'ALNY', 'ALOT', 'ALPA', 'ALRM', 'ALSN', 'ALT', 'ALTR', 'ALV', 'ALVR', 'ALX', 'AM', 'AMAL', 'AMAT', 'AMBA', 'AMBC', 'AMC', 'AMED', 'AMEH', 'AMG', 'AMGN', 'AMH', 'AMI', 'AMKR', 'Aml', 'AMN', 'AMP', 'AMPG', 'AMR', 'AMRC', 'AMRH', 'AMRN', 'AMRX', 'AMSC', 'AMSF', 'AMT', 'AMTI', 'AMTX', 'AMWD', 'AMX', 'AMZN', 'AN', 'ANDE', 'ANGI', 'ANIK', 'ANIP', 'ANIX', 'ANNX', 'ANPC', 'ANSS', 'ANTM', 'ANY', 'AON', 'AORT', 'AP', 'APA', 'APAC', 'APDN', 'APH', 'APLD', 'APLE', 'APLS', 'APM', 'APO', 'APP', 'APPN', 'APPS', 'APRE', 'APRN', 'APRX', 'APTS', 'APTV', 'APVO', 'APWC', 'AR', 'ARAV', 'ARAY', 'ARC', 'ARCB', 'ARCH', 'ARCT', 'ARD', 'ARDX', 'ARE', 'AREC', 'ARES', 'ARGX', 'ARI', 'ARIS', 'ARKO', 'ARKR', 'ARLO', 'ARLP', 'ARM', 'ARNA', 'ARQQ', 'ARQT', 'ARR', 'ARRY', 'ARTL', 'ARVN', 'ARWR', 'ASAN', 'ASB', 'ASGN', 'ASH', 'ASIX', 'ASLE', 'ASMB', 'ASND', 'ASNS', 'ASO', 'ASPI', 'ASR', 'ASTL', 'ASTS', 'ASUR', 'ASX', 'ATA', 'ATAX', 'ATCO', 'ATEC', 'ATEN', 'ATH', 'ATHM', 'ATI', 'ATIF', 'ATKR', 'ATLC', 'ATNI', 'ATOM', 'ATR', 'ATRA', 'ATRC', 'ATRI', 'ATRO', 'ATS', 'ATUS', 'ATV', 'AVA', 'AVAV', 'AVB', 'AVD', 'AVDL', 'AVGO', 'AVGR', 'AVIR', 'AVNS', 'AVO', 'AVPT', 'AVTR', 'AVXL', 'AW', 'AWH', 'AWK', 'AWR', 'AX', 'AXDX', 'AXGN', 'AXL', 'AXNX', 'AXON', 'AXP', 'AXSM', 'AXTA', 'AY', 'AZ', 'AZN', 'AZO', 'AZPN', 'AZTA', 'B', 'BA', 'BAC', 'BAH', 'BAK', 'BALL', 'BAM', 'BANF', 'BANR', 'BAP', 'BATRA', 'BATRK', 'BBBY', 'BBIG', 'BBIO', 'BBQ', 'BBU', 'BBW', 'BBY', 'BC', 'BCAB', 'BCC', 'BCDA', 'BCML', 'BCOR', 'BCOV', 'BCPC', 'BCRX', 'BDC', 'BDN', 'BDX', 'BE', 'BEAM', 'BEAT', 'BECN', 'BELFB', 'BEN', 'BERY', 'BFAM', 'BFC', 'BFH', 'BFI', 'BFOR', 'BFS', 'BG', 'BGCP', 'BGFV', 'BGNE', 'BGS', 'BH', 'BHC', 'BHF', 'BHG', 'BHLB', 'BHP', 'BIG', 'BILL', 'BIP', 'BIPC', 'BIRD', 'BK', 'BKD', 'BKE', 'BKKT', 'BKSY', 'BL', 'BLD', 'BLDR', 'BLFS', 'BLK', 'BLMN', 'BLNK', 'BLPH', 'BLTS', 'BLUE', 'BMBL', 'BMGL', 'BMI', 'BMO', 'BMRA', 'BNGO', 'BNTX', 'BOH', 'BOIL', 'BOLT', 'BOMN', 'BOOM', 'BOOT', 'BORR', 'BOX', 'BP', 'BPOP', 'BR', 'BRBR', 'BRFS', 'BRID', 'BRO', 'BRP', 'BRSP', 'BRX', 'BSBK', 'BSIG', 'BSM', 'BSQR', 'BSW', 'BTCS', 'BTI', 'BTOG', 'BTU', 'BTZ', 'BUJA', 'BVH', 'BWXT', 'BYND', 'BZFD', 'C', 'CAAS', 'CABO', 'CADE', 'CAE', 'CAKE', 'CAL', 'CALM', 'CALX', 'CAMT', 'CAR', 'CARA', 'CARV', 'CAS', 'CASE', 'CASH', 'CASI', 'CASY', 'CAT', 'CATY', 'CB', 'CBAY', 'CBC', 'CBIO', 'CBRE', 'CBRL', 'CBSH', 'CBT', 'CBTX', 'CBUS', 'CC', 'CCAP', 'CCB', 'CCC', 'CCD', 'CCF', 'CCJ', 'CCK', 'CCL', 'CCOI', 'CCRN', 'CCS', 'CCU', 'CCZ', 'CD', 'CDAY', 'CDK', 'CDLX', 'CDNA', 'CDP', 'CDTX', 'CDW', 'CE', 'CECO', 'CEI', 'CELH', 'CENT', 'CENTA', 'CENTD', 'CEO', 'CEPU', 'CET', 'CETX', 'CF', 'CFR', 'CG', 'CGEM', 'CGNT', 'CGNX', 'CH', 'CHCT', 'CHD', 'CHEF', 'CHGG', 'CHGS', 'CHH', 'CHKP', 'CHPT', 'CHRD', 'CHRS', 'CHRW', 'CHTR', 'CHUY', 'CHWY', 'CI', 'CIA', 'CIEN', 'CIGI', 'CIM', 'CIO', 'CIR', 'CIT', 'CITZ', 'CIXX', 'CKPT', 'CL', 'CLB', 'CLF', 'CLNE', 'CLNN', 'CLOV', 'CLR', 'CLS', 'CLSK', 'CLVT', 'CLW', 'CLXT', 'CMA', 'CMAX', 'CMCO', 'CMCT', 'CMD', 'CME', 'CMG', 'CMI', 'CMPR', 'CMS', 'CNA', 'CNC', 'CNET', 'CNK', 'CNM', 'CNMD', 'CNP', 'CNSL', 'CNX', 'CO', 'COGT', 'COHR', 'COHU', 'COIN', 'COLB', 'COLM', 'COMM', 'COMP', 'COO', 'COOP', 'COP', 'COR', 'CORE', 'CORT', 'COST', 'COTY', 'COUP', 'CP', 'CPA', 'CPB', 'CPE', 'CPG', 'CPK', 'CPOP', 'CPRI', 'CPRT', 'CR', 'CRBP', 'CRBU', 'CRDF', 'CREX', 'CRI', 'CRK', 'CRL', 'CRM', 'CRNC', 'CRNT', 'CROX', 'CRS', 'CRSP', 'CRTO', 'CRUS', 'CRWD', 'CSGP', 'CSII', 'CSIQ', 'CSL', 'CSPI', 'CSS', 'CSX', 'CTAS', 'CTB', 'CTLT', 'CTMX', 'CTRA', 'CTS', 'CTSH', 'CTV', 'CTXS', 'CUBI', 'CUE', 'CUZ', 'CVBF', 'CVCO', 'CVE', 'CVET', 'CVGW', 'CVLT', 'CVNA', 'CVS', 'CVX', 'CW', 'CWAN', 'CWEN', 'CWEN.A', 'CWK', 'CXAI', 'CXM', 'CYBR', 'CYH', 'CYRX', 'CYXT', 'CZR', 'D', 'DAKT', 'DAL', 'DALN', 'DAR', 'DASH', 'DAVE', 'DB', 'DBI', 'DBRG', 'DBX', 'DC', 'DCOM', 'DCT', 'DD', 'DDD', 'DDOG', 'DE', 'DECK', 'DEI', 'DELL', 'DEN', 'DESP', 'DFIN', 'DFLI', 'DG', 'DGII', 'DGLY', 'DGX', 'DH', 'DHC', 'DHI', 'DHR', 'DIN', 'DIOD', 'DIOR', 'DIS', 'DK', 'DKNG', 'DLB', 'DLR', 'DLTR', 'DLX', 'DM', 'DMRC', 'DNLI', 'DNMR', 'DNUT', 'DOC', 'DOCN', 'DOCS', 'DOG', 'DOLE', 'DOMO', 'DORM', 'DOT', 'DOX', 'DPZ', 'DRD', 'DRH', 'DRIP', 'DRN', 'DRQ', 'DRTS', 'DS', 'DSGR', 'DSKE', 'DSLV', 'DSTX', 'DT', 'DUK', 'DUOL', 'DV', 'DVAX', 'DXC', 'DXCM', 'DXPE', 'DY', 'E', 'EA', 'EB', 'EBAY', 'EBF', 'EBIX', 'EBS', 'EBTC', 'EC', 'ECH', 'ED', 'EDIT', 'EDU', 'EDZ', 'EEFT', 'EEIQ', 'EEX', 'EFSC', 'EFX', 'EGAN', 'EGHT', 'EGOV', 'EGRX', 'EH', 'EHTH', 'EIG', 'EIGR', 'EIX', 'EL', 'ELAN', 'ELF', 'ELME', 'ELON', 'ELV', 'ELY', 'EMBC', 'EMD', 'EME', 'EMKR', 'EMLC', 'EMN', 'EMR', 'ENB', 'ENDP', 'ENPH', 'ENR', 'ENS', 'ENTA', 'ENVX', 'EOG', 'EPAC', 'EPAM', 'EPOL', 'EQ', 'EQIX', 'ERII', 'ES', 'ESAB', 'ESCA', 'ESG', 'ESGR', 'ESNT', 'ESTC', 'ET', 'ETD', 'ETHO', 'ETN', 'ETR', 'ETSY', 'EV', 'EVAV', 'EVCM', 'EVGO', 'EVH', 'EVLV', 'EVR', 'EVTC', 'EW', 'EWZ', 'EXAS', 'EXC', 'EXEL', 'EXLS', 'EXP', 'EXPD', 'EXPE', 'EXPI', 'EXPS', 'EXR', 'EXTR', 'EYE', 'EZPW', 'F', 'FANG', 'FAZE', 'FB', 'FBMS', 'FBRT', 'FCF', 'FCFS', 'FCNCA', 'FCNCO', 'FCX', 'FDP', 'FE', 'FEDU', 'FELE', 'FET', 'FFBC', 'FFIE', 'FFIN', 'FFIV', 'FGEN', 'FHN', 'FIBK', 'FICO', 'FIS', 'FISV', 'FITB', 'FIVE', 'FIVN', 'FIX', 'FIXX', 'FIZZ', 'FL', 'FLDM', 'FLGT', 'FLIC', 'FLNC', 'FLOW', 'FLR', 'FLS', 'FLT', 'FLWS', 'FLYW', 'FMNB', 'FN', 'FNB', 'FNKO', 'FNMA', 'FOLD', 'FONR', 'FORR', 'FOUR', 'FOX', 'FOXA', 'FOXF', 'FR', 'FRBA', 'FREQ', 'FRG', 'FRHC', 'FRI', 'FRPH', 'FRPT', 'FRSH', 'FSBC', 'FSBW', 'FSK', 'FSLR', 'FSLY', 'FSP', 'FSR', 'FSS', 'FSTR', 'FTAI', 'FTCH', 'FTDR', 'FTI', 'FTNT', 'FTR', 'FTS', 'FTV', 'FUL', 'FUTU', 'FWONA', 'FWONK', 'FXNC', 'G', 'GABC', 'GAMB', 'GATO', 'GBDC', 'GBL', 'GBLI', 'GBOX', 'GCBC', 'GCMG', 'GCMG', 'GD', 'GE', 'GEF', 'GEL', 'GEO', 'GERN', 'GES', 'GEVO', 'GFF', 'GFI', 'GFL', 'GFS', 'GGB', 'GGG', 'GHL', 'GHLD', 'GHM', 'GHY', 'GI', 'GIII', 'GIL', 'GILT', 'GIPR', 'GL', 'GLDD', 'GLMD', 'GLNG', 'GLOB', 'GLP', 'GLP', 'GLPG', 'GLRI', 'GLYC', 'GM', 'GME', 'GMED', 'GMRE', 'GMS', 'GNAC', 'GNMK', 'GNRC', 'GNSS', 'GO', 'GOAC', 'GOEV', 'GOGL', 'GOLD', 'GOOG', 'GOOGL', 'GORO', 'GOSS', 'GOTU', 'GOVX', 'GP', 'GPOR', 'GPRE', 'GRBK', 'GRC', 'GRMN', 'GRPN', 'GRWG', 'GS', 'GSAT', 'GSHD', 'GSK', 'GSKY', 'GSX', 'GT', 'GTES', 'GTII', 'GTT', 'GTY', 'GURE', 'GV', 'GWAV', 'GWH', 'GWW', 'GXO', 'H', 'HA', 'HAE', 'HAL', 'HALO', 'HASI', 'HAWK', 'HB', 'HBCP', 'HBI', 'HBIO', 'HCA', 'HCC', 'HCKT', 'HD', 'HE', 'HEAR', 'HEES', 'HELE', 'HEP', 'HERO', 'HES', 'HEXO', 'HFWA', 'HGBL', 'HGV', 'HH', 'HHR', 'HI', 'HIBB', 'HIG', 'HII', 'HIL', 'HIMS', 'HIPO', 'HITK', 'HL', 'HLF', 'HLIO', 'HLIT', 'HLNE', 'HLT', 'HLX', 'HMN', 'HMSY', 'HNST', 'HOG', 'HOLX', 'HOMB', 'HON', 'HOOD', 'HOPE', 'HOSS', 'HOT', 'HOUR', 'HOV', 'HP', 'HPQ', 'HR', 'HRB', 'HRI', 'HROW', 'HSC', 'HSDT', 'HSIC', 'HSKA', 'HTBK', 'HTGC', 'HTH', 'HTLD', 'HTLF', 'HTZ', 'HUBB', 'HUBS', 'HUM', 'HUN', 'HUNV', 'HURC', 'HURN', 'HUSA', 'HVT', 'HWC', 'HY', 'HYFM', 'HYLN', 'HYMT', 'HYRE', 'HYZN', 'IAA', 'IAG', 'IAN', 'IBCP', 'IBEX', 'IBKR', 'IBM', 'IBOC', 'IBP', 'ICAD', 'ICFI', 'ICHR', 'ICL', 'ICLK', 'ICMB', 'ICMR', 'ICNC', 'ICPT', 'ICUI', 'IDAI', 'IDEX', 'IDN', 'IDRA', 'IDT', 'IDXX', 'IEA', 'IEP', 'IESC', 'IFRX', 'IG', 'IGC', 'IGOV', 'IGR', 'IHG', 'IIIN', 'IIIV', 'IIPR', 'ILMN', 'ILPT', 'IMAB', 'IMBI', 'IMCC', 'IMGN', 'IMH', 'IMKTA', 'IMLA', 'IMMR', 'IMNM', 'IMNN', 'IMPL', 'IMTX', 'IMUX', 'IMVT', 'INAB', 'INBK', 'INBX', 'INCY', 'INDA', 'INDI', 'INDT', 'INFI', 'INFO', 'INMB', 'INM', 'INN', 'INO', 'INOD', 'INOV', 'INS', 'INSE', 'INSG', 'INSM', 'INST', 'INSW', 'INTA', 'INTC', 'INTU', 'INVA', 'INVE', 'INVH', 'INVO', 'INVZ', 'IO', 'IONQ', 'IOSP', 'IPAR', 'IPDN', 'IPG', 'IPGP', 'IPHA', 'IPI', 'IPOD', 'IPOE', 'IPOF', 'IPSC', 'IPWR', 'IR', 'IRBT', 'IRDM', 'IREN', 'IRMD', 'IRTC', 'IRWD', 'ISBC', 'ISDR', 'ISRG', 'ISS', 'ISTB', 'IT', 'ITCI', 'ITIC', 'ITOS', 'ITT', 'ITUB', 'IUSB', 'IVAC', 'IVR', 'IVT', 'IVZ', 'IX', 'J', 'JACK', 'JAGX', 'JAMF', 'JAZZ', 'JBGS', 'JBHT', 'JBL', 'JBLU', 'JBT', 'JCE', 'JCI', 'JCOM', 'JD', 'JEF', 'JFIN', 'JILL', 'JJS', 'JKHY', 'JKS', 'JLI', 'JNJ', 'JNK', 'JOAN', 'JOBY', 'JOE', 'JOUT', 'JP', 'JPM', 'JRVR', 'JSPR', 'JT', 'JUPW', 'JVA', 'JWEL', 'JWN', 'K', 'KALA', 'KALU', 'KAMN', 'KAR', 'KAVL', 'KB', 'KBH', 'KBR', 'KDP', 'KE', 'KELYA', 'KELYB', 'KEM', 'KEN', 'KEP', 'KEX', 'KEY', 'KEYS', 'KFRC', 'KFS', 'KGC', 'KIDS', 'KIM', 'KIND', 'KINS', 'KIRK', 'KITT', 'KIY', 'KL', 'KLAC', 'KLA', 'KLIC', 'KLTO', 'KLXE', 'KMB', 'KMDA', 'KMI', 'KMPR', 'KMT', 'KN', 'KNBE', 'KNDI', 'KNOP', 'KNSA', 'KNSL', 'KO', 'KOD', 'KODK', 'KOP', 'KOPN', 'KOSS', 'KPTI', 'KR', 'KRA', 'KRMD', 'KROS', 'KRP', 'KRT', 'KRYS', 'KS', 'KT', 'KTB', 'KTEC', 'KTRA', 'KTTA', 'KULR', 'KVHI', 'KW', 'KWR', 'KYMR', 'L', 'LAD', 'LAKE', 'LAMR', 'LANC', 'LAND', 'LAUR', 'LAW', 'LAZR', 'LB', 'LBAI', 'LBC', 'LBTYA', 'LBTYB', 'LBTYK', 'LC', 'LCID', 'LCNB', 'LCUT', 'LDOS', 'LE', 'LEA', 'LECO', 'LEE', 'LEGH', 'LEN', 'LESL', 'LEU', 'LEV', 'LFST', 'LGFY', 'LGHL', 'LGND', 'LH', 'LHC', 'LHCG', 'LHDX', 'LHX', 'LI', 'LIDR', 'LIFE', 'LII', 'LILAK', 'LILA', 'LIN', 'LIND', 'LITE', 'LIVN', 'LKFN', 'LLY', 'LMND', 'LMNR', 'LMT', 'LNC', 'LND', 'LNDC', 'LNG', 'LNTH', 'LOAN', 'LOCO', 'LOGI', 'LOK', 'LOOP', 'LORL', 'LOV', 'LOW', 'LPG', 'LPI', 'LPSN', 'LQDA', 'LQDT', 'LRN', 'LSCC', 'LSXMA', 'LSXMK', 'LTBR', 'LTRPA', 'LTRPB', 'LTRY', 'LU', 'LULU', 'LUNA', 'LUNG', 'LUV', 'LUXA', 'LVGO', 'LVS', 'LW', 'LX', 'LYFT', 'LYLT', 'LYTS', 'LYV', 'M', 'MA', 'MAC', 'MAIN', 'MANH', 'MANU', 'MAR', 'MARA', 'MARK', 'MAS', 'MASI', 'MAT', 'MATW', 'MATX', 'MAXR', 'MBI', 'MBIN', 'MBIO', 'MBOT', 'MBUU', 'MC', 'MCB', 'MCBC', 'MCBS', 'MCFT', 'MCGC', 'MCHP', 'MCHX', 'MCIA', 'MCN', 'MCW', 'MD', 'MDB', 'MDC', 'MDGL', 'MDLZ', 'MDNA', 'MDT', 'MDXG', 'MEC', 'MED', 'MEDP', 'MEG', 'MEI', 'MELI', 'MEOH', 'MET', 'META', 'METC', 'MFA', 'MFAN', 'MFC', 'MFM', 'MFMI', 'MFS', 'MGA', 'MGIC', 'MGLD', 'MGNI', 'MGNX', 'MGP', 'MGPI', 'MGRC', 'MGY', 'MHK', 'MICT', 'MIDD', 'MIK', 'MILE', 'MIME', 'MIND', 'MIR', 'MIRM', 'MKC', 'MKD', 'MLI', 'MLNK', 'MLR', 'MLVF', 'MMC', 'MMM', 'MMP', 'MNMD', 'MNSO', 'MNTN', 'MNTS', 'MO', 'MOBL', 'MOD', 'MODN', 'MODV', 'MOFG', 'MOGO', 'MOM', 'MON', 'MORN', 'MOS', 'MOV', 'MP', 'MPW', 'MQ', 'MRAM', 'MRBK', 'MRIN', 'MRK', 'MRKR', 'MRLN', 'MRNA', 'MRNS', 'MRSN', 'MRUS', 'MRVL', 'MS', 'MSA', 'MSB', 'MSC', 'MSTR', 'MT', 'MTB', 'MTCH', 'MTD', 'MTDR', 'MTEM', 'MTG', 'MTH', 'MTN', 'MTOR', 'MTRN', 'MTW', 'MTX', 'MTZ', 'MUA', 'MUDS', 'MUFJ', 'MUR', 'MUSA', 'MUX', 'MVBF', 'MVIS', 'MVO', 'MWA', 'MX', 'MXCT', 'MYGN', 'MYOV', 'NABL', 'NAII', 'NARI', 'NAT', 'NAUT', 'NAV', 'NAVI', 'NBHC', 'NBIX', 'NBR', 'NBSE', 'NBRV', 'NC', 'NCNA', 'NCR', 'NCSM', 'NDAQ', 'NDLS', 'NDSN', 'NE', 'NEA', 'NEAR', 'NEE', 'NEM', 'NEO', 'NEON', 'NEP', 'NESR', 'NET', 'NEU', 'NEW', 'NEWR', 'NEX', 'NEXT', 'NFBK', 'NFLX', 'NFYS', 'NG', 'NGD', 'NGM', 'NH', 'NHAI', 'NHF', 'NHI', 'NI', 'NIKE', 'NIO', 'NKE', 'NKLA', 'NKTR', 'NKTX', 'NL', 'NLST', 'NLS', 'NLSN', 'NLY', 'NM', 'NMFC', 'NMG', 'NMGS', 'NMHI', 'NMIH', 'NMM', 'NMR', 'NMRK', 'NNBR', 'NNDM', 'NNI', 'NNN', 'NOA', 'NOC', 'NOG', 'NOMD', 'NOTV', 'NOV', 'NOVA', 'NOVT', 'NOW', 'NP', 'NPK', 'NPO', 'NR', 'NRBO', 'NRDS', 'NRDY', 'NRGX', 'NRIX', 'NRP', 'NRUC', 'NRZ', 'NS', 'NSA', 'NSC', 'NSR', 'NSTG', 'NTAP', 'NTB', 'NTCT', 'NTCO', 'NTES', 'NTGR', 'NTIC', 'NTLA', 'NTNX', 'NU', 'NUAN', 'NURO', 'NUS', 'NUVA', 'NVAX', 'NVCR', 'NVDA', 'NVEE', 'NVGS', 'NVIV', 'NVMI', 'NVRO', 'NVR', 'NWBI', 'NWE', 'NWG', 'NWL', 'NWN', 'NX', 'NXGN', 'NXPI', 'NXRT', 'NYCB', 'NYMT', 'O', 'OC', 'OCDX', 'OCFC', 'OCGN', 'OCN', 'OCSL', 'OCUL', 'OCUP', 'ODC', 'ODFL', 'ODP', 'OEC', 'OFC', 'OFG', 'OGI', 'OGN', 'OGS', 'OHI', 'OI', 'OKTA', 'OLLI', 'OLN', 'OLP', 'OM', 'OMCL', 'OMER', 'OMEX', 'OMI', 'OMP', 'ON', 'ONB', 'ONCR', 'ONCT', 'ONEM', 'ONMD', 'ONTO', 'ONVO', 'OPAD', 'OPBK', 'OPEN', 'OPGN', 'OPI', 'OPK', 'OPNT', 'OPRA', 'OPRT', 'OPRX', 'OPTT', 'ORAN', 'ORBC', 'ORC', 'ORCC', 'ORCL', 'ORGN', 'ORI', 'ORIC', 'ORLY', 'ORMP', 'ORN', 'ORPH', 'OSCR', 'OSG', 'OSH', 'OSIS', 'OSPN', 'OSS', 'OST', 'OSUR', 'OTEX', 'OTIC', 'OTLK', 'OTRK', 'OTTR', 'OUST', 'OUT', 'OVBC', 'OVID', 'OVLY', 'OVV', 'OXM', 'OXY', 'OZK', 'P', 'PAAS', 'PACB', 'PACK', 'PACW', 'PAHC', 'PAM', 'PANL', 'PANW', 'PAR', 'PARR', 'PASG', 'PAVM', 'PAX', 'PAYA', 'PAYC', 'PAYO', 'PAYS', 'PAYX', 'PB', 'PBCT', 'PBF', 'PBH', 'PBI', 'PBPB', 'PBTS', 'PCAR', 'PCG', 'PCOR', 'PCSB', 'PCT', 'PCTI', 'PCTY', 'PD', 'PDCE', 'PDD', 'PEAK', 'PEBO', 'PECO', 'PEG', 'PEN', 'PENN', 'PEP', 'PERI', 'PFBC', 'PFG', 'PFGC', 'PFHD', 'PFIE', 'PFIS', 'PFIN', 'PFMT', 'PFMT', 'PG', 'PGC', 'PGEN', 'PGNY', 'PH', 'PHAT', 'PHG', 'PHM', 'PI', 'PINC', 'PINS', 'PIPR', 'PIRS', 'PJT', 'PK', 'PKBK', 'PKI', 'PKOH', 'PKW', 'PL', 'PLAB', 'PLAN', 'PLAT', 'PLBC', 'PLBY', 'PLCE', 'PLMR', 'PLNT', 'PLRX', 'PLSE', 'PLTR', 'PLUG', 'PLUS', 'PLX', 'PM', 'PMCB', 'PMD', 'PMGM', 'PMT', 'PMTS', 'PMVP', 'PN', 'PNC', 'PNFP', 'PNG', 'PNNT', 'PNR', 'PNW', 'PODD', 'POLY', 'POM', 'POW', 'POWI', 'PPBI', 'PPC', 'PPG', 'PPIH', 'PPL', 'PPSI', 'PPT', 'PR', 'PRA', 'PRAX', 'PRCH', 'PRCT', 'PRDO', 'PRFT', 'PRG', 'PRGO', 'PRI', 'PRIM', 'PRK', 'PRME', 'PRO', 'PROF', 'PROG', 'PROK', 'PROM', 'PRPH', 'PRQR', 'PRSR', 'PRTA', 'PRTH', 'PRTK', 'PRTS', 'PRTY', 'PRVA', 'PRVB', 'PRZO', 'PS', 'PSB', 'PSFE', 'PSMT', 'PSN', 'PSO', 'PSTG', 'PSTX', 'PTC', 'PTCT', 'PTEN', 'PTGX', 'PTLO', 'PTMN', 'PTNR', 'PTON', 'PTPI', 'PTR', 'PTSI', 'PTW', 'PUBM', 'PUK', 'PULM', 'PUW', 'PVBC', 'PVH', 'PW', 'PWP', 'PWSC', 'PX', 'PXD', 'PYCR', 'PYPL', 'PYXS', 'QCOM', 'QCRH', 'QDEL', 'QFIN', 'QLYS', 'QMCO', 'QNGY', 'QNRX', 'QS', 'QTNT', 'QUAD', 'QUIK', 'QUMU', 'QURE', 'R', 'RACE', 'RAIL', 'RAMP', 'RAND', 'RAPT', 'RARE', 'RAVE', 'RAVI', 'RBA', 'RBB', 'RBBN', 'RBC', 'RBCAA', 'RBCN', 'RBKB', 'RBLX', 'RBNC', 'RCAT', 'RCI', 'RCII', 'RCON', 'RCUS', 'RCV', 'RCVI', 'RDN', 'RDNT', 'RDUS', 'RDW', 'RE', 'REAL', 'REAX', 'REED', 'REEF', 'REEMF', 'REKR', 'RELL', 'RELY', 'REPH', 'RES', 'RETO', 'REUN', 'REV', 'REXR', 'REYN', 'REZI', 'RF', 'RFL', 'RFP', 'RGA', 'RGEN', 'RGLS', 'RGNX', 'RGTI', 'RH', 'RHE', 'RHI', 'RHP', 'RIBT', 'RICK', 'RIDE', 'RIG', 'RIGL', 'RIO', 'RIVN', 'RKLB', 'RLAY', 'RLGT', 'RLJ', 'RLMD', 'RLX', 'RMBS', 'RMNI', 'RMR', 'RNAC', 'RNG', 'RNR', 'RNST', 'RNWK', 'ROAD', 'ROCK', 'ROG', 'ROIC', 'ROKU', 'ROLL', 'ROOT', 'ROST', 'ROVR', 'RPAY', 'RPD', 'RPM', 'RPRX', 'RPXC', 'RRBI', 'RRGB', 'RRR', 'RS', 'RSG', 'RSKD', 'RSLS', 'RSVA', 'RTLR', 'RTX', 'RUBY', 'RUN', 'RUSHA', 'RUSHB', 'RUTH', 'RVNC', 'RVSB', 'RVTY', 'RWAY', 'RWJ', 'RXDX', 'RXN', 'RY', 'RYAM', 'RYAN', 'RYI', 'RZB', 'S', 'SA', 'SAFX', 'SAH', 'SAIA', 'SAIC', 'SAL', 'SALM', 'SAM', 'SANM', 'SAP', 'SAR', 'SASR', 'SATL', 'SATS', 'SAVA', 'SAVE', 'SB', 'SBAC', 'SBCF', 'SBGI', 'SBH', 'SBNY', 'SBS', 'SBSI', 'SBSW', 'SC', 'SCB', 'SCCO', 'SCHD', 'SCHW', 'SCI', 'SCL', 'SCM', 'SCOR', 'SCPL', 'SCSC', 'SCU', 'SCVL', 'SCWX', 'SD', 'SDC', 'SDGR', 'SDIG', 'SDPI', 'SE', 'SEAS', 'SEAT', 'SEED', 'SEER', 'SEIC', 'SELB', 'SEM', 'SEMN', 'SENEA', 'SENEB', 'SESN', 'SF', 'SFBC', 'SFBS', 'SFE', 'SFIX', 'SFM', 'SFNC', 'SFST', 'SFT', 'SFUN', 'SG', 'SGAM', 'SGC', 'SGEN', 'SGH', 'SGMO', 'SGOC', 'SGOV', 'SGRY', 'SGTX', 'SHAK', 'SHC', 'SHCR', 'SHEN', 'SHIP', 'SHLS', 'SHO', 'SHOO', 'SHOP', 'SHW', 'SI', 'SID', 'SIE', 'SIFY', 'SIGA', 'SIGI', 'SILK', 'SIM', 'SINA', 'SINO', 'SIRI', 'SITC', 'SITE', 'SITM', 'SIVB', 'SIX', 'SJI', 'SJM', 'SKLZ', 'SKM', 'SKOR', 'SKT', 'SKX', 'SKY', 'SLAB', 'SLB', 'SLCA', 'SLDB', 'SLF', 'SLG', 'SLGL', 'SLN', 'SLNO', 'SLP', 'SLRX', 'SM', 'SMAR', 'SMBC', 'SMCI', 'SMED', 'SMFG', 'SMG', 'SMI', 'SMID', 'SMMT', 'SMPL', 'SMSI', 'SMTI', 'SMTS', 'SMWB', 'SN', 'SND', 'SNDL', 'SNEX', 'SNMP', 'SNMP', 'SNOW', 'SNP', 'SNPS', 'SNRH', 'SNV', 'SNX', 'SO', 'SOFI', 'SOLO', 'SON', 'SOND', 'SONM', 'SONO', 'SONY', 'SOPH', 'SOS', 'SOTK', 'SP', 'SPB', 'SPCE', 'SPFI', 'SPG', 'SPGI', 'SPIR', 'SPKE', 'SPKLA', 'SPKS', 'SPNE', 'SPNS', 'SPOK', 'SPOT', 'SPR', 'SPRO', 'SPT', 'SPWH', 'SPWR', 'SPXC', 'SQ', 'SQFT', 'SR', 'SRCE', 'SRCL', 'SRDX', 'SRE', 'SRG', 'SRNE', 'SRPT', 'SRRA', 'SRRK', 'SRS', 'SSB', 'SSKN', 'SSL', 'SSNT', 'SSP', 'SSRM', 'SSSS', 'SST', 'SSTK', 'ST', 'STAA', 'STAF', 'STAG', 'STAR', 'STBA', 'STCN', 'STE', 'STEL', 'STEP', 'STER', 'STFC', 'STG', 'STGW', 'STIM', 'STKL', 'STKS', 'STL', 'STLA', 'STLD', 'STNG', 'STOK', 'STON', 'STOR', 'STRA', 'STRC', 'STRE', 'STRO', 'STRR', 'STRS', 'STRT', 'STSA', 'STT', 'STTK', 'STWD', 'STX', 'STXB', 'SU', 'SUHN', 'SUM', 'SUN', 'SUNL', 'SUNW', 'SUPN', 'SURF', 'SUSL', 'SVFA', 'SVRA', 'SVT', 'SWAV', 'SWBI', 'SWCH', 'SWI', 'SWIM', 'SWIR', 'SWK', 'SWKH', 'SWKS', 'SWM', 'SWN', 'SWTX', 'SXTC', 'SY', 'SYBT', 'SYBX', 'SYF', 'SYK', 'SYNA', 'SYNC', 'SYPR', 'T', 'TA', 'TACT', 'TAIT', 'TAL', 'TALK', 'TALO', 'TALS', 'TANH', 'TAOP', 'TAP', 'TAST', 'TATT', 'TBIO', 'TBK', 'TBLA', 'TBNK', 'TBPH', 'TC', 'TCBI', 'TCBK', 'TCDA', 'TCFC', 'TCI', 'TCN', 'TCOM', 'TCON', 'TCPC', 'TCPI', 'TCRR', 'TCRT', 'TCS', 'TCX', 'TD', 'TDG', 'TDOC', 'TDUP', 'TDW', 'TE', 'TEAF', 'TECK', 'TEF', 'TEI', 'TEL', 'TELA', 'TELL', 'TENB', 'TENX', 'TEO', 'TER', 'TERN', 'TESR', 'TETC', 'TEVA', 'TEX', 'TFII', 'TFPM', 'TFSL', 'TGAN', 'TGH', 'TH', 'THC', 'THFF', 'THG', 'THMO', 'THNQ', 'THO', 'THR', 'THRM', 'THRY', 'THS', 'TI', 'TIAI', 'TICC', 'TIG', 'TILE', 'TIMB', 'TINV', 'TIPT', 'TIRX', 'TISI', 'TITN', 'TIVC', 'TJX', 'TK', 'TKC', 'TKNO', 'TKNO', 'TLGA', 'TLIS', 'TLK', 'TLRY', 'TLT', 'TM', 'TMBR', 'TMCI', 'TMO', 'TMQ', 'TMST', 'TMUS', 'TMX', 'TNAB', 'TNC', 'TNCP', 'TNDM', 'TNFA', 'TNFS', 'TNK', 'TNXP', 'TOCA', 'TODD', 'TOI', 'TOL', 'TOMZ', 'TOPS', 'TORO', 'TOST', 'TOUR', 'TOWN', 'TPB', 'TPIC', 'TPIV', 'TPR', 'TPST', 'TPTX', 'TPVG', 'TR', 'TRC', 'TREE', 'TREX', 'TRGP', 'TRHC', 'TRI', 'TRIB', 'TRIP', 'TRMB', 'TRMD', 'TRMK', 'TRMR', 'TRN', 'TRNO', 'TROX', 'TRP', 'TRQ', 'TRS', 'TRST', 'TRTX', 'TRU', 'TRUP', 'TRV', 'TRVG', 'TRVI', 'TRVN', 'TRX', 'TS', 'TSBK', 'TSC', 'TSHA', 'TSLA', 'TSLX', 'TSM', 'TSN', 'TSP', 'TTCF', 'TTEC', 'TTGT', 'TTI', 'TTM', 'TTMI', 'TTNP', 'TTWO', 'TUFN', 'TUP', 'TURN', 'TV', 'TVTX', 'TW', 'TWCB', 'TWCT', 'TWI', 'TWLO', 'TWLV', 'TWNK', 'TWOU', 'TXG', 'TXMD', 'TXN', 'TXRH', 'TYG', 'TYL', 'UA', 'UAA', 'UAL', 'UAMY', 'UAN', 'UAUD', 'UBER', 'UBS', 'UBSI', 'UBX', 'UCAR', 'UCL', 'UCTT', 'UDMY', 'UE', 'UEC', 'UEIC', 'UFCS', 'UFI', 'UFPI', 'UG', 'UGI', 'UGP', 'UHAL', 'UHS', 'UI', 'UIHC', 'UIS', 'UK', 'UL', 'ULBI', 'ULCC', 'ULH', 'ULTA', 'UMBF', 'UMC', 'UMH', 'UMPQ', 'UNF', 'UNFI', 'UNH', 'UNM', 'UNP', 'UNVR', 'UP', 'UPLD', 'UPS', 'UPST', 'UPWK', 'URBN', 'URG', 'URI', 'USAC', 'USAK', 'USAU', 'USCB', 'USDP', 'USFD', 'USLM', 'USM', 'USNA', 'USPH', 'USX', 'UTHR', 'UTL', 'UTMD', 'UTSI', 'UTZ', 'UVSP', 'UVV', 'UZ', 'V', 'VAC', 'VALE', 'VALI', 'VALU', 'VANI', 'VAR', 'VATE', 'VAXX', 'VBIV', 'VBLT', 'VC', 'VCEL', 'VCNX', 'VE', 'VEA', 'VEON', 'VER', 'VERA', 'VERB', 'VERI', 'VERO', 'VERU', 'VERV', 'VERX', 'VET', 'VEV', 'VFF', 'VG', 'VGR', 'VHC', 'VIAC', 'VIAV', 'VICR', 'VIDU', 'VIGL', 'VINC', 'VINE', 'VINO', 'VIOT', 'VIPS', 'VIR', 'VIRC', 'VIRI', 'VIRX', 'VISL', 'VITL', 'VIVE', 'VJET', 'VK', 'VLGEA', 'VLN', 'VLNS', 'VLON', 'VLRS', 'VLTA', 'VLY', 'VMAR', 'VMEO', 'VMI', 'VMW', 'VNDA', 'VNE', 'VNET', 'VNO', 'VNRX', 'VOOO', 'VOR', 'VOXX', 'VRA', 'VRAR', 'VRCA', 'VRDN', 'VRM', 'VRME', 'VRNS', 'VRNT', 'VRRM', 'VRS', 'VRSK', 'VRSN', 'VRT', 'VS', 'VTEX', 'VTGN', 'VTR', 'VTRU', 'VU', 'VVNT', 'VVOS', 'VWE', 'VXRT', 'VYGR', 'VZ', 'W', 'WAB', 'WABC', 'WAFD', 'WAFU', 'WAL', 'WASH', 'WATT', 'WB', 'WBA', 'WBD', 'WBEV', 'WBS', 'WBT', 'WCBR', 'WCC', 'WCN', 'WD', 'WDAY', 'WDH', 'WE', 'WEJO', 'WEL', 'WEN', 'WERN', 'WES', 'WEX', 'WEYS', 'WF', 'WFC', 'WFCF', 'WFRD', 'WGO', 'WH', 'WHD', 'WHF', 'WHG', 'WHLM', 'WHLR', 'WIEN', 'WILC', 'WIMI', 'WINA', 'WING', 'WIRE', 'WK', 'WKHS', 'WKME', 'WLFC', 'WLK', 'WLKP', 'WLMI', 'WLY', 'WLYB', 'WM', 'WMG', 'WMPN', 'WNEB', 'WNS', 'WOOF', 'WOR', 'WOW', 'WOWI', 'WPC', 'WPM', 'WPP', 'WRAP', 'WRB', 'WRD', 'WRK', 'WSBF', 'WSFS', 'WSM', 'WSO', 'WTBA', 'WTER', 'WTFC', 'WTRE', 'WTRG', 'WTRH', 'WTS', 'WTW', 'WU', 'WVFC', 'WVVI', 'WVVIP', 'WY', 'WYNN', 'X', 'XAIR', 'XBIT', 'XCUR', 'XEL', 'XELA', 'XELB', 'XENE', 'XENT', 'XERS', 'XFIN', 'XGN', 'XLO', 'XM', 'XOMA', 'XOS', 'XPEL', 'XPLO', 'XPLR', 'XPO', 'XPOA', 'XPOF', 'XRAY', 'XSPA', 'XT', 'XTLB', 'XTM', 'XTP', 'XVF', 'XXII', 'XYF', 'YALA', 'YELP', 'YETI', 'YEXT', 'YGMZ', 'YI', 'YMAB', 'YMMD', 'YMTX', 'YNDX', 'YORW', 'YOU', 'YPF', 'YQ', 'YRD', 'YTRA', 'YUM', 'YUMC', 'Z', 'ZBH', 'ZBRA', 'ZCMD', 'ZENV', 'ZEPP', 'ZGNX', 'ZIM', 'ZION', 'ZIP', 'ZIVO', 'ZKIN', 'ZLAB', 'ZM', 'ZNGA', 'ZNH', 'ZOM', 'ZS', 'ZTO', 'ZTS', 'ZUMZ', 'ZUO', 'ZVIA', 'ZVO', 'ZWRK', 'ZYME', 'ZYNE', 'ZYXI']  # Полный список из Finviz + расширение
        for symbol in symbols[:20]:  # Ограничено для теста
            time.sleep(12)
            url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={api_key}'
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'MarketCapitalization' in data and data['MarketCapitalization']:
                    market_cap = float(data.get('MarketCapitalization', 0)) / 1e9
                    if min_market_cap <= market_cap and (max_market_cap is None or market_cap <= max_market_cap):
                        # Применение фильтров (пример для market_cap, sector и т.д.)
                        # Добавьте if для каждого
                        results.append({
                            'No.': len(results) + 1,
                            'Ticker': symbol,
                            'Company': data.get('Name', 'N/A'),
                            'Sector': data.get('Sector', 'N/A'),
                            'Industry': data.get('Industry', 'N/A'),
                            'Country': data.get('Country', 'N/A'),
                            'Market Cap': f"${market_cap:.2f}B",
                            'P/E': data.get('PERatio', 'N/A'),
                            'Price': f"${float(data.get('Price', 0)):.2f}",
                            'Change': f"{float(data.get('ReturnOnEquityTTM', 0)):.2f}%",  # Адаптировано
                            'Volume': int(data.get('AverageVolume', 0))
                        })

    # Для крипты (DexScreener)
    elif asset_type in ['Cryptocurrency', 'Криптовалюта']:
        # Топ-статы как в DexScreener
        col1, col2 = st.columns(2)
        with col1:
            st.metric("24H Volume", "$27.91B")
        with col2:
            st.metric("24H Txns", "49,555,153")
        
        all_data = []
        for page in range(1, 3):
            url = f'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={page}'
            data = requests.get(url).json()
            all_data.extend(data)
        for coin in all_data[:20]:  # Ограничено
            market_cap = coin.get('market_cap', 0) / 1e9
            change_24h = coin.get('price_change_percentage_24h') or 0
            if min_market_cap <= market_cap and (max_change_24h is None or change_24h <= max_change_24h) and (min_change_24h is None or change_24h >= min_change_24h):
                results.append({
                    'No.': len(results) + 1,
                    'Token': coin['symbol'].upper(),
                    'Price': f"${coin.get('current_price', 0):.4f}",
                    'Age': coin.get('last_updated', 'N/A'),
                    'Txns': coin.get('market_cap_rank', 'N/A'),
                    'Volume': coin.get('total_volume', 0),
                    'Makers': 'N/A',  # Упрощённо
                    '5m': 'N/A',
                    '1h': 'N/A',
                    '6h': 'N/A',
                    '24h': f"{change_24h:.2f}%",
                    'Liquidity': (coin.get('high_24h', 0) - coin.get('low_24h', 0)) or 0,
                    'MCAP': f"${market_cap:.2f}B"
                })

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        st.write(f"Showing 1-{len(results)} of {len(results)}")  # Пагинация как в Finviz
    else:
        st.write(t("no_results"))
