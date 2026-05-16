"""
Trend Spotter Dashboard
A Streamlit app that shows what's trending on Google right now,
with related news articles and interest-over-time charts.

Uses 3 SerpApi engines:
  - google_trends_trending_now: Currently trending searches
  - google_news: News articles for a topic
  - google_trends: Interest over time (TIMESERIES)
"""

import os
import datetime

import pandas as pd
import streamlit as st
import serpapi
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv()

# Try multiple sources for the API key
API_KEY = os.getenv("SERPAPI_KEY", "")
if not API_KEY:
    # Fallback: read from file if present (local dev convenience)
    key_file = os.path.join(os.path.dirname(__file__), "serpapi-api-key.txt")
    if os.path.exists(key_file):
        with open(key_file) as f:
            API_KEY = f.read().strip()

CATEGORY_MAP = {
    "All": None,
    "Business": 12,
    "Entertainment": 4,
    "Health": 7,
    "Politics": 14,
    "Science": 15,
    "Sports": 17,
    "Technology": 18,
}

COUNTRY_MAP = {
    "United States": "US",
    "United Kingdom": "GB",
    "Canada": "CA",
    "Australia": "AU",
    "India": "IN",
    "Germany": "DE",
    "France": "FR",
    "Brazil": "BR",
    "Japan": "JP",
    "Mexico": "MX",
}

TIME_RANGE_MAP = {
    "Past 4 hours": 4,
    "Past 24 hours": 24,
    "Past 48 hours": 48,
    "Past 7 days": 168,
}

# ---------------------------------------------------------------------------
# SerpApi helpers (cached to preserve API quota)
# ---------------------------------------------------------------------------


def _get_client() -> serpapi.Client:
    return serpapi.Client(api_key=API_KEY)


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_trending(geo: str, hours: int, category_id: int | None) -> list[dict]:
    """Fetch currently trending searches via google_trends_trending_now."""
    params: dict = {
        "engine": "google_trends_trending_now",
        "geo": geo,
        "hours": hours,
        "hl": "en",
    }
    if category_id is not None:
        params["category_id"] = category_id

    results = _get_client().search(params)
    return results.get("trending_searches", [])


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_news(query: str, gl: str) -> list[dict]:
    """Fetch Google News results for a query."""
    results = _get_client().search(
        {
            "engine": "google_news",
            "q": query,
            "gl": gl.lower(),
            "hl": "en",
        }
    )
    return results.get("news_results", [])


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_interest_over_time(query: str, geo: str) -> list[dict]:
    """Fetch interest-over-time data via google_trends TIMESERIES."""
    results = _get_client().search(
        {
            "engine": "google_trends",
            "q": query,
            "geo": geo,
            "data_type": "TIMESERIES",
            "date": "now 7-d",
        }
    )
    iot = results.get("interest_over_time", {})
    return iot.get("timeline_data", [])


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------


def render_trending_card(trend: dict, index: int) -> bool:
    """Render a single trending topic card. Returns True if user clicks it."""
    query = trend.get("query", "Unknown")
    volume = trend.get("search_volume", 0)
    pct = trend.get("increase_percentage", 0)
    active = trend.get("active", False)
    categories = trend.get("categories", [])
    breakdown = trend.get("trend_breakdown", [])

    cat_tags = " ".join(f"`{c['name']}`" for c in categories) if categories else ""
    status_dot = "🟢" if active else "⚪"

    col1, col2 = st.columns([4, 1])
    with col1:
        clicked = st.button(
            f"{status_dot}  **{query}**",
            key=f"trend_{index}",
            use_container_width=True,
        )
        meta_parts = []
        if volume:
            meta_parts.append(f"Vol: **{volume:,}**")
        if pct:
            meta_parts.append(f"+{pct}%")
        if cat_tags:
            meta_parts.append(cat_tags)
        if meta_parts:
            st.caption(" | ".join(meta_parts))
    with col2:
        if breakdown:
            st.caption("Related:")
            st.caption(", ".join(breakdown[:3]))

    return clicked


def render_news_article(article: dict):
    """Render a single news article."""
    title = article.get("title", "")
    link = article.get("link", "")
    source = article.get("source", {})
    source_name = source.get("name", "Unknown")
    date_str = article.get("date", "")
    snippet = article.get("snippet", "")

    # Some results have nested "stories" instead of a direct title
    if not title and "highlight" in article:
        highlight = article["highlight"]
        title = highlight.get("title", "")
        link = highlight.get("link", link)
        source = highlight.get("source", source)
        source_name = source.get("name", source_name)
        date_str = highlight.get("date", date_str)

    if not title:
        return

    st.markdown(f"**[{title}]({link})**")
    caption_parts = [f"_{source_name}_"]
    if date_str:
        # Show just the date portion
        caption_parts.append(date_str.split(",")[0] if "," in date_str else date_str)
    st.caption(" | ".join(caption_parts))
    if snippet:
        st.write(snippet[:200])
    st.divider()


def render_interest_chart(timeline_data: list[dict], query: str):
    """Render an interest-over-time line chart."""
    if not timeline_data:
        st.info("No interest-over-time data available for this query.")
        return

    rows = []
    for point in timeline_data:
        date_str = point.get("date", "")
        values = point.get("values", [])
        for v in values:
            rows.append(
                {
                    "Date": date_str,
                    "Interest": v.get("extracted_value", 0),
                }
            )

    if not rows:
        return

    df = pd.DataFrame(rows)
    # Add numeric index for chart ordering
    df["idx"] = range(len(df))

    st.line_chart(df, x="idx", y="Interest", x_label="Time", y_label="Interest")
    st.caption(
        f"Google Trends interest over the past 7 days for **{query}**. "
        "Values are relative (0-100 scale)."
    )


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------


def main():
    st.set_page_config(
        page_title="Trend Spotter",
        page_icon="📈",
        layout="wide",
    )

    st.title("📈 Trend Spotter Dashboard")
    st.markdown(
        "Discover what's trending on Google right now. "
        "Click any trend to see related news and interest charts.  \n"
        "_Powered by [SerpApi](https://serpapi.com)._"
    )

    # --- API key guard ---
    if not API_KEY:
        st.error(
            "No SerpApi API key found. "
            "Set the `SERPAPI_KEY` environment variable or create a `.env` file. "
            "Get a free key at https://serpapi.com/users/sign_up"
        )
        st.stop()

    # --- Sidebar controls ---
    with st.sidebar:
        st.header("Settings")

        country_name = st.selectbox("Country", list(COUNTRY_MAP.keys()), index=0)
        geo = COUNTRY_MAP[country_name]

        time_label = st.selectbox("Time Range", list(TIME_RANGE_MAP.keys()), index=1)
        hours = TIME_RANGE_MAP[time_label]

        category_name = st.selectbox("Category", list(CATEGORY_MAP.keys()), index=0)
        category_id = CATEGORY_MAP[category_name]

        st.divider()

        st.header("Custom Search")
        custom_query = st.text_input(
            "Search any topic",
            placeholder="e.g. artificial intelligence",
        )

        st.divider()
        st.caption(
            "Data cached for 30 min to conserve API quota. "
            "Free plan: 250 searches/month."
        )

    # --- Custom search mode ---
    if custom_query:
        st.subheader(f"Results for: {custom_query}")

        tab_news, tab_trends = st.tabs(["News", "Interest Over Time"])

        with tab_news:
            with st.spinner("Fetching news..."):
                articles = fetch_news(custom_query, geo)
            if articles:
                for article in articles[:10]:
                    render_news_article(article)
            else:
                st.info("No news articles found for this query.")

        with tab_trends:
            with st.spinner("Fetching trend data..."):
                timeline = fetch_interest_over_time(custom_query, geo)
            render_interest_chart(timeline, custom_query)

        st.divider()
        st.markdown("---")

    # --- Trending now ---
    st.subheader(f"Trending Now in {country_name}")
    filter_desc = f"{time_label}"
    if category_name != "All":
        filter_desc += f" | {category_name}"
    st.caption(filter_desc)

    with st.spinner("Fetching trending searches..."):
        trends = fetch_trending(geo, hours, category_id)

    if not trends:
        st.warning("No trending searches found. Try a different country or time range.")
        st.stop()

    # Show count
    active_count = sum(1 for t in trends if t.get("active"))
    st.caption(
        f"Found **{len(trends)}** trending searches "
        f"(**{active_count}** currently active)"
    )

    # Use session state to track selected trend
    if "selected_trend" not in st.session_state:
        st.session_state.selected_trend = None

    # Render trend list
    for i, trend in enumerate(trends[:25]):
        clicked = render_trending_card(trend, i)
        if clicked:
            st.session_state.selected_trend = trend.get("query", "")

    # --- Deep dive into selected trend ---
    selected = st.session_state.selected_trend
    if selected:
        st.divider()
        st.subheader(f"Deep Dive: {selected}")

        tab_news, tab_trends, tab_info = st.tabs(
            ["News", "Interest Over Time", "Trend Info"]
        )

        with tab_news:
            with st.spinner("Fetching news..."):
                articles = fetch_news(selected, geo)
            if articles:
                for article in articles[:8]:
                    render_news_article(article)
            else:
                st.info("No news articles found.")

        with tab_trends:
            with st.spinner("Fetching trend data..."):
                timeline = fetch_interest_over_time(selected, geo)
            render_interest_chart(timeline, selected)

        with tab_info:
            # Find the trend data from our list
            trend_data = next(
                (t for t in trends if t.get("query") == selected), None
            )
            if trend_data:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Search Volume", f"{trend_data.get('search_volume', 0):,}")
                with col2:
                    st.metric("Increase", f"+{trend_data.get('increase_percentage', 0)}%")
                with col3:
                    st.metric(
                        "Status", "Active" if trend_data.get("active") else "Inactive"
                    )

                categories = trend_data.get("categories", [])
                if categories:
                    st.write("**Categories:**", ", ".join(c["name"] for c in categories))

                breakdown = trend_data.get("trend_breakdown", [])
                if breakdown:
                    st.write("**Related queries:**")
                    for bq in breakdown[:10]:
                        st.write(f"- {bq}")

        # Clear selection button
        if st.button("Clear selection"):
            st.session_state.selected_trend = None
            st.rerun()


if __name__ == "__main__":
    main()
