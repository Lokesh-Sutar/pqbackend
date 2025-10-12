import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import praw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentiment_common import (
    DEFAULT_TICKERS,
    TICKER_TO_COMPANY,
    analyze_sentiment,
    initialize_finbert,
    setup_logging,
)

from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from tools.sentiment.db_utils import (
    get_db_connection,
    initialize_database,
    insert_reddit_post,
)

logger = logging.getLogger(__name__)

SUBREDDITS = [
    'investing',
    'stocks',
    'StockMarket',
    'wallstreetbets',
    'trading',
    'Daytrading',
    'options',
    'algotrading',
    'technicalanalysis',
    'ValueInvesting',
    'dividends',
    'DividendInvesting',
    'Bogleheads',
    'financialindependence',
    'personalfinance',
    'pennystocks',
    'smallstreetbets',
    'RobinHood',
    'Wallstreetbetnew',
    'InvestingIdeas',
    'StockPicks',
    'StockMarketResearch',
    'InvestingForBeginners',
]


def fetch_reddit_sentiment(ticker: str, finbert, reddit, conn, limit: int = 200) -> int:
    """Fetch and analyze Reddit posts for a ticker"""
    company_name = TICKER_TO_COMPANY.get(ticker, ticker)
    logger.info(f'Fetching Reddit data for {ticker} ({company_name})...')

    inserted_count = 0

    for sub_name in SUBREDDITS:
        try:
            subreddit = reddit.subreddit(sub_name)
            search_query = f'{company_name} stock'

            for post in subreddit.search(
                search_query, time_filter='month', limit=limit
            ):
                title_lower = post.title.lower()
                text_lower = post.selftext.lower()
                combined = f'{title_lower} {text_lower}'

                # Check relevance
                if company_name.lower() not in combined:
                    continue

                text = f'{post.title} {post.selftext}'.strip()
                sentiment = analyze_sentiment(finbert, text)

                if not sentiment:
                    continue

                created_utc = int(post.created_utc)
                created_at_iso = datetime.fromtimestamp(created_utc).strftime('%Y-%m-%d')

                success = insert_reddit_post(
                    conn=conn,
                    ticker=ticker,
                    post_id=post.id,
                    title=post.title,
                    content=post.selftext,
                    subreddit=sub_name,
                    score=post.score,
                    created_utc=created_utc,
                    created_at_iso=created_at_iso,
                    url=f'https://reddit.com{post.permalink}',
                    sentiment_label=sentiment['label'],
                    sentiment_score=sentiment['score'],
                )

                if success:
                    inserted_count += 1

            logger.info(f'Processed r/{sub_name} for {ticker}')
            time.sleep(2)

        except Exception as e:
            logger.error(f'Error in r/{sub_name} for {ticker}: {e}')
            continue

    return inserted_count


def main():
    parser = argparse.ArgumentParser(description='Fetch Reddit sentiment data')
    parser.add_argument('--tickers', nargs='+', default=DEFAULT_TICKERS)
    args = parser.parse_args()

    setup_logging()
    logger.info('Starting Reddit sentiment fetch')

    initialize_database()
    finbert = initialize_finbert()

    if not finbert:
        logger.error('Failed to initialize FinBERT')
        return

    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )
        reddit.read_only = True
        logger.info('Reddit API initialized')
    except Exception as e:
        logger.error(f'Failed to initialize Reddit: {e}')
        return

    conn = get_db_connection()
    total = 0

    try:
        for ticker in args.tickers:
            count = fetch_reddit_sentiment(ticker, finbert, reddit, conn)
            total += count
            logger.info(f'✓ Inserted {count} Reddit posts for {ticker}')
            conn.commit()
    except KeyboardInterrupt:
        logger.info('Interrupted by user')
    finally:
        conn.close()

    logger.info(f'Total Reddit posts inserted: {total}')


if __name__ == '__main__':
    main()
