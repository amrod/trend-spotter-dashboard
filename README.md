# Trend Spotter Dashboard

Discover what's trending on Google right now. Click any trend to see related news and interest charts. Powered by [SerpApi](https://serpapi.com).

A Streamlit dashboard that shows what's trending on Google right now, with related news articles and interest-over-time charts.

Built with the **SerpApi Python SDK** for the SerpApi conference raffle challenge.

## What It Does

- **Trending Now** -- See the top trending searches on Google, with search volume, percentage increase, and category tags
- **News Deep-Dive** -- Click any trend to see related news articles from Google News
- **Interest Charts** -- View interest-over-time charts showing how a topic has trended over the past 7 days
- **Custom Search** -- Enter any topic to pull news and trend data on demand
- **Filters** -- Filter by country (US, UK, Canada, etc.), time range, and category (Sports, Tech, Entertainment, etc.)

## SerpApi Engines Used

| Engine | Purpose |
|--------|---------|
| `google_trends_trending_now` | Fetch currently trending searches with volume, categories, and related queries |
| `google_news` | Fetch news articles for a trending topic or custom query |
| `google_trends` | Fetch interest-over-time data (TIMESERIES) for charting |

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/amrod/trend-spotter-dashboard.git
cd trend-spotter-dashboard
```

### 2. Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Set your API key

Get a free API key at [serpapi.com/users/sign_up](https://serpapi.com/users/sign_up) (250 searches/month).

Create a `.env` file:

```bash
cp .env.example .env
# Edit .env and paste your API key
```

Or set the environment variable directly:

```bash
export SERPAPI_KEY=your_api_key_here
```

### 4. Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Deploy to Streamlit Community Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo and select `app.py`
4. Add `SERPAPI_KEY` as a secret in the Streamlit Cloud dashboard (Settings > Secrets):
   ```toml
   SERPAPI_KEY = "your_api_key_here"
   ```
5. Deploy

## Screenshots

### Trending Now

<img width="952" height="447" alt="Screenshot 2026-05-15 171436" src="https://github.com/user-attachments/assets/12fd56ef-1ba9-46a3-9b5d-ecf99b0ca450" />

The main view shows currently trending Google searches with search volume and category tags. Click any trend to deep-dive into related news and interest charts.

### Deep Dive

<img width="951" height="500" alt="Screenshot 2026-05-15 175412" src="https://github.com/user-attachments/assets/565c2b08-1ab7-4b07-9d15-e7294e862023" />

Select a trending topic to see:
- Related news articles from Google News
- An interest-over-time line chart from Google Trends
- Trend metadata (volume, increase %, categories, related queries)

### Custom Search

<img width="950" height="484" alt="Screenshot 2026-05-15 175507" src="https://github.com/user-attachments/assets/71abf467-e711-43bd-b43b-2f537f27acf3" />

Use the sidebar to search any topic and get news + trend data instantly.

## Tech Stack

- **Python 3.10+**
- **Streamlit** -- UI framework
- **SerpApi Python SDK** -- Search data (`pip install serpapi`)
- **Pandas** -- Data manipulation for charts

## License

MIT
