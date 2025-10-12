import argparse
import logging
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentiment_common import (
    DEFAULT_TICKERS,
    analyze_sentiment,
    initialize_finbert,
    setup_logging,
)

from config import FINNHUB_API_KEY
from tools.sentiment.db_utils import (
    get_db_connection,
    initialize_database,
    insert_finnhub_article,
)

logger = logging.getLogger(__name__)


def fetch_finhub_sentiment(ticker: str, finbert, conn, days_back: int = 7) -> int:
    """Fetch and analyze FinHub news for a ticker"""
    logger.info(f'Fetching FinHub data for {ticker}...')

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
            logger.warning(f'No news data for {ticker}')
            return 0

        inserted_count = 0

        for article in news_data:
            try:
                headline = article.get('headline', '')
                summary = article.get('summary', '')
                source = article.get('source', 'Unknown')
                url = article.get('url', '')
                published_at = article.get('datetime', 0)
                published_at_iso = (
                    datetime.fromtimestamp(published_at).strftime('%Y-%m-%d')
                    if published_at
                    else 'NA'
                )

                if not headline:
                    continue

                text = f'{headline} {summary}'.strip()
                sentiment = analyze_sentiment(finbert, text)

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
                    published_at_iso=published_at_iso,
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


def main():
    parser = argparse.ArgumentParser(description='Fetch FinHub sentiment data')
    parser.add_argument('--tickers', nargs='+', default=DEFAULT_TICKERS)
    parser.add_argument('--days-back', type=int, default=7)
    args = parser.parse_args()

    setup_logging()
    logger.info('Starting FinHub sentiment fetch')

    if not FINNHUB_API_KEY:
        logger.error('FINNHUB_API_KEY not configured')
        return

    initialize_database()
    finbert = initialize_finbert()

    if not finbert:
        logger.error('Failed to initialize FinBERT')
        return

    conn = get_db_connection()
    total = 0

    try:
        for ticker in args.tickers:
            count = fetch_finhub_sentiment(ticker, finbert, conn, args.days_back)
            total += count
            logger.info(f'✓ Inserted {count} FinHub articles for {ticker}')
            conn.commit()
    except KeyboardInterrupt:
        logger.info('Interrupted by user')
    finally:
        conn.close()

    logger.info(f'Total FinHub articles inserted: {total}')


if __name__ == '__main__':
    main()
