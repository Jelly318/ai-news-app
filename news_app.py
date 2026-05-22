import streamlit as st
import requests

API_KEY = st.secrets["NEWS_API_KEY"]

st.title("📰 AI News App")

# メインに操作
topic = st.selectbox("トピックを選ぶ", ["AI", "Apple", "Tesla", "Space", "Crypto"])
custom = st.text_input("または自由に入力", "")
if custom:
    topic = custom
search = st.button("ニュースを取得")

# サイドバーに件数スライダーだけ
with st.sidebar:
    st.header("⚙️ 設定")
    count = st.slider("表示件数", 5, 20, 10)

if search or custom:
    url = f"https://newsapi.org/v2/everything?q={topic}&language=en&sortBy=publishedAt&apiKey={API_KEY}&pageSize={count}"
    data = requests.get(url).json()

    st.subheader(f"「{topic}」の最新ニュース　（{len(data['articles'])}件表示）")

    for article in data["articles"]:
        st.subheader(article["title"])
        published = article.get("publishedAt", "")[:10]
        st.caption(f"📌 {article['source']['name']}  🗓 {published}")

        if article.get("urlToImage"):
            st.image(article["urlToImage"], use_container_width=True)

        st.write(article.get("description", ""))
        st.markdown(f"[記事を読む]({article['url']})")
        st.divider()