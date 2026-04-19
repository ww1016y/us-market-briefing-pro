from datetime import timedelta, timezone

KST = timezone(timedelta(hours=9))

INDICES = [
    ("^GSPC", "S&P 500", "S&P 500"),
    ("^IXIC", "NASDAQ", "나스닥"),
    ("^DJI", "Dow Jones", "다우존스"),
    ("^VIX", "VIX", "변동성지수(VIX)"),
]

SECTOR_TICKERS = {
    "IT": ("💻 정보기술 (IT)", [
        ("NVDA","NVIDIA","엔비디아"), ("AAPL","Apple","애플"), ("MSFT","Microsoft","마이크로소프트"), 
        ("AVGO","Broadcom","브로드컴"), ("AMD","AMD","AMD"), ("INTU","Intuit","인튜이트"),
        ("CRM","Salesforce","세일즈포스"), ("NOW","ServiceNow","서비스나우"), ("ADBE","Adobe","어도비"),
        ("ORCL","Oracle","오라클"), ("PLTR","Palantir","팔란티어")
    ]),
    "COMM": ("📡 커뮤니케이션 서비스", [
        ("GOOGL","Alphabet","알파벳"), ("META","Meta","메타"), ("NFLX","Netflix","넷플릭스"), 
        ("DIS","Disney","디즈니"), ("TMUS","T-Mobile","T모바일")
    ]),
    "DISC": ("🛍️ 임의소비재", [
        ("AMZN","Amazon","아마존"), ("TSLA","Tesla","테슬라"), ("HD","Home Depot","홈디포"), 
        ("MCD","McDonald's","맥도날드"), ("NKE","Nike","나이키")
    ]),
    "HLTH": ("🏥 헬스케어", [
        ("UNH","UnitedHealth","유나이티드헬스"), ("LLY","Eli Lilly","일라이릴리"),
        ("JNJ","J&J","존슨앤존슨"), ("ABBV","AbbVie","애브비"), ("MRK","Merck","머크")
    ]),
    "FIN": ("🏦 금융", [
        ("JPM","JPMorgan","JP모건"), ("BAC","Bank of America","뱅크오브아메리카"),
        ("GS","Goldman Sachs","골드만삭스"), ("V","Visa","비자"), ("MA","Mastercard","마스터카드")
    ]),
    "ENRG": ("⛽ 에너지", [
        ("XOM","ExxonMobil","엑슨모빌"), ("CVX","Chevron","셰브론"), ("COP","ConocoPhillips","코노코필립스")
    ]),
}

THEMES = {
    "AI_LLM": ("🤖 AI / 대형언어모델", ["NVDA", "MSFT", "META", "GOOGL", "AMZN", "PLTR", "SMCI"]),
    "NUCLEAR": ("☢️ 원자력 / SMR", ["CEG", "VST", "CCJ", "SMR", "OKLO"]),
    "OBESITY": ("💊 비만치료 / GLP-1", ["LLY", "NVO", "VKTX", "HIMS"]),
    "CRYPTO": ("₿ 가상자산", ["COIN", "MSTR", "HOOD", "MARA", "RIOT"]),
}
