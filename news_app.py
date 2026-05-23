import streamlit as st
import requests
from deep_translator import GoogleTranslator
from datetime import datetime, timezone

st.set_page_config(
    page_title="AI News App",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans JP', sans-serif;
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 2rem !important;
    max-width: 900px !important;
}

/* ===== HEADER ===== */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.2rem 1.5rem;
    border-bottom: 1px solid #e5e7eb;
    margin-bottom: 1.5rem;
    background: white;
}
.header-left {
    display: flex;
    align-items: center;
    gap: 14px;
}
.header-icon {
    width: 64px;
    height: 64px;
    background: linear-gradient(160deg, #1a1a3e 0%, #2d1b69 50%, #1a1a3e 100%);
    border-radius: 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    gap: 1px;
    box-shadow: 0 2px 12px rgba(108,62,244,0.3);
}
.header-icon-text-ai {
    font-size: 18px;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #818cf8, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1;
    letter-spacing: 1px;
}
.header-icon-text-news {
    font-size: 8px;
    font-weight: 700;
    color: #a78bfa;
    letter-spacing: 2px;
    line-height: 1;
}
.header-title {
    font-size: 36px;
    font-weight: 800;
    color: #111827;
    margin: 0;
    line-height: 1.2;
}
.header-sub {
    font-size: 13px;
    color: #6b7280;
    margin: 2px 0 0 0;
}
.deploy-btn {
    background: linear-gradient(135deg, #7C3AED, #6D28D9);
    color: white !important;
    border: none;
    border-radius: 10px;
    padding: 9px 20px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ===== SEARCH AREA ===== */
.search-area {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
}

/* ===== FETCH BUTTON ===== */
div[data-testid="stButton"] > button {
    width: 100% !important;
    background: linear-gradient(135deg, #7C3AED, #6D28D9) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px;
    transition: opacity 0.2s;
    margin-top: 0.5rem;
}
div[data-testid="stButton"] > button:hover {
    opacity: 0.9 !important;
}

/* ===== RESULTS HEADER ===== */
.results-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 1.2rem 0 1rem 0;
}
.results-title {
    font-size: 17px;
    font-weight: 700;
    color: #111827;
    display: flex;
    align-items: center;
    gap: 8px;
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

/* ===== ARTICLE CARD ===== */
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
    width: 80px;
    height: 80px;
    border-radius: 10px;
    object-fit: cover;
    flex-shrink: 0;
    background: #f3f4f6;
}
.article-thumb-placeholder {
    width: 80px;
    height: 80px;
    border-radius: 10px;
    background: linear-gradient(135deg, #EDE9FE, #DDD6FE);
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
}
.article-content {
    flex: 1;
    min-width: 0;
}
.article-title {
    font-size: 15px;
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
    font-size: 13px;
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
    gap: 8px;
}
.article-source {
    font-weight: 600;
    color: #6b7280;
}
.article-arrow {
    color: #d1d5db;
    font-size: 18px;
    flex-shrink: 0;
    align-self: center;
}

/* ===== FOOTER ===== */
.app-footer {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    padding: 1.5rem;
    border-top: 1px solid #e5e7eb;
    margin-top: 2rem;
    background: #fafafa;
    border-radius: 0 0 16px 16px;
}
.footer-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
}
.footer-icon {
    font-size: 18px;
    flex-shrink: 0;
    margin-top: 2px;
}
.footer-title {
    font-size: 13px;
    font-weight: 600;
    color: #374151;
    margin: 0 0 3px 0;
}
.footer-text {
    font-size: 11px;
    color: #9ca3af;
    line-height: 1.5;
    margin: 0;
}
.footer-link {
    color: #7C3AED;
    text-decoration: none;
    font-size: 11px;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: white;
    border-right: 1px solid #e5e7eb;
}
[data-testid="stSidebar"] .sidebar-title {
    font-size: 16px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 1.2rem;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #374151 !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div {
    background: #7C3AED !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div > div {
    background: #7C3AED !important;
}
[data-testid="stSidebar"] input[type="range"]::-webkit-slider-thumb {
    background: #7C3AED !important;
}
[data-testid="stSidebar"] input[type="range"]::-webkit-slider-runnable-track {
    background: #7C3AED !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    border: 1.5px solid #e0dcff !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] [data-testid="stSlider"] span {
    background: transparent !important;
    color: #374151 !important;
}
/* スライダーの丸を紫に */
[data-testid="stSidebar"] [data-testid="stSlider"] div[role="slider"] {
    background: #7C3AED !important;
    border-color: #7C3AED !important;
}
/* ホバー時の1と10（紫背景）を消す */
.st-emotion-cache-193zvb2,
.st-emotion-cache-15wjmlq {
    display: none !important;
}
.how-to-box {
    background: #F5F3FF;
    border: 1px solid #DDD6FE;
    border-radius: 12px;
    padding: 1rem;
    margin-top: 1.5rem;
}
.how-to-title {
    font-size: 13px;
    font-weight: 700;
    color: #5B21B6;
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 8px;
}
.how-to-text {
    font-size: 12px;
    color: #6D28D9;
    line-height: 1.6;
}

/* Selectbox styling */
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
[data-testid="stSelectbox"] > div > div > div {
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

# ===== HEADER =====
st.markdown("""
<div class="app-header">
    <div class="header-left">
        <svg width="70" height="70" viewBox="0 0 70 70" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;border-radius:16px;">
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
            <p style="font-size:32px;font-weight:800;color:#111827;margin:0;line-height:1.2;">AI News App</p>
            <p style="font-size:14px;color:#6b7280;margin:4px 0 0 0;">最新のトレンドニュースをAIが素早くキャッチアップします</p>
        </div>
    </div>
    <a class="deploy-btn" href="https://streamlit.io/cloud" target="_blank">🚀 Deploy</a>
</div>
""", unsafe_allow_html=True)

# 1と10のブロックをJSで消す
st.markdown("""
<script>
function removeTickLabels() {
    const slider = document.querySelector('[data-testid="stSidebar"] [data-testid="stSlider"]');
    if (slider) {
        const ps = slider.querySelectorAll('p');
        ps.forEach(p => {
            if (p.textContent === '1' || p.textContent === '10') {
                p.parentElement.style.display = 'none';
            }
        });
    }
}
setTimeout(removeTickLabels, 500);
setTimeout(removeTickLabels, 1500);
</script>
""", unsafe_allow_html=True)
with st.sidebar:
    st.markdown('<p class="sidebar-title" style="font-size:18px;font-weight:700;color:#5B21B6;">⚙️ 設定</p>', unsafe_allow_html=True)
    count = st.slider("表示件数", 1, 10, 5)
    st.markdown('<div style="display:flex;justify-content:space-between;margin-top:-4.2rem;margin-bottom:2.8rem;padding:0 2px;"><span style="font-size:12px;color:#9ca3af;">1</span><span style="font-size:12px;color:#9ca3af;">10</span></div>', unsafe_allow_html=True)
    lang = st.selectbox("翻訳言語", ["翻訳しない", "日本語", "中国語", "韓国語", "スペイン語"])

    st.markdown("""
    <div class="how-to-box">
        <div class="how-to-title">💡 使い方</div>
        <div class="how-to-text">
            トピックやキーワードを指定すると、AIが最新のニュースを収集・要約します。<br><br>
            気になるテーマを自由に検索してみてください。
        </div>
    </div>
    """, unsafe_allow_html=True)

# ===== SEARCH AREA =====
col1, col2 = st.columns(2)
with col1:
    topic = st.selectbox("トピックを選ぶ", ["AI", "Apple", "Tesla", "Space", "Crypto"])
with col2:
    custom = st.text_input("またはキーワードで検索", placeholder="キーワードを入力 🔍")
if custom:
    topic = custom
search = st.button("✦  ニュースを取得", use_container_width=True)

# ===== ARTICLES =====
lang_map = {"日本語": "ja", "中国語": "zh-CN", "韓国語": "ko", "スペイン語": "es"}

if True:
    url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=publishedAt&apiKey={API_KEY}&pageSize={count}"
    data = requests.get(url).json()
    articles = data.get("articles", [])

    now = datetime.now().strftime("%Y/%m/%d %H:%M")
    st.markdown(f"""
    <div class="results-header">
        <div class="results-title">
            ✨ 「{topic}」の最新ニュース
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

        # 経過時間
        try:
            pub_dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            diff = datetime.now(timezone.utc) - pub_dt
            hours = int(diff.total_seconds() // 3600)
            time_str = f"{hours}時間前" if hours < 24 else f"{diff.days}日前"
        except:
            time_str = published[:10]

        # 翻訳
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

    # ===== FOOTER =====
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
                <p class="footer-text">AIによる自動要約が含まれるため、情報の正確性を完全に保証するものではありません。重要なニュースは必ず元の配信記事をご確認ください。</p>
            </div>
        </div>
        <div class="footer-item">
            <div class="footer-icon">🤖</div>
            <div>
                <p class="footer-title">APIについて</p>
                <p class="footer-text">本アプリは外部のニュースAPIを利用しています。<br><a class="footer-link" href="https://newsapi.org" target="_blank">データ提供: Powered by NewsAPI</a></p>
            </div>
        </div>
        <div class="footer-item">
            <div class="footer-icon">🔒</div>
            <div>
                <p class="footer-title">安全・安心</p>
                <p class="footer-text">安全・安心にご利用いただけるようプライバシーとデータの保護に努めています。</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)