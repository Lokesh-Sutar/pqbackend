import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

import yfinance as yf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentiment_common import (
    INDIAN_TICKERS,
    analyze_sentiment,
    initialize_finbert,
    setup_logging,
)

from tools.sentiment.db_utils import (
    get_db_connection,
    initialize_database,
    insert_yfinance_news,
)

logger = logging.getLogger(__name__)


def fetch_yfinance_sentiment(ticker: str, finbert, conn, max_results: int = 50) -> int:
    """Fetch and analyze YFinance news for a ticker"""
    logger.info(f'Fetching YFinance news for {ticker}...')

    try:
        stock = yf.Ticker(ticker)
        news = stock.news

        if not news:
            logger.warning(f'No news data for {ticker}')
            return 0

        inserted_count = 0

        for article in news[:max_results]:
            try:
                provider_name = 'Unknown Provider'
                content = article.get('content', {})
                title = content.get('title', 'No Title')
                summary = content.get('summary', 'No Summary')
                link = content.get('link', 'No Link')

                pubdate = content.get('pubDate', 0)
                pubdate_iso = 'NA'
                if pubdate:
                    try:
                        dt = datetime.fromisoformat(pubdate.replace('Z', '+00:00'))
                        pubdate = int(dt.timestamp())
                        pubdate_iso = dt.strftime('%Y-%m-%d')
                    except (ValueError, TypeError):
                        pubdate = 0
                        pubdate_iso = 'NA'

                provider = content.get('provider', {})
                if provider:
                    provider_name = provider.get('displayName', 'Unknown Provider')

                click_url = content.get('clickThroughUrl', {})
                if click_url:
                    link = click_url.get('url', link)

                if title == 'No Title' or summary == 'No Summary':
                    continue

                text = f'{title} {summary}'.strip()
                sentiment = analyze_sentiment(finbert, text)

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
                    published_at_iso=pubdate_iso,
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
    parser = argparse.ArgumentParser(description='Fetch YFinance sentiment data')
    parser.add_argument('--tickers', nargs='+', default=INDIAN_TICKERS)
    parser.add_argument('--max-results', type=int, default=50)
    args = parser.parse_args()

    setup_logging()
    logger.info('Starting YFinance sentiment fetch')

    initialize_database()
    finbert = initialize_finbert()

    if not finbert:
        logger.error('Failed to initialize FinBERT')
        return

    conn = get_db_connection()
    total = 0

    try:
        for ticker in args.tickers:
            count = fetch_yfinance_sentiment(ticker, finbert, conn, args.max_results)
            total += count
            logger.info(f'✓ Inserted {count} YFinance articles for {ticker}')
            conn.commit()
    except KeyboardInterrupt:
        logger.info('Interrupted by user')
    finally:
        conn.close()

    logger.info(f'Total YFinance articles inserted: {total}')


if __name__ == '__main__':
    main()
