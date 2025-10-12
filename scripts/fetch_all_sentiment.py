import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import praw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fetch_finhub_sentiment import fetch_finhub_sentiment
from fetch_reddit_sentiment import fetch_reddit_sentiment
from fetch_yfinance_sentiment import fetch_yfinance_sentiment
from sentiment_common import (
    DEFAULT_TICKERS,
    INDIAN_TICKERS,
    initialize_finbert,
    setup_logging,
)

from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from tools.sentiment.db_utils import (
    cleanup_old_data,
    get_db_connection,
    initialize_database,
)

logger = logging.getLogger(__name__)


def run_reddit(tickers):
    """Run Reddit sentiment fetch"""
    setup_logging()
    logger.info('Starting Reddit fetch process')

    finbert = initialize_finbert()
    if not finbert:
        return

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )
    reddit.read_only = True

    conn = get_db_connection()
    total = 0

    for ticker in tickers:
        count = fetch_reddit_sentiment(ticker, finbert, reddit, conn)
        total += count
        conn.commit()

    conn.close()
    logger.info(f'Reddit process complete: {total} posts')


def run_finhub(tickers, days_back):
    """Run FinHub sentiment fetch"""
    setup_logging()
    logger.info('Starting FinHub fetch process')

    finbert = initialize_finbert()
    if not finbert:
        return

    conn = get_db_connection()
    total = 0

    for ticker in tickers:
        count = fetch_finhub_sentiment(ticker, finbert, conn, days_back)
        total += count
        conn.commit()

    conn.close()
    logger.info(f'FinHub process complete: {total} articles')


def run_yfinance(tickers, max_results):
    """Run YFinance sentiment fetch"""
    setup_logging()
    logger.info('Starting YFinance fetch process')

    finbert = initialize_finbert()
    if not finbert:
        return

    conn = get_db_connection()
    total = 0

    for ticker in tickers:
        count = fetch_yfinance_sentiment(ticker, finbert, conn, max_results)
        total += count
        conn.commit()

    conn.close()
    logger.info(f'YFinance process complete: {total} articles')


def main():
    parser = argparse.ArgumentParser(description='Fetch all sentiment data')
    parser.add_argument('--tickers', nargs='+', default=DEFAULT_TICKERS)
    parser.add_argument('--indian-stocks', action='store_true')
    parser.add_argument('--cleanup', action='store_true')
    parser.add_argument('--days-back', type=int, default=90)
    parser.add_argument('--max-results', type=int, default=500)
    args = parser.parse_args()

    setup_logging()
    logger.info('=' * 80)
    logger.info(f'Starting sentiment data fetch at {datetime.now()}')
    logger.info('=' * 80)

    initialize_database()

    if args.cleanup:
        logger.info('Cleaning up old data...')
        cleanup_old_data(days_to_keep=30)

    tickers = INDIAN_TICKERS if args.indian_stocks else args.tickers
    is_indian = args.indian_stocks or any(
        t.endswith('.NS') or t.endswith('.BO') for t in tickers
    )

    finbert = initialize_finbert()
    if not finbert:
        return

    conn = get_db_connection()

    try:
        if is_indian:
            total = 0
            for ticker in tickers:
                count = fetch_yfinance_sentiment(
                    ticker, finbert, conn, args.max_results
                )
                total += count
                logger.info(f'✓ {count} YFinance articles for {ticker}')
                conn.commit()
            logger.info(f'Total: {total} YFinance articles')
        else:
            reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT,
            )
            reddit.read_only = True

            total_finhub = 0
            total_yfinance = 0
            total_reddit = 0

            for ticker in tickers:
                finhub_count = fetch_finhub_sentiment(
                    ticker, finbert, conn, args.days_back
                )
                total_finhub += finhub_count
                logger.info(f'✓ {ticker}: {finhub_count} FinHub')
                conn.commit()

                yfinance_count = fetch_yfinance_sentiment(
                    ticker, finbert, conn, args.max_results
                )
                total_yfinance += yfinance_count
                logger.info(f'✓ {ticker}: {yfinance_count} YFinance')
                conn.commit()

                reddit_count = fetch_reddit_sentiment(ticker, finbert, reddit, conn)
                total_reddit += reddit_count
                logger.info(f'✓ {ticker}: {reddit_count} Reddit')
                conn.commit()

            logger.info(
                f'Total: {total_finhub} FinHub, {total_yfinance} YFinance, {total_reddit} Reddit'
            )
    finally:
        conn.close()

    logger.info('=' * 80)
    logger.info(f'Completed at {datetime.now()}')
    logger.info('=' * 80)


if __name__ == '__main__':
    main()
