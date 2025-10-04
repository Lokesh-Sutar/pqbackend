import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import praw
import requests
import yfinance as yf
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import (
    FINNHUB_API_KEY,
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
)
from tools.sentiment.db_utils import (
    cleanup_old_data,
    get_db_connection,
    initialize_database,
    insert_finnhub_article,
    insert_reddit_post,
    insert_yfinance_news,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/sentiment_fetch.log'),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

DEFAULT_TICKERS = [
    'AAPL',
    'AMD',
    'AMZN',
    'GOOGL',
    'GOOG',
    'IBM',
    'META',
    'MSFT',
    'NFLX',
    'NVDA',
    'ORCL',
    'PYPL',
    'QCOM',
    'TSLA',
    'UBER',
]

# Indian stock tickers (NSE - .NS suffix, BSE - .BO suffix)
# Indian stock tickers (NSE - .NS suffix, BSE - .BO suffix)

INDIAN_TICKERS = [
    # --- BIG CONGLOMERATES ---
    'RELIANCE.NS',  # Reliance Industries
    'ADANIENT.NS',  # Adani Enterprises
    'TATAMOTORS.NS',  # Tata Motors
    'TATASTEEL.NS',  # Tata Steel
    # --- TECHNOLOGY / IT ---
    'TCS.NS',  # Tata Consultancy Services
    'INFY.NS',  # Infosys
    'WIPRO.NS',  # Wipro
    'HCLTECH.NS',  # HCL Technologies
    'TECHM.NS',  # Tech Mahindra
    # --- BANKING / FINANCE ---
    'HDFCBANK.NS',  # HDFC Bank
    'ICICIBANK.NS',  # ICICI Bank
    'SBIN.NS',  # State Bank of India
    'KOTAKBANK.NS',  # Kotak Mahindra Bank
    'BAJFINANCE.NS',  # Bajaj Finance
    # --- FMCG / CONSUMER ---
    'HINDUNILVR.NS',  # Hindustan Unilever
    'ITC.NS',  # ITC Limited
    'ASIANPAINT.NS',  # Asian Paints
    'DABUR.NS',  # Dabur
    'NESTLEIND.NS',  # Nestlé India
    # --- PHARMA / HEALTHCARE ---
    'SUNPHARMA.NS',  # Sun Pharmaceutical
    'DRREDDY.NS',  # Dr. Reddy’s Labs
    'CIPLA.NS',  # Cipla
    'DIVISLAB.NS',  # Divi’s Laboratories
    'LUPIN.NS',  # Lupin
    # --- DEFENCE / ENGINEERING ---
    'BEL.NS',  # Bharat Electronics
    'HAL.NS',  # Hindustan Aeronautics
    'LT.NS',  # Larsen & Toubro
    'BEML.NS',  # BEML
    'MAZDOCK.NS',  # Mazagon Dock Shipbuilders
    # --- ENERGY / POWER ---
    'ONGC.NS',  # Oil & Natural Gas Corp
    'NTPC.NS',  # NTPC Ltd
    'POWERGRID.NS',  # Power Grid Corp
    'IOC.NS',  # Indian Oil Corp
]

TICKER_TO_COMPANY = {
    # US stocks
    'AAPL': 'Apple',
    'AMD': 'Advanced Micro Devices',
    'AMZN': 'Amazon',
    'GOOGL': 'Google',
    'GOOG': 'Google',
    'IBM': 'IBM',
    'META': 'Meta',
    'MSFT': 'Microsoft',
    'NFLX': 'Netflix',
    'NVDA': 'Nvidia',
    'ORCL': 'Oracle',
    'PYPL': 'PayPal',
    'QCOM': 'Qualcomm',
    'TSLA': 'Tesla',
    'UBER': 'Uber',
    # Indian stocks
    'RELIANCE.NS': 'Reliance Industries',
    'ADANIENT.NS': 'Adani Enterprises',
    'TATAMOTORS.NS': 'Tata Motors',
    'TATASTEEL.NS': 'Tata Steel',
    'TCS.NS': 'Tata Consultancy Services',
    'INFY.NS': 'Infosys',
    'WIPRO.NS': 'Wipro',
    'HCLTECH.NS': 'HCL Technologies',
    'TECHM.NS': 'Tech Mahindra',
    'HDFCBANK.NS': 'HDFC Bank',
    'ICICIBANK.NS': 'ICICI Bank',
    'SBIN.NS': 'State Bank of India',
    'KOTAKBANK.NS': 'Kotak Mahindra Bank',
    'BAJFINANCE.NS': 'Bajaj Finance',
    'HINDUNILVR.NS': 'Hindustan Unilever',
    'ITC.NS': 'ITC Limited',
    'ASIANPAINT.NS': 'Asian Paints',
    'DABUR.NS': 'Dabur',
    'NESTLEIND.NS': 'Nestlé India',
    'SUNPHARMA.NS': 'Sun Pharmaceutical',
    'DRREDDY.NS': "Dr. Reddy's Laboratories",
    'CIPLA.NS': 'Cipla',
    'DIVISLAB.NS': "Divi's Laboratories",
    'LUPIN.NS': 'Lupin',
    'BEL.NS': 'Bharat Electronics',
    'HAL.NS': 'Hindustan Aeronautics',
    'LT.NS': 'Larsen & Toubro',
    'BEML.NS': 'BEML',
    'MAZDOCK.NS': 'Mazagon Dock Shipbuilders',
    'ONGC.NS': 'Oil & Natural Gas Corporation',
    'NTPC.NS': 'NTPC Limited',
    'POWERGRID.NS': 'Power Grid Corporation',
    'IOC.NS': 'Indian Oil Corporation',
}

subreddits = [
    # General investing & markets
    'investing',
    'stocks',
    'StockMarket',
    'wallstreetbets',
    # Trading & tactics
    'trading',
    'Daytrading',
    'options',
    'algotrading',
    'technicalanalysis',
    # Strategy / value / long-term investing
    'ValueInvesting',
    'dividends',
    'DividendInvesting',
    'dividends',
    'Bogleheads',
    'financialindependence',
    'personalfinance',
    # Niche / high-risk / microcaps
    'pennystocks',
    'smallstreetbets',
    'RobinHood',
    'Wallstreetbetsnew',
    # Idea-sharing & research
    'InvestingIdeas',
    'StockPicks',
    'StockMarketResearch',
    'InvestingForBeginners',
]


class SentimentDataFetcher:
    """Fetches and analyzes sentiment data from Reddit and FinHub"""

    def __init__(self):
        self.finbert = None
        self.reddit = None
        self._initialize_finbert()
        self._initialize_reddit()

    def _initialize_finbert(self):
        """Initialize FinBERT model for sentiment analysis"""
        logger.info('Loading FinBERT model...')
        try:
            tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert')
            model = AutoModelForSequenceClassification.from_pretrained(
                'ProsusAI/finbert', num_labels=3
            )
            self.finbert = pipeline(  # pyright: ignore[reportCallIssue]
                'sentiment-analysis', model=model, tokenizer=tokenizer, device='cpu'
            )
            logger.info('FinBERT model loaded successfully')
        except Exception as e:
            logger.error(f'Failed to initialize FinBERT: {e}')
            self.finbert = None

    def _initialize_reddit(self):
        """Initialize Reddit API connection"""
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
            )
            self.reddit.read_only = True
            logger.info('Reddit API initialized successfully')
        except Exception as e:
            logger.error(f'Failed to initialize Reddit API: {e}')
            self.reddit = None

    def analyze_text_sentiment(self, text: str) -> dict | None:
        """Analyze sentiment of text using FinBERT"""
        if not self.finbert or not text or len(text.strip()) < 10:
            return None

        try:
            result = self.finbert(text[:512])[0]
            label = result['label'].lower()
            score = result['score']

            if label in ['positive', 'bullish']:
                normalized_label = 'positive'
            elif label in ['negative', 'bearish']:
                normalized_label = 'negative'
            else:
                normalized_label = 'neutral'

            return {'label': normalized_label, 'score': score}
        except Exception as e:
            logger.warning(f'Error analyzing text sentiment: {e}')
            return None

    def _is_relevant_post(self, post, ticker: str, company_name: str) -> bool:
        """
        Check if a Reddit post is relevant to the stock/company.
        Searches by company name + stock-related keywords instead of just ticker.
        """
        title_lower = post.title.lower()
        text_lower = post.selftext.lower()
        combined_text = f'{title_lower} {text_lower}'

        company_lower = company_name.lower()
        ticker_lower = ticker.lower()

        # Check if company name appears with stock-related keywords
        # add more keywords related to stock market
        stock_keywords = [
            'stock',
            'ticker',
            'shares',
            'equity',
            'trading',
            'invest',
            'buy',
            'sell',
            'portfolio',
            'market',
            'short',
            'bullish',
            'bearish',
            'volatility',
            'dividend',
            'earnings',
            'ipo',
            'merger',
            'acquisition',
            'sec',
            'nasdaq',
            'nyse',
            'sp500',
            'dowjones',
            'etf',
            'fund',
            'broker',
            'analyst',
            'valuation',
            'p/e',
            'price target',
            'volume',
        ]

        # Company name must be present
        if company_lower not in combined_text:
            return False

        # Check if any stock-related keyword appears near the company name
        # or if the ticker symbol appears (as fallback)
        has_stock_context = any(keyword in combined_text for keyword in stock_keywords)
        has_ticker_mention = ticker_lower in combined_text

        return has_stock_context or has_ticker_mention

    def fetch_reddit_data(self, ticker: str, conn, limit: int = 200) -> int:
        """
        Fetch and analyze Reddit posts for a ticker.
        Uses company name + stock keywords for more reliable matching.

        Returns:
            Number of posts successfully inserted
        """
        if not self.reddit or not self.finbert:
            logger.error('Reddit API or FinBERT not initialized')
            return 0

        # Get company name for better search relevance
        company_name = TICKER_TO_COMPANY.get(ticker, ticker)
        logger.info(f'Fetching Reddit data for {ticker} ({company_name})...')

        inserted_count = 0

        for sub_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(sub_name)
                posts_processed = 0

                # Search for posts mentioning the company name
                search_query = f'{company_name} stock'

                # Use search instead of just hot posts for better targeting
                for post in subreddit.search(
                    search_query, time_filter='month', limit=limit
                ):
                    # Verify relevance using more sophisticated check
                    if not self._is_relevant_post(post, ticker, company_name):
                        continue

                    text = f'{post.title} {post.selftext}'.strip()
                    sentiment = self.analyze_text_sentiment(text)

                    if not sentiment:
                        continue

                    success = insert_reddit_post(
                        conn=conn,
                        ticker=ticker,
                        post_id=post.id,
                        title=post.title,
                        content=post.selftext,
                        subreddit=sub_name,
                        score=post.score,
                        created_utc=int(post.created_utc),
                        url=f'https://reddit.com{post.permalink}',
                        sentiment_label=sentiment['label'],
                        sentiment_score=sentiment['score'],
                    )

                    if success:
                        inserted_count += 1

                    posts_processed += 1

                logger.info(
                    f'Processed {posts_processed} relevant posts from r/{sub_name} for {ticker}'
                )

                time.sleep(2)  # Increased delay to respect Reddit API rate limits

            except Exception as e:
                logger.error(f'Error fetching from r/{sub_name} for {ticker}: {e}')
                continue

        return inserted_count

    def fetch_finnhub_data(self, ticker: str, conn, days_back: int = 7) -> int:
        """
        Fetch and analyze FinHub news for a ticker.

        Returns:
            Number of articles successfully inserted
        """
        if not self.finbert or not FINNHUB_API_KEY:
            logger.error('FinBERT or FinHub API key not available')
            return 0

        logger.info(f'Fetching FinHub data for {ticker}...')

        from datetime import datetime, timedelta

        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        url = 'https://finnhub.io/api/v1/company-news'
        params = {
            'symbol': ticker,
            'from': start_date,
            'to': end_date,
            'token': FINNHUB_API_KEY,
        }

        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code != 200:
                logger.error(f'FinHub API error: {response.status_code}')
                return 0

            news_data = response.json()

            if not news_data or not isinstance(news_data, list):
                logger.warning(f'No news data found for {ticker}')
                return 0

            inserted_count = 0

            for article in news_data[:50]:
                try:
                    headline = article.get('headline', '')
                    summary = article.get('summary', '')
                    source = article.get('source', 'Unknown')
                    url = article.get('url', '')
                    published_at = article.get('datetime', 0)

                    if not headline:
                        continue

                    text_to_analyze = f'{headline} {summary}'.strip()
                    sentiment = self.analyze_text_sentiment(text_to_analyze)

                    if not sentiment:
                        continue

                    success = insert_finnhub_article(
                        conn=conn,
                        ticker=ticker,
                        article_id='',
                        headline=headline,
                        summary=summary,
                        source=source,
                        url=url,
                        published_at=published_at,
                        sentiment_label=sentiment['label'],
                        sentiment_score=sentiment['score'],
                    )

                    if success:
                        inserted_count += 1

                except Exception as e:
                    logger.warning(f'Error processing article: {e}')
                    continue

            logger.info(f'Processed {inserted_count} articles for {ticker}')

            time.sleep(1)

            return inserted_count

        except Exception as e:
            logger.error(f'Error fetching FinHub data for {ticker}: {e}')
            return 0

    def fetch_yfinance_data(self, ticker: str, conn, max_results: int = 50) -> int:
        """
        Fetch and analyze YFinance news for a ticker (especially useful for Indian stocks).

        Args:
            ticker: Stock ticker symbol (e.g., 'RELIANCE.NS', 'TATAMOTORS.BO')
            conn: Database connection
            max_results: Maximum number of news articles to fetch

        Returns:
            Number of articles successfully inserted
        """
        if not self.finbert:
            logger.error('FinBERT not initialized')
            return 0

        logger.info(f'Fetching YFinance news for {ticker}...')

        try:
            # Get the stock ticker object
            stock = yf.Ticker(ticker)

            # Fetch news
            news = stock.news

            if not news:
                logger.warning(f'No news data found for {ticker}')
                return 0

            inserted_count = 0

            for article in news[:max_results]:
                try:
                    provider_name = 'Unknown Provider'
                    content = article.get('content', None)
                    pubdate = 0
                    if content:
                        title = content.get('title', 'No Title')
                        summary = content.get('summary', 'No Summary')
                        pubdate = content.get('pubDate', 0)
                        if pubdate:
                            try:
                                dt = datetime.fromisoformat(
                                    pubdate.replace('Z', '+00:00')
                                )
                                pubdate = int(dt.timestamp())
                            except (ValueError, TypeError):
                                pubdate = 0

                        link = content.get('link', 'No Link')
                        provider = content.get('provider', None)
                        if provider:
                            provider_name = provider.get(
                                'displayName', 'Unknown Provider'
                            )
                        click_url = content.get('clickThroughUrl', None)
                        if click_url:
                            link = click_url.get('url', link)

                    if title != 'No Title' and summary != 'No Summary':
                        text_to_analyze = f'{title} {summary}'.strip()
                        sentiment = self.analyze_text_sentiment(text_to_analyze)

                    if not sentiment:
                        continue

                    success = insert_yfinance_news(
                        conn=conn,
                        ticker=ticker,
                        title=title,
                        summary=summary,
                        publisher=provider_name,
                        link=link,
                        published_at=pubdate,
                        sentiment_label=sentiment['label'],
                        sentiment_score=sentiment['score'],
                    )

                    if success:
                        inserted_count += 1

                except Exception as e:
                    logger.warning(f'Error processing YFinance article: {e}')
                    continue

            logger.info(f'Processed {inserted_count} YFinance articles for {ticker}')

            time.sleep(1)

            return inserted_count

        except Exception as e:
            logger.error(f'Error fetching YFinance data for {ticker}: {e}')
            return 0


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Fetch and analyze sentiment data from Reddit and FinHub'
    )
    parser.add_argument(
        '--tickers',
        nargs='+',
        default=DEFAULT_TICKERS,
        help='List of stock tickers to analyze (default: predefined list)',
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up old data (>30 days) before fetching new data',
    )
    parser.add_argument(
        '--reddit-only', action='store_true', help='Fetch only Reddit data'
    )
    parser.add_argument(
        '--finnhub-only', action='store_true', help='Fetch only FinHub data'
    )
    parser.add_argument(
        '--days-back',
        type=int,
        default=7,
        help='Days back to fetch FinHub news (default: 7)',
    )
    parser.add_argument(
        '--indian-stocks',
        action='store_true',
        help='Fetch data for Indian stocks using YFinance (uses default Indian tickers)',
    )
    parser.add_argument(
        '--yfinance-only',
        action='store_true',
        help='Fetch only YFinance data (for custom tickers)',
    )

    args = parser.parse_args()

    # Determine which tickers to use
    if args.indian_stocks:
        tickers_to_process = INDIAN_TICKERS
        logger.info('Using Indian stock tickers')
    else:
        tickers_to_process = args.tickers

    logger.info('=' * 80)
    logger.info(f'Starting sentiment data fetch at {datetime.now()}')
    logger.info(f'Tickers: {", ".join(tickers_to_process)}')
    logger.info('=' * 80)

    initialize_database()

    if args.cleanup:
        logger.info('Cleaning up old data...')
        cleanup_old_data(days_to_keep=30)

    fetcher = SentimentDataFetcher()

    conn = get_db_connection()

    total_reddit_posts = 0
    total_finnhub_articles = 0
    total_yfinance_articles = 0

    try:
        for ticker in tickers_to_process:
            logger.info(f'\n{"=" * 60}')
            logger.info(f'Processing {ticker}')
            logger.info(f'{"=" * 60}')

            # Check if this is an Indian stock (has .NS or .BO suffix) or YFinance-only mode
            is_indian_stock = ticker.endswith('.NS') or ticker.endswith('.BO')
            use_yfinance = is_indian_stock or args.yfinance_only

            if use_yfinance:
                # For Indian stocks or YFinance-only mode, use YFinance
                if not args.reddit_only and not args.finnhub_only:
                    yfinance_count = fetcher.fetch_yfinance_data(
                        ticker, conn, max_results=50
                    )
                    total_yfinance_articles += yfinance_count
                    logger.info(
                        f'✓ Inserted {yfinance_count} YFinance articles for {ticker}'
                    )
            else:
                # For US stocks, use Reddit and/or Finnhub
                if not args.finnhub_only and not args.yfinance_only:
                    reddit_count = fetcher.fetch_reddit_data(ticker, conn, limit=200)
                    total_reddit_posts += reddit_count
                    logger.info(f'✓ Inserted {reddit_count} Reddit posts for {ticker}')

                if not args.reddit_only and not args.yfinance_only:
                    finnhub_count = fetcher.fetch_finnhub_data(
                        ticker, conn, days_back=args.days_back
                    )
                    total_finnhub_articles += finnhub_count
                    logger.info(
                        f'✓ Inserted {finnhub_count} FinHub articles for {ticker}'
                    )

            conn.commit()

    except KeyboardInterrupt:
        logger.info('\n\nProcess interrupted by user')
    except Exception as e:
        logger.error(f'Unexpected error: {e}', exc_info=True)
    finally:
        conn.close()

    logger.info('\n' + '=' * 80)
    logger.info('SUMMARY')
    logger.info('=' * 80)
    logger.info(f'Total Reddit posts inserted: {total_reddit_posts}')
    logger.info(f'Total FinHub articles inserted: {total_finnhub_articles}')
    logger.info(f'Total YFinance articles inserted: {total_yfinance_articles}')
    logger.info(f'Completed at: {datetime.now()}')
    logger.info('=' * 80)


if __name__ == '__main__':
    main()
