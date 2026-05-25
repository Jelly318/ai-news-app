import streamlit as st
import requests
from deep_translator import GoogleTranslator
from datetime import datetime, timezone

st.set_page_config(
    page_title="AI News App",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans JP', sans-serif;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 900px !important;
}

.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.2rem;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 1.5rem;
    background: white;
    gap: 10px;
}
.header-left {
    display: flex;
    align-items: center;
    gap: 12px;
    flex: 1 1 0;
    min-width: 0;
}
.header-title {
    font-size: clamp(18px, 4vw, 32px);
    font-weight: 800;
    color: #111827;
    margin: 0;
    line-height: 1.2;
}
.header-sub {
    font-size: clamp(10px, 2vw, 13px);
    color: #6b7280;
    margin: 3px 0 0 0;
}
.header-icon-svg {
    flex-shrink: 0;
    width: clamp(44px, 8vw, 64px);
    height: clamp(44px, 8vw, 64px);
    border-radius: 14px;
}
.deploy-btn {
    background: linear-gradient(135deg, #7C3AED, #6D28D9);
    color: white !important;
    border: none;
    border-radius: 10px;
    padding: 8px 14px;
    font-size: clamp(12px, 2.5vw, 14px);
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 5px;
    white-space: nowrap;
    flex-shrink: 0;
}

div[data-testid="stButton"] > button {
    width: 100% !important;
    background: linear-gradient(135deg, #7C3AED, #6D28D9) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    margin-top: 0.5rem;
}
div[data-testid="stButton"] > button:hover {
    opacity: 0.9 !important;
}

.results-header {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin: 1.2rem 0 1rem 0;
}
.results-title-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
}
.results-title {
    font-size: clamp(14px, 3.5vw, 17px);
    font-weight: 700;
    color: #111827;
}
.results-badge {
    background: #EDE9FE;
    color: #6D28D9;
    font-size: 12px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
}
.results-date {
    font-size: 12px;
    color: #9ca3af;
}

.article-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    display: flex;
    gap: 14px;
    align-items: flex-start;
    cursor: pointer;
    transition: box-shadow 0.2s, border-color 0.2s;
    text-decoration: none;
}
.article-card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    border-color: #c4b5fd;
}
.article-thumb {
    width: 72px;
    height: 72px;
    border-radius: 10px;
    object-fit: cover;
    flex-shrink: 0;
}
.article-thumb-placeholder {
    width: 72px;
    height: 72px;
    border-radius: 10px;
    background: linear-gradient(135deg, #EDE9FE, #DDD6FE);
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
}
.article-content { flex: 1; min-width: 0; }
.article-title {
    font-size: clamp(13px, 2.8vw, 15px);
    font-weight: 600;
    color: #111827;
    margin: 0 0 5px 0;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.article-desc {
    font-size: clamp(11px, 2.2vw, 13px);
    color: #6b7280;
    margin: 0 0 8px 0;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.article-meta {
    font-size: 12px;
    color: #9ca3af;
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
}
.article-source { font-weight: 600; color: #6b7280; }
.article-arrow { color: #d1d5db; font-size: 18px; flex-shrink: 0; align-self: center; }

.app-footer {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    padding: 1.5rem;
    border-top: 1px solid #e5e7eb;
    margin-top: 2rem;
    background: #fafafa;
    border-radius: 0 0 16px 16px;
}
.footer-item { display: flex; align-items: flex-start; gap: 10px; }
.footer-icon { font-size: 18px; flex-shrink: 0; margin-top: 2px; }
.footer-title { font-size: 13px; font-weight: 600; color: #374151; margin: 0 0 3px 0; }
.footer-text { font-size: 11px; color: #9ca3af; line-height: 1.5; margin: 0; }
.footer-link { color: #7C3AED; text-decoration: none; font-size: 11px; }

/* スライダー紫 */
[data-testid="stSlider"] [role="slider"] {
    background: #7C3AED !important;
    border-color: #7C3AED !important;
}
[data-testid="stSliderThumbValue"] {
    background: transparent !important;
    color: #7C3AED !important;
}

[data-testid="stSelectbox"] label {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #374151 !important;
}
[data-testid="stSelectbox"] > div > div {
    background-color: white !important;
    border: 1.5px solid #e5e7eb !important;
    color: #111827 !important;
}
[data-testid="stTextInput"] label {
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #374151 !important;
}
</style>
""", unsafe_allow_html=True)

API_KEY = st.secrets["NEWS_API_KEY"]

st.markdown("""
<div class="app-header">
    <div class="header-left">
        <svg class="header-icon-svg" viewBox="0 0 70 70" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#0f0c29"/>
              <stop offset="50%" style="stop-color:#302b63"/>
              <stop offset="100%" style="stop-color:#1a1a4e"/>
            </linearGradient>
            <linearGradient id="aiGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#c084fc"/>
              <stop offset="50%" style="stop-color:#818cf8"/>
              <stop offset="100%" style="stop-color:#e879f9"/>
            </linearGradient>
          </defs>
          <rect width="70" height="70" rx="16" fill="url(#bgGrad)"/>
          <text x="35" y="36" text-anchor="middle" font-family="Arial Black, sans-serif" font-weight="900" font-size="24" fill="url(#aiGrad)">AI</text>
          <text x="35" y="54" text-anchor="middle" font-family="Arial, sans-serif" font-weight="700" font-size="10" fill="#a78bfa" letter-spacing="3">NEWS</text>
        </svg>
        <div>
            <p class="header-title">AI News App</p>
            <p class="header-sub">最新のトレンドニュースをAIが素早くキャッチアップします</p>
        </div>
    </div>
    <a class="deploy-btn" href="https://streamlit.io/cloud" target="_blank">🚀 Deploy</a>
</div>
""", unsafe_allow_html=True)

# 設定エリア
set_col1, set_col2 = st.columns([1, 2])
with set_col1:
    count = st.slider("表示件数", min_value=1, max_value=10, value=5, step=1)
with set_col2:
    lang = st.selectbox("翻訳言語", ["翻訳しない", "日本語", "中国語", "韓国語", "スペイン語"])

# 検索エリア
col1, col2 = st.columns(2)
with col1:
    topic = st.selectbox("トピックを選ぶ", ["AI", "Apple", "Tesla", "Space", "Crypto"])
with col2:
    custom = st.text_input("またはキーワードで検索", placeholder="キーワードを入力 🔍")
if custom:
    topic = custom
search = st.button("✦  ニュースを取得", use_container_width=True)

# 記事取得
lang_map = {"日本語": "ja", "中国語": "zh-CN", "韓国語": "ko", "スペイン語": "es"}

if True:
    url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=publishedAt&apiKey={API_KEY}&pageSize={count}"
    data = requests.get(url).json()
    articles = data.get("articles", [])

    now = datetime.now().strftime("%Y/%m/%d %H:%M")
    st.markdown(f"""
    <div class="results-header">
        <div class="results-title-row">
            <span class="results-title">✨ 「{topic}」の最新ニュース</span>
            <span class="results-badge">{len(articles)}件表示</span>
        </div>
        <div class="results-date">更新日時: {now}</div>
    </div>
    """, unsafe_allow_html=True)

    for article in articles:
        title = article.get("title") or ""
        description = article.get("description") or ""
        source = article.get("source", {}).get("name", "")
        url_img = article.get("urlToImage") or ""
        article_url = article.get("url", "#")
        published = article.get("publishedAt", "")

        try:
            pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            diff = datetime.now(timezone.utc) - pub_dt
            hours = int(diff.total_seconds() // 3600)
            time_str = f"{hours}時間前" if hours < 24 else f"{diff.days}日前"
        except:
            time_str = published[:10]

        if lang != "翻訳しない":
            target = lang_map[lang]
            try:
                if title:
                    title = GoogleTranslator(source="en", target=target).translate(title)
                if description:
                    description = GoogleTranslator(source="en", target=target).translate(description)
            except:
                pass

        thumb_html = f'<img class="article-thumb" src="{url_img}" />' if url_img else '<div class="article-thumb-placeholder">📄</div>'

        st.markdown(f"""
        <a class="article-card" href="{article_url}" target="_blank">
            {thumb_html}
            <div class="article-content">
                <p class="article-title">{title}</p>
                <p class="article-desc">{description}</p>
                <div class="article-meta">
                    <span class="article-source">{source}</span>
                    <span>•</span>
                    <span>{time_str}</span>
                </div>
            </div>
            <span class="article-arrow">›</span>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="app-footer">
        <div class="footer-item">
            <div class="footer-icon">📄</div>
            <div>
                <p class="footer-title">著作権について</p>
                <p class="footer-text">本アプリで配信される記事の著作権は、それぞれの配信元メディアに帰属します。</p>
            </div>
        </div>
        <div class="footer-item">
            <div class="footer-icon">🛡️</div>
            <div>
                <p class="footer-title">免責事項</p>
                <p class="footer-text">AIによる自動要約が含まれるため、情報の正確性を完全に保証するものではありません。</p>
            </div>
        </div>
        <div class="footer-item">
            <div class="footer-icon">🤖</div>
            <div>
                <p class="footer-title">APIについて</p>
                <p class="footer-text">本アプリは外部のニュースAPIを利用しています。<br><a class="footer-link" href="https://newsapi.org" target="_blank">Powered by NewsAPI</a></p>
            </div>
        </div>
        <div class="footer-item">
            <div class="footer-icon">🔒</div>
            <div>
                <p class="footer-title">安全・安心</p>
                <p class="footer-text">プライバシーとデータの保護に努めています。</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)