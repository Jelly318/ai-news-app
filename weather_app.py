import streamlit as st
import requests
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

# ---- キャッシュ付きAPI取得関数 ----
@st.cache_data(ttl=600)  # 10分間キャッシュ
def fetch_weather(city_en: str, api_key: str) -> dict:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_en}&appid={api_key}&units=metric&lang=ja"
    return requests.get(url, timeout=10).json()

@st.cache_data(ttl=600)  # 10分間キャッシュ
def fetch_forecast(city_en: str, api_key: str) -> dict:
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_en}&appid={api_key}&units=metric&lang=ja&cnt=40"
    return requests.get(url, timeout=10).json()

# ---- ページ設定 ----
st.set_page_config(
    page_title="天気アプリ",
    page_icon="⛅",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_KEY = os.getenv("OPENWEATHER_API_KEY")

CITIES = {
    "東京": "Tokyo",
    "札幌": "Sapporo",
    "福岡": "Fukuoka",
    "大阪": "Osaka",
    "名古屋": "Nagoya",
    "仙台": "Sendai",
    "広島": "Hiroshima",
    "那覇": "Naha",
    "帯広": "Obihiro",
}

# OpenWeatherアイコンコード → 絵文字マッピング
ICON_MAP = {
    "01d": "☀️", "01n": "☀️",          # 快晴（夜も太陽）
    "02d": "🌤️", "02n": "🌤️",          # 少し雲
    "03d": "⛅", "03n": "⛅",           # 曇り
    "04d": "☁️", "04n": "☁️",           # 厚い雲
    "09d": "🌧️", "09n": "🌧️",           # にわか雨
    "10d": "🌦️", "10n": "🌦️",           # 雨
    "11d": "⛈️", "11n": "⛈️",           # 雷雨
    "13d": "❄️", "13n": "❄️",           # 雪
    "50d": "🌫️", "50n": "🌫️",           # 霧
}

def calc_life_index(temp: float, humidity: float, wind: float, desc: str) -> list:
    results = []

    # 外ラン指数
    run_score = 5
    if temp < 0: run_score -= 3
    elif temp < 5: run_score -= 2
    elif temp > 30: run_score -= 2
    elif temp > 35: run_score -= 3
    if humidity > 80: run_score -= 1
    if wind > 10: run_score -= 1
    if any(w in desc for w in ["雨", "雪", "雷"]): run_score -= 2
    run_score = max(1, min(5, run_score))
    run_labels = {5:"最高のランニング日和！", 4:"快適に走れます", 3:"まあまあ走れます", 2:"やや厳しいです", 1:"今日は室内トレがおすすめ"}
    results.append(("🏃", "外ラン指数", run_score, run_labels[run_score]))

    # サウナ外気浴指数
    sauna_score = 5
    if temp > 30: sauna_score -= 2
    elif temp > 25: sauna_score -= 1
    if wind > 15: sauna_score -= 2
    elif wind > 8: sauna_score -= 1
    if "雨" in desc: sauna_score -= 1
    if "雷" in desc: sauna_score -= 3
    sauna_score = max(1, min(5, sauna_score))
    sauna_labels = {5:"外気浴が最高！ととのえます", 4:"良いコンディションです", 3:"まずまずです", 2:"ちょっと厳しいかも", 1:"今日は室内サウナで"}
    results.append(("🧖", "サウナ外気浴指数", sauna_score, sauna_labels[sauna_score]))

    # 路面凍結指数
    if temp <= -5: freeze_score = 5
    elif temp <= 0: freeze_score = 4
    elif temp <= 3: freeze_score = 3
    elif temp <= 7: freeze_score = 2
    else: freeze_score = 1
    freeze_labels = {1:"問題なし", 2:"念のため注意", 3:"滑りやすい箇所あり", 4:"かなり危険！慎重に", 5:"超危険！外出注意"}
    results.append(("🧊", "路面凍結指数", freeze_score, freeze_labels[freeze_score]))

    # 洗濯指数
    wash_score = 5
    if humidity > 85: wash_score -= 3
    elif humidity > 70: wash_score -= 2
    elif humidity > 60: wash_score -= 1
    if wind < 2: wash_score -= 1
    elif wind > 5: wash_score += 1
    if any(w in desc for w in ["雨", "雪"]): wash_score -= 3
    if "曇" in desc: wash_score -= 1
    wash_score = max(1, min(5, wash_score))
    wash_labels = {5:"完璧な洗濯日和！", 4:"よく乾きます", 3:"午後から乾きそう", 2:"乾きにくいです", 1:"室内干し推奨"}
    results.append(("👕", "洗濯指数", wash_score, wash_labels[wash_score]))

    return results

def get_weather_icon_url(icon_code: str) -> str:
    return ICON_MAP.get(icon_code, "🌤️")

# ---- カスタムCSS ----
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700&family=Raleway:wght@300;600;800&display=swap');

/* ===== GLOBAL RESET ===== */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    font-family: 'Noto Sans JP', sans-serif;
    background: transparent !important;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(
        180deg,
        #e8f4fd 0%,
        #c5dff7 15%,
        #a8cce8 30%,
        #8db8d6 45%,
        #b5d4a0 60%,
        #8eb87a 75%,
        #6fa355 90%,
        #5a8a42 100%
    ) !important;
    min-height: 100vh;
    position: relative;
    overflow-x: hidden;
}

/* Sky clouds effect */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 55vh;
    background:
        radial-gradient(ellipse 300px 120px at 20% 30%, rgba(255,255,255,0.7) 0%, transparent 70%),
        radial-gradient(ellipse 200px 80px at 50% 20%, rgba(255,255,255,0.5) 0%, transparent 70%),
        radial-gradient(ellipse 250px 100px at 75% 35%, rgba(255,255,255,0.6) 0%, transparent 70%),
        radial-gradient(ellipse 180px 70px at 35% 45%, rgba(255,255,255,0.4) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

/* Rolling hills silhouette */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    bottom: 0; left: 0; right: 0;
    height: 40vh;
    background:
        radial-gradient(ellipse 60% 50% at 20% 100%, #4a7c3a 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 60% 100%, #5a8c45 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 90% 100%, #3d6b30 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stMain"], .main .block-container {
    position: relative;
    z-index: 1;
}

/* Streamlitデフォルトの枠を消す */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] > div {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.block-container {
    max-width: 960px !important;
    padding: 2rem 2rem 4rem !important;
}

/* ===== HEADER ===== */
.app-header {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.app-title {
    font-family: 'Raleway', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: #fff;
    text-shadow: 0 2px 12px rgba(0,0,0,0.25);
    letter-spacing: 0.05em;
    margin: 0;
}

/* ===== GLASS CARD ===== */
.glass-card {
    background: rgba(255, 255, 255, 0.55);
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.75);
    border-radius: 24px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(80,130,60,0.15), 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem;
}

/* タブコンテンツ：枠なし・自然に流れる */
div[data-testid="stTabsContent"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 1.5rem 0 0 0 !important;
    margin-top: 0 !important;
}

/* タブパネル内の余白をリセット */
[data-testid="stTabsContent"] {
    padding-top: 1.5rem !important;
}
[data-testid="stTabsContent"] > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
/* stVerticalBlock の余分な上マージン除去 */
[data-testid="stTabsContent"] [data-testid="stVerticalBlock"] > div:first-child {
    margin-top: 0 !important;
}
/* selectbox の上の空白 */
[data-testid="stTabsContent"] [data-testid="stSelectbox"]:first-child,
[data-testid="stTabsContent"] [data-testid="stWidgetLabel"]:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* ===== TABS ===== */
[data-testid="stTabs"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 0 1rem !important;
}

[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.45) !important;
    backdrop-filter: blur(12px);
    border-radius: 50px !important;
    padding: 6px !important;
    border: 1px solid rgba(255,255,255,0.7) !important;
    width: fit-content;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

[data-testid="stTabs"] [data-baseweb="tab-list"] > div {
    gap: 4px;
    border-bottom: none !important;
}

[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-radius: 40px !important;
    padding: 8px 22px !important;
    font-weight: 500;
    font-size: 0.9rem;
    color: #4a6741 !important;
    transition: all 0.25s ease;
}

[data-testid="stTabs"] [aria-selected="true"] {
    background: rgba(255,255,255,0.9) !important;
    color: #2d5a20 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    display: none !important;
}

/* ===== SELECT BOX ===== */
[data-testid="stSelectbox"] label {
    font-size: 0.9rem;
    color: #3a5a2f;
    font-weight: 500;
    margin-bottom: 6px;
}

[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.8) !important;
    border: 1.5px solid rgba(255,255,255,0.9) !important;
    border-radius: 14px !important;
    font-size: 1rem;
    color: #2d4a25 !important;
    backdrop-filter: blur(8px);
}

/* ===== SEARCH BUTTON ===== */
[data-testid="stButton"] button {
    width: 100%;
    background: linear-gradient(135deg, #f5c842 0%, #e8a800 100%) !important;
    color: #4a3200 !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.75rem 2rem !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    font-family: 'Noto Sans JP', sans-serif !important;
    letter-spacing: 0.08em;
    box-shadow: 0 4px 15px rgba(229,168,0,0.4), 0 1px 3px rgba(0,0,0,0.1) !important;
    transition: all 0.2s ease !important;
    cursor: pointer;
}

[data-testid="stButton"] button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(229,168,0,0.55), 0 2px 6px rgba(0,0,0,0.12) !important;
    background: linear-gradient(135deg, #fad44a 0%, #f0b800 100%) !important;
}

[data-testid="stButton"] button:active {
    transform: translateY(0);
}

/* ===== WEATHER RESULT CARD ===== */
.weather-result {
    background: transparent;
    border: none;
    padding: 0.5rem 0;
    margin-top: 0.5rem;
}

.weather-main {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}

.weather-icon-big { font-size: 4rem; line-height: 1; }

.weather-temp {
    font-family: 'Raleway', sans-serif;
    font-size: 3.5rem;
    font-weight: 800;
    color: #2d5a20;
    line-height: 1;
}

.weather-city {
    font-size: 1.1rem;
    color: #5a7a50;
    font-weight: 500;
    margin-top: 4px;
}

.weather-desc {
    font-size: 0.95rem;
    color: #6a8a60;
}

/* ===== METRIC CARDS ===== */
.metric-row {
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    margin-top: 1rem;
}

.metric-card {
    flex: 1;
    min-width: 120px;
    background: rgba(255,255,255,0.55);
    border: 1px solid rgba(255,255,255,0.8);
    border-radius: 16px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.metric-card .metric-icon { font-size: 1.6rem; margin-bottom: 4px; }
.metric-card .metric-value {
    font-family: 'Raleway', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #2d5a20;
    line-height: 1.1;
}
.metric-card .metric-label {
    font-size: 0.75rem;
    color: #7a9a70;
    margin-top: 2px;
    font-weight: 500;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ===== COMPARISON TABLE ===== */
.compare-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.8);
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(60,100,40,0.12);
    margin-top: 1rem;
    font-family: 'Noto Sans JP', sans-serif;
}
.compare-table th {
    background: rgba(220,240,210,0.75);
    color: #3a5a2f;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 13px 16px;
    text-align: left;
    border-bottom: 1.5px solid rgba(180,210,160,0.5);
}
.compare-table td {
    padding: 12px 16px;
    font-size: 0.95rem;
    color: #2d4a25;
    border-bottom: 1px solid rgba(180,210,160,0.25);
    vertical-align: middle;
    white-space: nowrap;
}
.compare-table tr:last-child td { border-bottom: none; }
.compare-table tr:hover td { background: rgba(255,255,255,0.5); }
.city-cell { font-weight: 600; font-size: 1rem; }
.temp-val {
    font-family: 'Raleway', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    color: #2d5a20;
}
.hum-wrap { display: flex; align-items: center; gap: 8px; }
.hum-bar { width: 60px; height: 6px; background: rgba(180,210,160,0.3); border-radius: 3px; overflow: hidden; }
.hum-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, #7ec860, #4a9a30); }
.sub-row td { padding: 4px 16px 14px !important; border-bottom: 1px solid rgba(180,210,160,0.25); }
.compare-table tr.sub-row:last-child td { border-bottom: none; }
.sub-weather {
    font-size: 0.88rem;
    color: #2d5a20;
    font-weight: 500;
    margin-right: 20px;
    background: rgba(180,220,160,0.3);
    padding: 2px 10px;
    border-radius: 20px;
}
.sub-wind {
    font-size: 0.88rem;
    color: #2d5a20;
    font-weight: 500;
    background: rgba(180,220,160,0.3);
    padding: 2px 10px;
    border-radius: 20px;
}

/* ===== FORECAST CARDS ===== */
.forecast-section { margin-top: 1.5rem; }
.forecast-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #5a7a50;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}
.forecast-row {
    display: flex;
    gap: 0.75rem;
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 4px;
}
.forecast-card {
    flex: 1;
    min-width: 90px;
    background: rgba(255,255,255,0.55);
    border: 1px solid rgba(255,255,255,0.8);
    border-radius: 16px;
    padding: 0.75rem 0.5rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.forecast-date { font-size: 0.72rem; color: #7a9a70; font-weight: 600; margin-bottom: 4px; }
.forecast-icon img { width: 48px; height: 48px; filter: brightness(1.1) drop-shadow(0 2px 4px rgba(200,150,0,0.3)); }
.forecast-temp-high { font-family: 'Raleway', sans-serif; font-size: 1.1rem; font-weight: 700; color: #2d5a20; }
.forecast-temp-low { font-size: 0.8rem; color: #8aaa80; margin-top: 2px; }
.forecast-desc { font-size: 0.7rem; color: #7a9a70; margin-top: 4px; }

/* ===== LIFE INDEX ===== */
.life-index-section { margin-top: 1.5rem; }
.life-index-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #5a7a50;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}
.life-index-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
}
.life-index-card {
    background: rgba(255,255,255,0.55);
    border: 1px solid rgba(255,255,255,0.8);
    border-radius: 16px;
    padding: 0.9rem 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.life-index-header { display: flex; align-items: center; gap: 0.4rem; margin-bottom: 0.4rem; }
.life-index-emoji { font-size: 1.3rem; }
.life-index-name { font-size: 0.78rem; color: #5a7a50; font-weight: 600; }
.life-index-stars { color: #f5a623; font-size: 1rem; letter-spacing: 1px; }
.life-index-label { font-size: 0.75rem; color: #6a8a60; margin-top: 2px; }

/* ===== MOBILE RESPONSIVE ===== */
@media (max-width: 640px) {
    .app-title { font-size: 2rem !important; }

    .block-container { padding: 1rem 0.75rem 4rem !important; }

    /* メトリクスカードを2列に */
    .metric-row { gap: 0.5rem; }
    .metric-card { min-width: calc(50% - 0.25rem); flex: 0 0 calc(50% - 0.25rem); }
    .metric-card .metric-value { font-size: 1.3rem; }

    /* 天気メインを縦並びに */
    .weather-main { flex-direction: column; align-items: flex-start; gap: 0.75rem; }
    .weather-temp { font-size: 2.5rem; }
    .weather-icon-big img { width: 60px !important; height: 60px !important; }

    /* 予報カードを小さく */
    .forecast-card { min-width: 70px; padding: 0.5rem 0.25rem; }
    .forecast-icon img { width: 36px !important; height: 36px !important; filter: brightness(1.1) drop-shadow(0 2px 4px rgba(200,150,0,0.3)) !important; }
    .forecast-temp-high { font-size: 0.95rem; }
    .forecast-temp-low { font-size: 0.72rem; }
    .forecast-desc { font-size: 0.65rem; }
    .forecast-date { font-size: 0.65rem; }

    /* タブ文字を小さく */
    [data-testid="stTabs"] [data-baseweb="tab"] {
        padding: 6px 12px !important;
        font-size: 0.8rem !important;
    }
}

/* ===== HIDE streamlit branding ===== */
#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }

/* ===== FOOTER ===== */
.app-footer {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    background: rgba(40,65,30,0.85);
    backdrop-filter: blur(10px);
    color: rgba(255,255,255,0.6);
    font-size: 0.75rem;
    padding: 10px 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 100;
}
.footer-links { display: flex; gap: 1.5rem; }
.footer-links a { color: rgba(255,255,255,0.6); text-decoration: none; }
.footer-links a:hover { color: #fff; }
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown("""
<div class="app-header">
    <h1 class="app-title">⛅ 天気アプリ</h1>
</div>
""", unsafe_allow_html=True)

# ===== TABS =====
tab1, tab2 = st.tabs(["🔍 1都市を詳しく", "📊 全都市を比較"])

# ---- Tab1: Single City ----
with tab1:
    city_jp = st.selectbox("都市を選んでください", list(CITIES.keys()), key="city_select")
    search_btn = st.button("検索", key="search_btn")

    if search_btn or "last_city" not in st.session_state:
        st.session_state["last_city"] = city_jp

    if True:
        if not API_KEY:
            st.error("⚠️ APIキーが設定されていません。.envファイルを確認してください。")
            st.stop()
        city_en = CITIES[city_jp]
        
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_en}&appid={API_KEY}&units=metric&lang=ja"
        with st.spinner(f"{city_jp}の天気を取得中..."):
            try:
                data = fetch_weather(city_en, API_KEY)
                if data.get("cod") != 200:
                    st.error(f"エラー: {data.get('message', '天気データを取得できませんでした')}")
                else:
                    temp = data["main"]["temp"]
                    feels = data["main"]["feels_like"]
                    humidity = data["main"]["humidity"]
                    wind = data["wind"]["speed"]
                    desc = data["weather"][0]["description"]
                    icon_code = data["weather"][0]["icon"]
                    icon_url = get_weather_icon_url(icon_code)

                    st.markdown(f"""
                    <div class="weather-result">
                        <div class="weather-main">
                            <div class="weather-icon-big">{icon_url}</div>
                            <div>
                                <div class="weather-temp">{temp:.0f}°C</div>
                                <div class="weather-city">📍 {city_jp}</div>
                                <div class="weather-desc">{desc}</div>
                            </div>
                        </div>
                        <div class="metric-row">
                            <div class="metric-card">
                                <div class="metric-icon">🌡️</div>
                                <div class="metric-value">{temp:.1f}°</div>
                                <div class="metric-label">気温</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-icon">🤔</div>
                                <div class="metric-value">{feels:.1f}°</div>
                                <div class="metric-label">体感温度</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-icon">💧</div>
                                <div class="metric-value">{humidity}%</div>
                                <div class="metric-label">湿度</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-icon">💨</div>
                                <div class="metric-value">{wind}</div>
                                <div class="metric-label">風速 m/s</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # 5日間予報
                    forecast_data = fetch_forecast(city_en, API_KEY)
                    if forecast_data.get("cod") == "200":
                        # 日付ごとに1件（正午付近）だけ抽出
                        seen_dates = []
                        daily = []
                        for item in forecast_data["list"]:
                            date = item["dt_txt"][:10]
                            hour = item["dt_txt"][11:13]
                            if date not in seen_dates and hour >= "11":
                                seen_dates.append(date)
                                daily.append(item)
                            if len(daily) >= 5:
                                break

                        cards_html = ""
                        for d in daily:
                            date_str = d["dt_txt"][:10][5:]  # MM-DD
                            f_icon_url = get_weather_icon_url(d["weather"][0]["icon"])
                            f_desc = d["weather"][0]["description"]
                            f_high = round(d["main"]["temp_max"], 0)
                            f_low = round(d["main"]["temp_min"], 0)
                            cards_html += f"""
                            <div class='forecast-card'>
                                <div class='forecast-date'>{date_str}</div>
                                <div class='forecast-icon' style='font-size:2.2rem;line-height:1.2;'>{f_icon_url}</div>
                                <div class='forecast-temp-high'>{f_high:.0f}°</div>
                                <div class='forecast-temp-low'>{f_low:.0f}°</div>
                                <div class='forecast-desc'>{f_desc}</div>
                            </div>"""

                        st.markdown(
                            f"<div class='forecast-section'><div class='forecast-title'>📅 5日間予報</div><div class='forecast-row'>{cards_html}</div></div>",
                            unsafe_allow_html=True
                        )

                    # 生活指数
                    indices = calc_life_index(temp, humidity, wind, desc)
                    cards_li = ""
                    for emoji, name, score, label in indices:
                        stars = "★" * score + "☆" * (5 - score)
                        cards_li += f"<div class='life-index-card'><div class='life-index-header'><span class='life-index-emoji'>{emoji}</span><span class='life-index-name'>{name}</span></div><div class='life-index-stars'>{stars}</div><div class='life-index-label'>{label}</div></div>"
                    st.markdown(
                        f"<div class='life-index-section'><div class='life-index-title'>🌿 生活指数</div><div class='life-index-grid'>{cards_li}</div></div>",
                        unsafe_allow_html=True
                    )

            except requests.exceptions.Timeout:
                st.error("⏱️ タイムアウト：サーバーの応答がありません。時間をおいて再試行してください。")
            except requests.exceptions.ConnectionError:
                st.error("📡 接続エラー：インターネット接続を確認してください。")
            except Exception as e:
                st.error(f"⚠️ 予期しないエラーが発生しました: {e}")

# ---- Tab2: All Cities ----
with tab2:
    all_btn = st.button("全都市のデータを取得", key="all_btn")

    if all_btn:
        if not API_KEY:
            st.error("⚠️ APIキーが設定されていません。.envファイルを確認してください。")
            st.stop()
        progress = st.progress(0, text="全都市のデータを並列取得中...")

        def fetch_city(jp_en):
            jp, en = jp_en
            url = f"https://api.openweathermap.org/data/2.5/weather?q={en}&appid={API_KEY}&units=metric&lang=ja"
            try:
                d = fetch_weather(en, API_KEY)
                icon_code = d["weather"][0]["icon"]
                icon_url = get_weather_icon_url(icon_code)
                return jp, {
                    "都市": f"{icon_url} {jp}",
                    "気温(℃)": round(d["main"]["temp"], 1),
                    "体感(℃)": round(d["main"]["feels_like"], 1),
                    "湿度(%)": d["main"]["humidity"],
                    "天気": d["weather"][0]["description"],
                    "風速(m/s)": d["wind"]["speed"],
                }
            except Exception:
                return jp, {"都市": jp, "気温(℃)": "—", "体感(℃)": "—", "湿度(%)": "—", "天気": "取得失敗", "風速(m/s)": "—"}

        results = {}
        total = len(CITIES)
        with ThreadPoolExecutor(max_workers=9) as executor:
            futures = {executor.submit(fetch_city, item): item[0] for item in CITIES.items()}
            done = 0
            for future in as_completed(futures):
                jp, row = future.result()
                results[jp] = row
                done += 1
                progress.progress(done / total, text=f"{done}/{total} 都市取得完了")

        progress.empty()
        # 元の都市順に並べ直す
        rows = [results[jp] for jp in CITIES.keys() if jp in results]

        # HTMLテーブルで描画
        rows_html = ""
        for r in rows:
            hum = r["湿度(%)"] if isinstance(r["湿度(%)"], int) else 0
            rows_html += f"""
            <tr>
                <td class='city-cell'>{r["都市"]}</td>
                <td class='temp-val'>{r["気温(℃)"]}°</td>
                <td class='temp-val'>{r["体感(℃)"]}°</td>
                <td>
                    <div class='hum-wrap'>
                        <span>{r["湿度(%)"]}%</span>
                        <div class='hum-bar'><div class='hum-fill' style='width:{hum}%'></div></div>
                    </div>
                </td>
            </tr>
            <tr class='sub-row'>
                <td colspan='4'>
                    <span class='sub-weather'>{r["天気"]}</span>
                    <span class='sub-wind'>💨 風速 {r["風速(m/s)"]} m/s</span>
                </td>
            </tr>"""

        st.markdown(f"""
        <table class='compare-table'>
            <thead><tr>
                <th>都市</th><th>気温</th><th>体感</th><th>湿度</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
        """, unsafe_allow_html=True)

# ===== FOOTER =====
st.markdown("""
<div class="app-footer">
    <span>Weather App 🌤️</span>
    <div class="footer-links">
        <span>Data: OpenWeatherMap</span>
        <span>© 2026 WeatherApp</span>
    </div>
</div>
""", unsafe_allow_html=True)