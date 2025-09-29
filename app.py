import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="OmniScreener", layout="wide")

# Минималистичный дизайн (светлый, читаемый)
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    .stButton > button {
        background-color: #007bff;
        color: white;
        border-radius: 4px;
        padding: 10px 20px;
        margin: 5px;
        font-weight: bold;
    }
    .stDialog {
        background-color: #ffffff;
        border: 2px solid #007bff;
        border-radius: 4px;
        padding: 20px;
        max-height: 80vh;
        overflow-y: auto;
    }
    .stDialog .stButton > button {
        background-color: #0056b3;
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
</style>
""", unsafe_allow_html=True)

# Переключатель языка
language = st.selectbox("Language / Язык", ["English", "Russian"])

# Функция для текстов
def t(key):
    texts = {
        "English": {
            "title": "OmniScreener",
            "subheader": "Universal screener",
            "stocks": "Stocks",
            "bonds": "Bonds",
            "metals": "Metals",
            "crypto": "Cryptocurrency",
            "apply": "Apply",
            "no_results": "No assets match the criteria.",
            "descriptive": "Descriptive",
            "fundamental": "Fundamental",
            "technical": "Technical",
            "news": "News",
            "etf": "ETF",
            "all": "All",
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
            "subheader": "Универсальный скринер",
            "stocks": "Акции",
            "bonds": "Облигации",
            "metals": "Металлы",
            "crypto": "Криптовалюта",
            "apply": "Применить",
            "no_results": "Нет активов по критериям.",
            "descriptive": "Описательные",
            "fundamental": "Фундаментальные",
            "technical": "Технические",
            "news": "Новости",
            "etf": "ETF",
            "all": "Все",
            "crypto_profile": "Профиль",
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
            "metals_spot_min": "Минимальная Spot Price ($)",
            "metals_spot_max": "Максимальная Spot Price ($)",
            "metals_expiry_min": "Минимальный Futures Expiry (дни)",
            "currency_rate_min": "Минимальный Exchange Rate",
            "currency_rate_max": "Максимальный Exchange Rate",
            "currency_vol_min": "Минимальный Volatility (%)"
        }
    }
    return texts[language].get(key, key)

st.title(t("title"))
st.subheader(t("subheader"))

# Кнопки выбора актива
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button(t("stocks")):
        with st.dialog(t("stocks")):
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
            if st.button(t("apply")):
                st.rerun()
with col2:
    if st.button(t("bonds")):
        with st.dialog(t("bonds")):
            yield_min = st.number_input(t("bonds_yield_min"), value=0.0)
            yield_max = st.number_input(t("bonds_yield_max"), value=float('inf'))
            duration_max = st.number_input(t("bonds_duration_max"), value=float('inf'))
            credit_min = st.number_input(t("bonds_credit_min"), value=0)
            if st.button(t("apply")):
                st.rerun()
with col3:
    if st.button(t("metals")):
        with st.dialog(t("metals")):
            spot_min = st.number_input(t("metals_spot_min"), value=0.0)
            spot_max = st.number_input(t("metals_spot_max"), value=float('inf'))
            expiry_min = st.number_input(t("metals_expiry_min"), value=0)
            if st.button(t("apply")):
                st.rerun()
with col4:
    if st.button(t("crypto")):
        with st.dialog(t("crypto")):
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
            if st.button(t("apply")):
                st.rerun()

# Поиск (упрощённый с данными из скриншотов)
if 'exchange' in locals() or 'yield_min' in locals() or 'spot_min' in locals() or 'profile' in locals():
    st.write("Searching...")
    progress_bar = st.progress(0)
    status_text = st.empty()
    results = []

    if 'exchange' in locals():  # Акции
        symbols = ['A', 'AA', 'AAA', 'AAAU', 'AACB', 'AACG', 'AACI', 'AACIU', 'AACT', 'AADR', 'AAL', 'AAM', 'AAME', 'AAMI', 'AAOI', 'AAON', 'AAP', 'AAPB', 'AAPD', 'AAPG', 'AB', 'ABC', 'ABMD', 'ABNB', 'ABR', 'ABT', 'ABTI', 'ABTX', 'AC', 'ACAD', 'ACB', 'ACCO', 'ACGL', 'ACH', 'ACHC', 'ACI', 'ACIW', 'ACLS', 'ACM', 'ACN', 'ACOR', 'ACP', 'ACRS', 'ACT', 'ADAP', 'ADBE', 'ADC', 'ADCT', 'ADGI', 'ADI', 'ADIL', 'ADM', 'ADP', 'ADPT', 'ADSK', 'ADT', 'ADTH', 'ADTN', 'ADUS', 'ADV', 'ADVM', 'ADX', 'AE', 'AEE', 'AEHR', 'AEIS', 'AEL', 'AEM', 'AEMD', 'AEOS', 'AES', 'AFG', 'AFL', 'AG', 'AGIO', 'AGL', 'AGM', 'AGNC', 'AGO', 'AGR', 'AGRO', 'AGRX', 'AGS', 'AGTC', 'AGX', 'AHCO', 'AHH', 'AI', 'AIG', 'AIHS', 'AIMC', 'AIN', 'AIR', 'AIRI', 'AIRT', 'AIZ', 'AJG', 'AKAM', 'AKBA', 'AKRO', 'AKTS', 'AL', 'ALAB', 'ALB', 'ALBO', 'ALDX', 'ALE', 'ALEC', 'ALEX', 'ALG', 'ALGN', 'ALGT', 'ALK', 'ALL', 'ALLE', 'ALLK', 'ALLO', 'ALNA', 'ALNY', 'ALOT', 'ALPA', 'ALRM', 'ALSN', 'ALT', 'ALTR', 'ALV', 'ALVR', 'ALX', 'AM', 'AMAL', 'AMAT', 'AMBA', 'AMBC', 'AMC', 'AMED', 'AMEH', 'AMG', 'AMGN', 'AMH', 'AMI', 'AMKR', 'AML', 'AMN', 'AMP', 'AMPG', 'AMR', 'AMRC', 'AMRH', 'AMRN', 'AMRX', 'AMSC', 'AMSF', 'AMT', 'AMTI', 'AMTX', 'AMWD', 'AMX', 'AMZN', 'AN', 'ANDE', 'ANGI', 'ANIK', 'ANIP', 'ANIX', 'ANNX', 'ANPC', 'ANSS', 'ANTM', 'ANY', 'AON', 'AORT', 'AP', 'APA', 'APAC', 'APDN', 'APH', 'APLD', 'APLE', 'APLS', 'APM', 'APO', 'APP', 'APPN', 'APPS', 'APRE', 'APRN', 'APRX', 'APTS', 'APTV', 'APVO', 'APWC', 'AR', 'ARAV', 'ARAY', 'ARC', 'ARCB', 'ARCH', 'ARCT', 'ARD', 'ARDX', 'ARE', 'AREC', 'ARES', 'ARGX', 'ARI', 'ARIS', 'ARKO', 'ARKR', 'ARLO', 'ARLP', 'ARM', 'ARNA', 'ARQQ', 'ARQT', 'ARR', 'ARRY', 'ARTL', 'ARVN', 'ARWR', 'ASAN', 'ASB', 'ASGN', 'ASH', 'ASIX', 'ASLE', 'ASMB', 'ASND', 'ASNS', 'ASO', 'ASPI', 'ASR', 'ASTL', 'ASTS', 'ASUR', 'ASX', 'ATA', 'ATAX', 'ATCO', 'ATEC', 'ATEN', 'ATH', 'ATHM', 'ATI', 'ATIF', 'ATKR', 'ATLC', 'ATNI', 'ATOM', 'ATR', 'ATRA', 'ATRC', 'ATRI', 'ATRO', 'ATS', 'ATUS', 'ATV', 'AVA', 'AVAV', 'AVB', 'AVD', 'AVDL', 'AVGO', 'AVGR', 'AVIR', 'AVNS', 'AVO', 'AVPT', 'AVTR', 'AVXL', 'AW', 'AWH', 'AWK', 'AWR', 'AX', 'AXDX', 'AXGN', 'AXL', 'AXNX', 'AXON', 'AXP', 'AXSM', 'AXTA', 'AY', 'AZ', 'AZN', 'AZO', 'AZPN', 'AZTA', 'B', 'BA', 'BAC', 'BAH', 'BAK', 'BALL', 'BAM', 'BANF', 'BANR', 'BAP', 'BATRA', 'BATRK', 'BBBY', 'BBIG', 'BBIO', 'BBQ', 'BBU', 'BBW', 'BBY', 'BC', 'BCAB', 'BCC', 'BCDA', 'BCML', 'BCOR', 'BCOV', 'BCPC', 'BCRX', 'BDC', 'BDN', 'BDX', 'BE', 'BEAM', 'BEAT', 'BECN', 'BELFB', 'BEN', 'BERY', 'BFAM', 'BFC', 'BFH', 'BFI', 'BFOR', 'BFS', 'BG', 'BGCP', 'BGFV', 'BGNE', 'BGS', 'BH', 'BHC', 'BHF', 'BHG', 'BHLB', 'BHP', 'BIG', 'BILL', 'BIP', 'BIPC', 'BIRD', 'BK', 'BKD', 'BKE', 'BKKT', 'BKSY', 'BL', 'BLD', 'BLDR', 'BLFS', 'BLK', 'BLMN', 'BLNK', 'BLPH', 'BLTS', 'BLUE', 'BMBL', 'BMGL', 'BMI', 'BMO', 'BMRA', 'BNGO', 'BNTX', 'BOH', 'BOIL', 'BOLT', 'BOMN', 'BOOM', 'BOOT', 'BORR', 'BOX', 'BP', 'BPOP', 'BR', 'BRBR', 'BRFS', 'BRID', 'BRO', 'BRP', 'BRSP', 'BRX', 'BSBK', 'BSIG', 'BSM', 'BSQR', 'BSW', 'BTCS', 'BTI', 'BTOG', 'BTU', 'BTZ', 'BUJA', 'BVH', 'BWXT', 'BYND', 'BZFD', 'C', 'CAAS', 'CABO', 'CADE', 'CAE', 'CAKE', 'CAL', 'CALM', 'CALX', 'CAMT', 'CAR', 'CARA', 'CARV', 'CAS', 'CASE', 'CASH', 'CASI', 'CASY', 'CAT', 'CATY', 'CB', 'CBAY', 'CBC', 'CBIO', 'CBRE', 'CBRL', 'CBSH', 'CBT', 'CBTX', 'CBUS', 'CC', 'CCAP', 'CCB', 'CCC', 'CCD', 'CCF', 'CCJ', 'CCK', 'CCL', 'CCOI', 'CCRN', 'CCS', 'CCU', 'CCZ', 'CD', 'CDAY', 'CDK', 'CDLX', 'CDNA', 'CDP', 'CDTX', 'CDW', 'CE', 'CECO', 'CEI', 'CELH', 'CENT', 'CENTA', 'CENTD', 'CEO', 'CEPU', 'CET', 'CETX', 'CF', 'CFR', 'CG', 'CGEM', 'CGNT', 'CGNX', 'CH', 'CHCT', 'CHD', 'CHEF', 'CHGG', 'CHGS', 'CHH', 'CHKP', 'CHPT', 'CHRD', 'CHRS', 'CHRW', 'CHTR', 'CHUY', 'CHWY', 'CI', 'CIA', 'CIEN', 'CIGI', 'CIM', 'CIO', 'CIR', 'CIT', 'CITZ', 'CIXX', 'CKPT', 'CL', 'CLB', 'CLF', 'CLNE', 'CLNN', 'CLOV', 'CLR', 'CLS', 'CLSK', 'CLVT', 'CLW', 'CLXT', 'CMA', 'CMAX', 'CMCO', 'CMCT', 'CMD', 'CME', 'CMG', 'CMI', 'CMPR', 'CMS', 'CNA', 'CNC', 'CNET', 'CNK', 'CNM', 'CNMD', 'CNP', 'CNSL', 'CNX', 'CO', 'COGT', 'COHR', 'COHU', 'COIN', 'COLB', 'COLM', 'COMM', 'COMP', 'COO', 'COOP', 'COP', 'COR', 'CORE', 'CORT', 'COST', 'COTY', 'COUP', 'CP', 'CPA', 'CPB', 'CPE', 'CPG', 'CPK', 'CPOP', 'CPRI', 'CPRT', 'CR', 'CRBP', 'CRBU', 'CRDF', 'CREX', 'CRI', 'CRK', 'CRL', 'CRM', 'CRNC', 'CRNT', 'CROX', 'CRS', 'CRSP', 'CRTO', 'CRUS', 'CRWD', 'CSGP', 'CSII', 'CSIQ', 'CSL', 'CSPI', 'CSS', 'CSX', 'CTAS', 'CTB', 'CTLT', 'CTMX', 'CTRA', 'CTS', 'CTSH', 'CTV', 'CTXS', 'CUBI', 'CUE', 'CUZ', 'CVBF', 'CVCO', 'CVE', 'CVET', 'CVGW', 'CVLT', 'CVNA', 'CVS', 'CVX', 'CW', 'CWAN', 'CWEN', 'CWEN.A', 'CWK', 'CXAI', 'CXM', 'CYBR', 'CYH', 'CYRX', 'CYXT', 'CZR', 'D', 'DAKT', 'DAL', 'DALN', 'DAR', 'DASH', 'DAVE', 'DB', 'DBI', 'DBRG', 'DBX', 'DC', 'DCOM', 'DCT', 'DD', 'DDD', 'DDOG', 'DE', 'DECK', 'DEI', 'DELL', 'DEN', 'DESP', 'DFIN', 'DFLI', 'DG', 'DGII', 'DGLY', 'DGX', 'DH', 'DHC', 'DHI', 'DHR', 'DIN', 'DIOD', 'DIOR', 'DIS', 'DK', 'DKNG', 'DLB', 'DLR', 'DLTR', 'DLX', 'DM', 'DMRC', 'DNLI', 'DNMR', 'DNUT', 'DOC', 'DOCN', 'DOCS', 'DOG', 'DOLE', 'DOMO', 'DORM', 'DOT', 'DOX', 'DPZ', 'DRD', 'DRH', 'DRIP', 'DRN', 'DRQ', 'DRTS', 'DS', 'DSGR', 'DSKE', 'DSLV', 'DSTX', 'DT', 'DUK', 'DUOL', 'DV', 'DVAX', 'DXC', 'DXCM', 'DXPE', 'DY', 'E', 'EA', 'EB', 'EBAY', 'EBF', 'EBIX', 'EBS', 'EBTC', 'EC', 'ECH', 'ED', 'EDIT', 'EDU', 'EDZ', 'EEFT', 'EEIQ', 'EEX', 'EFSC', 'EFX', 'EGAN', 'EGHT', 'EGOV', 'EGRX', 'EH', 'EHTH', 'EIG', 'EIGR', 'EIX', 'EL', 'ELAN', 'ELF', 'ELME', 'ELON', 'ELV', 'ELY', 'EMBC', 'EMD', 'EME', 'EMKR', 'EMLC', 'EMN', 'EMR', 'ENB', 'ENDP', 'ENPH', 'ENR', 'ENS', 'ENTA', 'ENVX', 'EOG', 'EPAC', 'EPAM', 'EPOL', 'EQ', 'EQIX', 'ERII', 'ES', 'ESAB', 'ESCA', 'ESG', 'ESGR', 'ESNT', 'ESTC', 'ET', 'ETD', 'ETHO', 'ETN', 'ETR', 'ETSY', 'EV', 'EVAV', 'EVCM', 'EVGO', 'EVH', 'EVLV', 'EVR', 'EVTC', 'EW', 'EWZ', 'EXAS', 'EXC', 'EXEL', 'EXLS', 'EXP', 'EXPD', 'EXPE', 'EXPI', 'EXPS', 'EXR', 'EXTR', 'EYE', 'EZPW', 'F', 'FANG', 'FAZE', 'FB', 'FBMS', 'FBRT', 'FCF', 'FCFS', 'FCNCA', 'FCNCO', 'FCX', 'FDP', 'FE', 'FEDU', 'FELE', 'FET', 'FFBC', 'FFIE', 'FFIN', 'FFIV', 'FGEN', 'FHN', 'FIBK', 'FICO', 'FIS', 'FISV', 'FITB', 'FIVE', 'FIVN', 'FIX', 'FIXX', 'FIZZ', 'FL', 'FLDM', 'FLGT', 'FLIC', 'FLNC', 'FLOW', 'FLR', 'FLS', 'FLT', 'FLWS', 'FLYW', 'FMNB', 'FN', 'FNB', 'FNKO', 'FNMA', 'FOLD', 'FONR', 'FORR', 'FOUR', 'FOX', 'FOXA', 'FOXF', 'FR', 'FRBA', 'FREQ', 'FRG', 'FRHC', 'FRI', 'FRPH', 'FRPT', 'FRSH', 'FSBC', 'FSBW', 'FSK', 'FSLR', 'FSLY', 'FSP', 'FSR', 'FSS', 'FSTR', 'FTAI', 'FTCH', 'FTDR', 'FTI', 'FTNT', 'FTR', 'FTS', 'FTV', 'FUL', 'FUTU', 'FWONA', 'FWONK', 'FXNC', 'G', 'GABC', 'GAMB', 'GATO', 'GBDC', 'GBL', 'GBLI', 'GBOX', 'GCBC', 'GCMG', 'GD', 'GE', 'GEF', 'GEL', 'GEO', 'GERN', 'GES', 'GEVO', 'GFF', 'GFI', 'GFL', 'GFS', 'GGB', 'GGG', 'GHL', 'GHLD', 'GHM', 'GHY', 'GI', 'GIII', 'GIL', 'GILT', 'GIPR', 'GL', 'GLDD', 'GLMD', 'GLNG', 'GLOB', 'GLP', 'GLPG', 'GLRI', 'GLYC', 'GM', 'GME', 'GMED', 'GMRE', 'GMS', 'GNAC', 'GNMK', 'GNRC', 'GNSS', 'GO', 'GOAC', 'GOEV', 'GOGL', 'GOLD', 'GOOG', 'GOOGL', 'GORO', 'GOSS', 'GOTU', 'GOVX', 'GP', 'GPOR', 'GPRE', 'GRBK', 'GRC', 'GRMN', 'GRPN', 'GRWG', 'GS', 'GSAT', 'GSHD', 'GSK', 'GSKY', 'GSX', 'GT', 'GTES', 'GTII', 'GTT', 'GTY', 'GURE', 'GV', 'GWAV', 'GWH', 'GWW', 'GXO', 'H', 'HA', 'HAE', 'HAL', 'HALO', 'HASI', 'HAWK', 'HB', 'HBCP', 'HBI', 'HBIO', 'HCA', 'HCC', 'HCKT', 'HD', 'HE', 'HEAR', 'HEES', 'HELE', 'HEP', 'HERO', 'HES', 'HEXO', 'HFWA', 'HGBL', 'HGV', 'HH', 'HHR', 'HI', 'HIBB', 'HIG', 'HII', 'HIL', 'HIMS', 'HIPO', 'HITK', 'HL', 'HLF', 'HLIO', 'HLIT', 'HLNE', 'HLT', 'HLX', 'HMN', 'HMSY', 'HNST', 'HOG', 'HOLX', 'HOMB', 'HON', 'HOOD', 'HOPE', 'HOSS', 'HOT', 'HOUR', 'HOV', 'HP', 'HPQ', 'HR', 'HRB', 'HRI', 'HROW', 'HSC', 'HSDT', 'HSIC', 'HSKA', 'HTBK', 'HTGC', 'HTH', 'HTLD', 'HTLF', 'HTZ', 'HUBB', 'HUBS', 'HUM', 'HUN', 'HUNV', 'HURC', 'HURN', 'HUSA', 'HVT', 'HWC', 'HY', 'HYFM', 'HYLN', 'HYMT', 'HYRE', 'HYZN', 'IAA', 'IAG', 'IAN', 'IBCP', 'IBEX', 'IBKR', 'IBM', 'IBOC', 'IBP', 'ICAD', 'ICFI', 'ICHR', 'ICL', 'ICLK', 'ICMB', 'ICMR', 'ICNC', 'ICPT', 'ICUI', 'IDAI', 'IDEX', 'IDN', 'IDRA', 'IDT', 'IDXX', 'IEA', 'IEP', 'IESC', 'IFRX', 'IG', 'IGC', 'IGOV', 'IGR', 'IHG', 'IIIN', 'IIIV', 'IIPR', 'ILMN', 'ILPT', 'IMAB', 'IMBI', 'IMCC', 'IMGN', 'IMH', 'IMKTA', 'IMLA', 'IMMR', 'IMNM', 'IMNN', 'IMPL', 'IMTX', 'IMUX', 'IMVT', 'INAB', 'INBK', 'INBX', 'INCY', 'INDA', 'INDI', 'INDT', 'INFI', 'INFO', 'INMB', 'INM', 'INN', 'INO', 'INOD', 'INOV', 'INS', 'INSE', 'INSG', 'INSM', 'INST', 'INSW', 'INTA', 'INTC', 'INTU', 'INVA', 'INVE', 'INVH', 'INVO', 'INVZ', 'IO', 'IONQ', 'IOSP', 'IPAR', 'IPDN', 'IPG', 'IPGP', 'IPHA', 'IPI', 'IPOD', 'IPOE', 'IPOF', 'IPSC', 'IPWR', 'IR', 'IRBT', 'IRDM', 'IREN', 'IRMD', 'IRTC', 'IRWD', 'ISBC', 'ISDR', 'ISRG', 'ISS', 'ISTB', 'IT', 'ITCI', 'ITIC', 'ITOS', 'ITT', 'ITUB', 'IUSB', 'IVAC', 'IVR', 'IVT', 'IVZ', 'IX', 'J', 'JACK', 'JAGX', 'JAMF', 'JAZZ', 'JBGS', 'JBHT', 'JBL', 'JBLU', 'JBT', 'JCE', 'JCI', 'JCOM', 'JD', 'JEF', 'JFIN', 'JILL', 'JJS', 'JKHY', 'JKS', 'JLI', 'JNJ', 'JNK', 'JOAN', 'JOBY', 'JOE', 'JOUT', 'JP', 'JPM', 'JRVR', 'JSPR', 'JT', 'JUPW', 'JVA', 'JWEL', 'JWN', 'K', 'KALA', 'KALU', 'KAMN', 'KAR', 'KAVL', 'KB', 'KBH', 'KBR', 'KDP', 'KE', 'KELYA', 'KELYB', 'KEM', 'KEN', 'KEP', 'KEX', 'KEY', 'KEYS', 'KFRC', 'KFS', 'KGC', 'KIDS', 'KIM', 'KIND', 'KINS', 'KIRK', 'KITT', 'KIY', 'KL', 'KLAC', 'KLA', 'KLIC', 'KLTO', 'KLXE', 'KMB', 'KMDA', 'KMI', 'KMPR', 'KMT', 'KN', 'KNBE', 'KNDI', 'KNOP', 'KNSA', 'KNSL', 'KO', 'KOD', 'KODK', 'KOP', 'KOPN', 'KOSS', 'KPTI', 'KR', 'KRA', 'KRMD', 'KROS', 'KRP', 'KRT', 'KRYS', 'KS', 'KT', 'KTB', 'KTEC', 'KTRA', 'KTTA', 'KULR', 'KVHI', 'KW', 'KWR', 'KYMR', 'L', 'LAD', 'LAKE', 'LAMR', 'LANC', 'LAND', 'LAUR', 'LAW', 'LAZR', 'LB', 'LBAI', 'LBC', 'LBTYA', 'LBTYB', 'LBTYK', 'LC', 'LCID', 'LCNB', 'LCUT', 'LDOS', 'LE', 'LEA', 'LECO', 'LEE', 'LEGH', 'LEN', 'LESL', 'LEU', 'LEV', 'LFST', 'LGFY', 'LGHL', 'LGND', 'LH', 'LHC', 'LHCG', 'LHDX', 'LHX', 'LI', 'LIDR', 'LIFE', 'LII', 'LILAK', 'LILA', 'LIN', 'LIND', 'LITE', 'LIVN', 'LKFN', 'LLY', 'LMND', 'LMNR', 'LMT', 'LNC', 'LND', 'LNDC', 'LNG', 'LNTH', 'LOAN', 'LOCO', 'LOGI', 'LOK', 'LOOP', 'LORL', 'LOV', 'LOW', 'LPG', 'LPI', 'LPSN', 'LQDA', 'LQDT', 'LRN', 'LSCC', 'LSXMA', 'LSXMK', 'LTBR', 'LTRPA', 'LTRPB', 'LTRY', 'LU', 'LULU', 'LUNA', 'LUNG', 'LUV', 'LUXA', 'LVGO', 'LVS', 'LW', 'LX', 'LYFT', 'LYLT', 'LYTS', 'LYV', 'M', 'MA', 'MAC', 'MAIN', 'MANH', 'MANU', 'MAR', 'MARA', 'MARK', 'MAS', 'MASI', 'MAT', 'MATW', 'MATX', 'MAXR', 'MBI', 'MBIN', 'MBIO', 'MBOT', 'MBUU', 'MC', 'MCB', 'MCBC', 'MCBS', 'MCFT', 'MCGC', 'MCHP', 'MCHX', 'MCIA', 'MCN', 'MCW', 'MD', 'MDB', 'MDC', 'MDGL', 'MDLZ', 'MDNA', 'MDT', 'MDXG', 'MEC', 'MED', 'MEDP', 'MEG', 'MEI', 'MELI', 'MEOH', 'MET', 'META', 'METC', 'MFA', 'MFAN', 'MFC', 'MFM', 'MFMI', 'MFS', 'MGA', 'MGIC', 'MGLD', 'MGNI', 'MGNX', 'MGP', 'MGPI', 'MGRC', 'MGY', 'MHK', 'MICT', 'MIDD', 'MIK', 'MILE', 'MIME', 'MIND', 'MIR', 'MIRM', 'MKC', 'MKD', 'MLI', 'MLNK', 'MLR', 'MLVF', 'MMC', 'MMM', 'MMP', 'MNMD', 'MNSO', 'MNTN', 'MNTS', 'MO', 'MOBL', 'MOD', 'MODN', 'MODV', 'MOFG', 'MOGO', 'MOM', 'MON', 'MORN', 'MOS', 'MOV', 'MP', 'MPW', 'MQ', 'MRAM', 'MRBK', 'MRIN', 'MRK', 'MRKR', 'MRLN', 'MRNA', 'MRNS', 'MRSN', 'MRUS', 'MRVL', 'MS', 'MSA', 'MSB', 'MSC', 'MSTR', 'MT', 'MTB', 'MTCH', 'MTD', 'MTDR', 'MTEM', 'MTG', 'MTH', 'MTN', 'MTOR', 'MTRN', 'MTW', 'MTX', 'MTZ', 'MUA', 'MUDS', 'MUFJ', 'MUR', 'MUSA', 'MUX', 'MVBF', 'MVIS', 'MVO', 'MWA', 'MX', 'MXCT', 'MYGN', 'MYOV', 'NABL', 'NAII', 'NARI', 'NAT', 'NAUT', 'NAV', 'NAVI', 'NBHC', 'NBIX', 'NBR', 'NBSE', 'NBRV', 'NC', 'NCNA', 'NCR', 'NCSM', 'NDAQ', 'NDLS', 'NDSN', 'NE', 'NEA', 'NEAR', 'NEE', 'NEM', 'NEO', 'NEON', 'NEP', 'NESR', 'NET', 'NEU', 'NEW', 'NEWR', 'NEX', 'NEXT', 'NFBK', 'NFLX', 'NFYS', 'NG', 'NGD', 'NGM', 'NH', 'NHAI', 'NHF', 'NHI', 'NI', 'NIKE', 'NIO', 'NKE', 'NKLA', 'NKTR', 'NKTX', 'NL', 'NLST', 'NLS', 'NLSN', 'NLY', 'NM', 'NMFC', 'NMG', 'NMGS', 'NMHI', 'NMIH', 'NMM', 'NMR', 'NMRK', 'NNBR', 'NNDM', 'NNI', 'NNN', 'NOA', 'NOC', 'NOG', 'NOMD', 'NOTV', 'NOV', 'NOVA', 'NOVT', 'NOW', 'NP', 'NPK', 'NPO', 'NR', 'NRBO', 'NRDS', 'NRDY', 'NRGX', 'NRIX', 'NRP', 'NRUC', 'NRZ', 'NS', 'NSA', 'NSC', 'NSR', 'NSTG', 'NTAP', 'NTB', 'NTCT', 'NTCO', 'NTES', 'NTGR', 'NTIC', 'NTLA', 'NTNX', 'NU', 'NUAN', 'NURO', 'NUS', 'NUVA', 'NVAX', 'NVCR', 'NVDA', 'NVEE', 'NVGS', 'NVIV', 'NVMI', 'NVRO', 'NVR', 'NWBI', 'NWE', 'NWG', 'NWL', 'NWN', 'NX', 'NXGN', 'NXPI', 'NXRT', 'NYCB', 'NYMT', 'O', 'OC', 'OCDX', 'OCFC', 'OCGN', 'OCN', 'OCSL', 'OCUL', 'OCUP', 'ODC', 'ODFL', 'ODP', 'OEC', 'OFC', 'OFG', 'OGI', 'OGN', 'OGS', 'OHI', 'OI', 'OKTA', 'OLLI', 'OLN', 'OLP', 'OM', 'OMCL', 'OMER', 'OMEX', 'OMI', 'OMP', 'ON', 'ONB', 'ONCR', 'ONCT', 'ONEM', 'ONMD', 'ONTO', 'ONVO', 'OPAD', 'OPBK', 'OPEN', 'OPGN', 'OPI', 'OPK', 'OPNT', 'OPRA', 'OPRT', 'OPRX', 'OPTT', 'ORAN', 'ORBC', 'ORC', 'ORCC', 'ORCL', 'ORGN', 'ORI', 'ORIC', 'ORLY', 'ORMP', 'ORN', 'ORPH', 'OSCR', 'OSG', 'OSH', 'OSIS', 'OSPN', 'OSS', 'OST', 'OSUR', 'OTEX', 'OTIC', 'OTLK', 'OTRK', 'OTTR', 'OUST', 'OUT', 'OVBC', 'OVID', 'OVLY', 'OVV', 'OXM', 'OXY', 'OZK', 'P', 'PAAS', 'PACB', 'PACK', 'PACW', 'PAHC', 'PAM', 'PANL', 'PANW', 'PAR', 'PARR', 'PASG', 'PAVM', 'PAX', 'PAYA', 'PAYC', 'PAYO', 'PAYS', 'PAYX', 'PB', 'PBCT', 'PBF', 'PBH', 'PBI', 'PBPB', 'PBTS', 'PCAR', 'PCG', 'PCOR', 'PCSB', 'PCT', 'PCTI', 'PCTY', 'PD', 'PDCE', 'PDD', 'PEAK', 'PEBO', 'PECO', 'PEG', 'PEN', 'PENN', 'PEP', 'PERI', 'PFBC', 'PFG', 'PFGC', 'PFHD', 'PFIE', 'PFIS', 'PFIN', 'PFMT', 'PG', 'PGC', 'PGEN', 'PGNY', 'PH', 'PHAT', 'PHG', 'PHM', 'PI', 'PINC', 'PINS', 'PIPR', 'PIRS', 'PJT', 'PK', 'PKBK', 'PKI', 'PKOH', 'PKW', 'PL', 'PLAB', 'PLAN', 'PLAT', 'PLBC', 'PLBY', 'PLCE', 'PLMR', 'PLNT', 'PLRX', 'PLSE', 'PLTR', 'PLUG', 'PLUS', 'PLX', 'PM', 'PMCB', 'PMD', 'PMGM', 'PMT', 'PMTS', 'PMVP', 'PN', 'PNC', 'PNFP', 'PNG', 'PNNT', 'PNR', 'PNW', 'PODD', 'POLY', 'POM', 'POW', 'POWI', 'PPBI', 'PPC', 'PPG', 'PPIH', 'PPL', 'PPSI', 'PPT', 'PR', 'PRA', 'PRAX', 'PRCH', 'PRCT', 'PRDO', 'PRFT', 'PRG', 'PRGO', 'PRI', 'PRIM', 'PRK', 'PRME', 'PRO', 'PROF', 'PROG', 'PROK', 'PROM', 'PRPH', 'PRQR', 'PRSR', 'PRTA', 'PRTH', 'PRTK', 'PRTS', 'PRTY', 'PRVA', 'PRVB', 'PRZO', 'PS', 'PSB', 'PSFE', 'PSMT', 'PSN', 'PSO', 'PSTG', 'PSTX', 'PTC', 'PTCT', 'PTEN', 'PTGX', 'PTLO', 'PTMN', 'PTNR', 'PTON', 'PTPI', 'PTR', 'PTSI', 'PTW', 'PUBM', 'PUK', 'PULM', 'PUW', 'PVBC', 'PVH', 'PW', 'PWP', 'PWSC', 'PX', 'PXD', 'PYCR', 'PYPL', 'PYXS', 'QCOM', 'QCRH', 'QDEL', 'QFIN', 'QLYS', 'QMCO', 'QNGY', 'QNRX', 'QS', 'QTNT', 'QUAD', 'QUIK', 'QUMU', 'QURE', 'R', 'RACE', 'RAIL', 'RAMP', 'RAND', 'RAPT', 'RARE', 'RAVE', 'RAVI', 'RBA', 'RBB', 'RBBN', 'RBC', 'RBCAA', 'RBCN', 'RBKB', 'RBLX', 'RBNC', 'RCAT', 'RCI', 'RCII', 'RCON', 'RCUS', 'RCV', 'RCVI', 'RDN', 'RDNT', 'RDUS', 'RDW', 'RE', 'REAL', 'REAX', 'REED', 'REEF', 'REEMF', 'REKR', 'RELL', 'RELY', 'REPH', 'RES', 'RETO', 'REUN', 'REV', 'REXR', 'REYN', 'REZI', 'RF', 'RFL', 'RFP', 'RGA', 'RGEN', 'RGLS', 'RGNX', 'RGTI', 'RH', 'RHE', 'RHI', 'RHP', 'RIBT', 'RICK', 'RIDE', 'RIG', 'RIGL', 'RIO', 'RIVN', 'RKLB', 'RLAY', 'RLGT', 'RLJ', 'RLMD', 'RLX', 'RMBS', 'RMNI', 'RMR', 'RNAC', 'RNG', 'RNR', 'RNST', 'RNWK', 'ROAD', 'ROCK', 'ROG', 'ROIC', 'ROKU', 'ROLL', 'ROOT', 'ROST', 'ROVR', 'RPAY', 'RPD', 'RPM', 'RPRX', 'RPXC', 'RRBI', 'RRGB', 'RRR', 'RS', 'RSG', 'RSKD', 'RSLS', 'RSVA', 'RTLR', 'RTX', 'RUBY', 'RUN', 'RUSHA', 'RUSHB', 'RUTH', 'RVNC', 'RVSB', 'RVTY', 'RWAY', 'RWJ', 'RXDX', 'RXN', 'RY', 'RYAM', 'RYAN', 'RYI', 'RZB', 'S', 'SA', 'SAFX', 'SAH', 'SAIA', 'SAIC', 'SAL', 'SALM', 'SAM', 'SANM', 'SAP', 'SAR', 'SASR', 'SATL', 'SATS', 'SAVA', 'SAVE', 'SB', 'SBAC', 'SBCF', 'SBGI', 'SBH', 'SBNY', 'SBS', 'SBSI', 'SBSW', 'SC', 'SCB', 'SCCO', 'SCHD', 'SCHW', 'SCI', 'SCL', 'SCM', 'SCOR', 'SCPL', 'SCSC', 'SCU', 'SCVL', 'SCWX', 'SD', 'SDC', 'SDG', 'SDH', 'SDI', 'SDL', 'SDM', 'SDP', 'SDR', 'SDS', 'SDT', 'SDX', 'SDY', 'SE', 'SEA', 'SEAC', 'SEAS', 'SEB', 'SEC', 'SECO', 'SEDG', 'SEE', 'SEED', 'SEEL', 'SEER', 'SEIC', 'SELB', 'SELF', 'SEM', 'SENEA', 'SENEB', 'SENS', 'SEP', 'SERV', 'SES', 'SF', 'SFBS', 'SFE', 'SFIX', 'SFM', 'SFNC', 'SFR', 'SFS', 'SFT', 'SFUN', 'SG', 'SGEN', 'SGH', 'SGHL', 'SGI', 'SGMO', 'SGMS', 'SGOC', 'SGRY', 'SGTX', 'SHAK', 'SHBI', 'SHC', 'SHEN', 'SHG', 'SHI', 'SHIP', 'SHLS', 'SHO', 'SHOO', 'SHOP', 'SHOT', 'SHPW', 'SHW', 'SI', 'SID', 'SIEB', 'SIEN', 'SIFY', 'SIG', 'SIGA', 'SIGI', 'SILC', 'SILI', 'SIMO', 'SINA', 'SINO', 'SINT', 'SIOX', 'SIRI', 'SITE', 'SITM', 'SIVB', 'SIX', 'SJR', 'SKM', 'SKT', 'SKX', 'SKY', 'SKYS', 'SLAB', 'SLB', 'SLCA', 'SLCR', 'SLCT', 'SLDB', 'SLDP', 'SLG', 'SLGL', 'SLGN', 'SLM', 'SLN', 'SLNO', 'SLP', 'SLQT', 'SLRC', 'SLRX', 'SLS', 'SLVO', 'SM', 'SMAR', 'SMCI', 'SMCP', 'SMCW', 'SMED', 'SMG', 'SMHI', 'SMI', 'SMIT', 'SMLP', 'SMM', 'SMMT', 'SMP', 'SMPL', 'SMSI', 'SMTC', 'SMTX', 'SMYD', 'SN', 'SNA', 'SNAP', 'SNBR', 'SNC', 'SNCR', 'SND', 'SNDE', 'SNDX', 'SNE', 'SNES', 'SNEX', 'SNMP', 'SNN', 'SNOA', 'SNOW', 'SNP', 'SNPO', 'SNPS', 'SNR', 'SNRH', 'SNSS', 'SNV', 'SNX', 'SO', 'SOFI', 'SOGO', 'SOHO', 'SOI', 'SOJA', 'SOJB', 'SOL', 'SOLO', 'SON', 'SONA', 'SONC', 'SOND', 'SONM', 'SONN', 'SONO', 'SONS', 'SOPH', 'SOR', 'SORL', 'SOS', 'SOTK', 'SOVO', 'SP', 'SPB', 'SPCB', 'SPCE', 'SPCM', 'SPCMU', 'SPFI', 'SPG', 'SPH', 'SPHS', 'SPI', 'SPK', 'SPKE', 'SPLK', 'SPN', 'SPOK', 'SPOT', 'SPPI', 'SPR', 'SPRB', 'SPSC', 'SPT', 'SPTN', 'SPWH', 'SPWR', 'SPXC', 'SPXX', 'SQ', 'SQM', 'SQNS', 'SQQQ', 'SR', 'SRAX', 'SRC', 'SRCE', 'SRCL', 'SRDX', 'SRE', 'SREV', 'SRF', 'SRG', 'SRI', 'SRL', 'SRLP', 'SRNE', 'SRNA', 'SRPT', 'SRRA', 'SRS', 'SRT', 'SRTS', 'SRZN', 'SSAA', 'SSB', 'SSBI', 'SSC', 'SSD', 'SSE', 'SSF', 'SSG', 'SSH', 'SSI', 'SSL', 'SSNC', 'SSNT', 'SSP', 'SSRM', 'SST', 'SSTI', 'SSTK', 'SSU', 'SSW', 'SSY', 'ST', 'STAA', 'STAF', 'STAG', 'STAY', 'STBA', 'STC', 'STCN', 'STE', 'STEP', 'STG', 'STGW', 'STI', 'STIM', 'STK', 'STL', 'STLA', 'STM', 'STN', 'STND', 'STNE', 'STON', 'STOR', 'STOT', 'STPF', 'STRA', 'STRL', 'STRO', 'STRP', 'STRS', 'STRT', 'STT', 'STTK', 'STU', 'STUM', 'STX', 'STXS', 'STZ', 'SUI', 'SUM', 'SUN', 'SUNW', 'SUP', 'SUPN', 'SURF', 'SURG', 'SUSA', 'SUSC', 'SUSB', 'SUSQ', 'SUTR', 'SUV', 'SUZ', 'SV', 'SVA', 'SVB', 'SVC', 'SVD', 'SVE', 'SVFD', 'SVFDU', 'SVFA', 'SVFAU', 'SVG', 'SVND', 'SVP', 'SVRA', 'SVT', 'SVVC', 'SWAV', 'SWBI', 'SWCH', 'SWI', 'SWIM', 'SWK', 'SWKS', 'SWM', 'SWN', 'SWP', 'SWSS', 'SWT', 'SWTX', 'SWX', 'SWZ', 'SX', 'SXC', 'SXE', 'SXTC', 'SY', 'SYBT', 'SYBX', 'SYF', 'SYK', 'SYKE', 'SYMM', 'SYN', 'SYNC', 'SYNH', 'SYNL', 'SYNX', 'SYPR', 'SYRS', 'SYT', 'SYX', 'SYY', 'SZC', 'T', 'TA', 'TAC', 'TACO', 'TACT', 'TAIL', 'TAL', 'TALO', 'TAN', 'TANH', 'TANN', 'TAP', 'TARA', 'TARO', 'TARS', 'TAT', 'TATT', 'TAYD', 'TBCP', 'TBI', 'TBK', 'TBLD', 'TBLT', 'TBNK', 'TC', 'TCBI', 'TCBK', 'TCCO', 'TCDA', 'TCEHY', 'TCFC', 'TCI', 'TCMD', 'TCO', 'TCP', 'TCPC', 'TCRR', 'TCRT', 'TCS', 'TCX', 'TD', 'TDC', 'TDF', 'TDG', 'TDOC', 'TDS', 'TDUP', 'TDW', 'TDY', 'TE', 'TEAM', 'TECH', 'TECK', 'TECL', 'TEDU', 'TEF', 'TEI', 'TEL', 'TELL', 'TEN', 'TENB', 'TENX', '
