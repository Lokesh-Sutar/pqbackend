import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DB_DIR = Path(__file__).resolve().parent.parent.parent / 'data' / 'databases'
DB_PATH = DB_DIR / 'sentiment_data.db'


def get_db_connection() -> sqlite3.Connection:
    """Create and return a database connection"""
    DB_DIR.mkdir(exist_ok=True)
    conn = sqlite3.Connection(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Initialize database schema for sentiment data storage"""
    conn = get_db_connection()
    cursor = conn.cursor()

    _ = cursor.execute("""
        CREATE TABLE IF NOT EXISTS reddit_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            post_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            subreddit TEXT NOT NULL,
            score INTEGER,
            created_utc INTEGER,
            url TEXT,
            sentiment_label TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, post_id)
        )
    """)

    _ = cursor.execute("""
        CREATE TABLE IF NOT EXISTS finnhub_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            article_id TEXT,
            headline TEXT NOT NULL,
            summary TEXT,
            source TEXT,
            url TEXT,
            published_at INTEGER,
            sentiment_label TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, headline, published_at)
        )
    """)

    _ = cursor.execute("""
        CREATE TABLE IF NOT EXISTS yfinance_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            publisher TEXT,
            link TEXT,
            published_at INTEGER,
            sentiment_label TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, title, published_at)
        )
    """)

    _ = cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reddit_ticker_analyzed 
        ON reddit_posts(ticker, analyzed_at DESC)
    """)

    _ = cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_finnhub_ticker_analyzed 
        ON finnhub_articles(ticker, analyzed_at DESC)
    """)

    _ = cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_reddit_ticker_created 
        ON reddit_posts(ticker, created_utc DESC)
    """)

    _ = cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_finnhub_ticker_published 
        ON finnhub_articles(ticker, published_at DESC)
    """)

    _ = cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_yfinance_ticker_analyzed 
        ON yfinance_news(ticker, analyzed_at DESC)
    """)

    _ = cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_yfinance_ticker_published 
        ON yfinance_news(ticker, published_at DESC)
    """)

    conn.commit()
    conn.close()
    logger.info(f'Database initialized at {DB_PATH}')


def insert_reddit_post(
    conn: sqlite3.Connection,
    ticker: str,
    post_id: str,
    title: str,
    content: str,
    subreddit: str,
    score: int,
    created_utc: int,
    url: str,
    sentiment_label: str,
    sentiment_score: float,
) -> bool:
    """Insert a Reddit post with sentiment data into database. Skips if post already exists."""
    try:
        cursor = conn.cursor()

        cursor.execute(
            'SELECT 1 FROM reddit_posts WHERE post_id = ? AND ticker = ?',
            (post_id, ticker.upper()),
        )
        if cursor.fetchone():
            logger.debug(f'Post {post_id} for {ticker} already exists, skipping')
            return False

        cursor.execute(
            """
            INSERT INTO reddit_posts 
            (ticker, post_id, title, content, subreddit, score, created_utc, url, 
             sentiment_label, sentiment_score, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticker.upper(),
                post_id,
                title,
                content,
                subreddit,
                score,
                created_utc,
                url,
                sentiment_label,
                sentiment_score,
                datetime.now().isoformat(),
            ),
        )
        return True
    except sqlite3.IntegrityError as e:
        logger.debug(f'Post already exists or duplicate: {e}')
        return False
    except Exception as e:
        logger.error(f'Error inserting Reddit post: {e}')
        return False


def insert_finnhub_article(
    conn: sqlite3.Connection,
    ticker: str,
    article_id: str,
    headline: str,
    summary: str,
    source: str,
    url: str,
    published_at: int,
    sentiment_label: str,
    sentiment_score: float,
) -> bool:
    """Insert a FinHub article with sentiment data into database. Skips if article already exists."""
    try:
        cursor = conn.cursor()

        cursor.execute(
            'SELECT 1 FROM finnhub_articles WHERE ticker = ? AND headline = ? AND published_at = ?',
            (ticker.upper(), headline, published_at),
        )
        if cursor.fetchone():
            logger.debug(
                f'Article "{headline[:50]}..." for {ticker} already exists, skipping'
            )
            return False

        cursor.execute(
            """
            INSERT INTO finnhub_articles 
            (ticker, article_id, headline, summary, source, url, published_at, 
             sentiment_label, sentiment_score, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticker.upper(),
                article_id,
                headline,
                summary,
                source,
                url,
                published_at,
                sentiment_label,
                sentiment_score,
                datetime.now().isoformat(),
            ),
        )
        return True
    except sqlite3.IntegrityError as e:
        logger.debug(f'Article already exists or duplicate: {e}')
        return False
    except Exception as e:
        logger.error(f'Error inserting FinHub article: {e}')
        return False


def insert_yfinance_news(
    conn: sqlite3.Connection,
    ticker: str,
    title: str,
    summary: str,
    publisher: str,
    link: str,
    published_at: int,
    sentiment_label: str,
    sentiment_score: float,
) -> bool:
    """Insert a YFinance news article with sentiment data into database. Skips if article already exists."""
    try:
        cursor = conn.cursor()

        cursor.execute(
            'SELECT 1 FROM yfinance_news WHERE ticker = ? AND title = ? AND published_at = ?',
            (ticker.upper(), title, published_at),
        )
        if cursor.fetchone():
            logger.debug(
                f'YFinance article "{title[:50]}..." for {ticker} already exists, skipping'
            )
            return False

        cursor.execute(
            """
            INSERT INTO yfinance_news 
            (ticker, title, summary, publisher, link, published_at, 
             sentiment_label, sentiment_score, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticker.upper(),
                title,
                summary,
                publisher,
                link,
                published_at,
                sentiment_label,
                sentiment_score,
                datetime.now().isoformat(),
            ),
        )
        return True
    except sqlite3.IntegrityError as e:
        logger.debug(f'YFinance article already exists or duplicate: {e}')
        return False
    except Exception as e:
        logger.error(f'Error inserting YFinance article: {e}')
        return False


def get_recent_reddit_posts(
    ticker: str, days_back: int = 7, limit: int = 100
) -> list[dict[str, Any]]:
    """
    Retrieve recent Reddit posts for a ticker from database.

    Args:
        ticker: Stock ticker symbol
        days_back: Number of days to look back (default: 7)
        limit: Maximum number of posts to retrieve (default: 100)

    Returns:
        List of dictionaries containing post data and sentiment
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # cutoff_time = datetime.now() - timedelta(days=days_back)
    # cutoff_timestamp = int(cutoff_time.timestamp())

    _ = cursor.execute(
        """
        SELECT * FROM reddit_posts 
        WHERE ticker = ?
        ORDER BY created_utc DESC
        LIMIT ?
        """,
        (ticker.upper(), limit),
    )

    rows = cursor.fetchall()
    conn.close()

    posts = []
    for row in rows:
        posts.append(
            {
                'post_id': row['post_id'],
                'title': row['title'],
                'content': row['content'],
                'subreddit': row['subreddit'],
                'score': row['score'],
                'created_utc': row['created_utc'],
                'url': row['url'],
                'sentiment': {
                    'label': row['sentiment_label'],
                    'score': row['sentiment_score'],
                },
                'analyzed_at': row['analyzed_at'],
            }
        )

    return posts


def get_recent_finnhub_articles(
    ticker: str, days_back: int = 7, limit: int = 100
) -> list[dict[str, Any]]:
    """
    Retrieve recent FinHub articles for a ticker from database.

    Args:
        ticker: Stock ticker symbol
        days_back: Number of days to look back (default: 7)
        limit: Maximum number of articles to retrieve (default: 100)

    Returns:
        List of dictionaries containing article data and sentiment
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # cutoff_time = datetime.now() - timedelta(days=days_back)
    # cutoff_timestamp = int(cutoff_time.timestamp())

    _ = cursor.execute(
        """
        SELECT * FROM finnhub_articles 
        WHERE ticker = ?
        ORDER BY published_at DESC
        LIMIT ?
        """,
        (ticker.upper(), limit),
    )

    rows = cursor.fetchall()
    conn.close()

    articles = []
    for row in rows:
        published_date = (
            datetime.fromtimestamp(row['published_at']).strftime('%Y-%m-%d')
            if row['published_at']
            else 'Unknown'
        )

        articles.append(
            {
                'article_id': row['article_id'],
                'headline': row['headline'],
                'summary': row['summary'],
                'source': row['source'],
                'url': row['url'],
                'published_at': row['published_at'],
                'published_date': published_date,
                'sentiment': {
                    'label': row['sentiment_label'],
                    'score': row['sentiment_score'],
                },
                'analyzed_at': row['analyzed_at'],
            }
        )

    return articles


def get_recent_yfinance_news(
    ticker: str, days_back: int = 7, limit: int = 100
) -> list[dict[str, Any]]:
    """
    Retrieve recent YFinance news for a ticker from database.

    Args:
        ticker: Stock ticker symbol
        days_back: Number of days to look back (default: 7)
        limit: Maximum number of articles to retrieve (default: 100)

    Returns:
        List of dictionaries containing article data and sentiment
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # cutoff_time = datetime.now() - timedelta(days=days_back)
    # cutoff_timestamp = int(cutoff_time.timestamp())

    _ = cursor.execute(
        """
        SELECT * FROM yfinance_news 
        WHERE ticker = ?
        ORDER BY published_at DESC
        LIMIT ?
        """,
        (ticker.upper(), limit),
    )

    rows = cursor.fetchall()
    conn.close()

    articles = []
    for row in rows:
        published_date = (
            datetime.fromtimestamp(row['published_at']).strftime('%Y-%m-%d')
            if row['published_at']
            else 'Unknown'
        )

        articles.append(
            {
                'title': row['title'],
                'publisher': row['publisher'],
                'link': row['link'],
                'published_at': row['published_at'],
                'published_date': published_date,
                'sentiment': {
                    'label': row['sentiment_label'],
                    'score': row['sentiment_score'],
                },
                'analyzed_at': row['analyzed_at'],
            }
        )

    return articles


def get_reddit_stats(ticker: str, days_back: int = 7) -> dict[str, Any]:
    """Get statistics about Reddit posts for a ticker"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # cutoff_time = datetime.now() - timedelta(days=days_back)
    # cutoff_timestamp = int(cutoff_time.timestamp())

    _ = cursor.execute(
        """
        SELECT 
            COUNT(*) as total,
            AVG(sentiment_score) as avg_confidence,
            MAX(analyzed_at) as last_update
        FROM reddit_posts 
        WHERE ticker = ?
        """,
        (ticker.upper(),),
    )

    row = cursor.fetchone()
    conn.close()

    return {
        'total_posts': row['total'] if row else 0,
        'avg_confidence': row['avg_confidence'] if row else 0,
        'last_update': row['last_update'] if row else None,
    }


def get_finnhub_stats(ticker: str, days_back: int = 7) -> dict[str, Any]:
    """Get statistics about FinHub articles for a ticker"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # cutoff_time = datetime.now() - timedelta(days=days_back)
    # cutoff_timestamp = int(cutoff_time.timestamp())

    _ = cursor.execute(
        """
        SELECT 
            COUNT(*) as total,
            AVG(sentiment_score) as avg_confidence,
            MAX(analyzed_at) as last_update
        FROM finnhub_articles 
        WHERE ticker = ?
        """,
        (ticker.upper(),),
    )

    row = cursor.fetchone()
    conn.close()

    return {
        'total_articles': row['total'] if row else 0,
        'avg_confidence': row['avg_confidence'] if row else 0,
        'last_update': row['last_update'] if row else None,
    }


def get_yfinance_stats(ticker: str, days_back: int = 7) -> dict[str, Any]:
    """Get statistics about YFinance news for a ticker"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # cutoff_time = datetime.now() - timedelta(days=days_back)
    # cutoff_timestamp = int(cutoff_time.timestamp())

    _ = cursor.execute(
        """
        SELECT 
            COUNT(*) as total,
            AVG(sentiment_score) as avg_confidence,
            MAX(analyzed_at) as last_update
        FROM yfinance_news 
        WHERE ticker = ?
        """,
        (ticker.upper(),),
    )

    row = cursor.fetchone()
    conn.close()

    return {
        'total_articles': row['total'] if row else 0,
        'avg_confidence': row['avg_confidence'] if row else 0,
        'last_update': row['last_update'] if row else None,
    }


def cleanup_old_data(days_to_keep: int = 500):
    """Remove sentiment data older than specified days"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cutoff_time = datetime.now() - timedelta(days=days_to_keep)
    cutoff_timestamp = int(cutoff_time.timestamp())

    _ = cursor.execute(
        'DELETE FROM reddit_posts WHERE created_utc < ?', (cutoff_timestamp,)
    )
    reddit_deleted = cursor.rowcount

    _ = cursor.execute(
        'DELETE FROM finnhub_articles WHERE published_at < ?', (cutoff_timestamp,)
    )
    finnhub_deleted = cursor.rowcount

    _ = cursor.execute(
        'DELETE FROM yfinance_news WHERE published_at < ?', (cutoff_timestamp,)
    )
    yfinance_deleted = cursor.rowcount

    conn.commit()
    conn.close()

    logger.info(
        f'Cleaned up {reddit_deleted} Reddit posts, {finnhub_deleted} FinHub articles, '
        f'and {yfinance_deleted} YFinance articles older than {days_to_keep} days'
    )

    return {
        'reddit_deleted': reddit_deleted,
        'finnhub_deleted': finnhub_deleted,
        'yfinance_deleted': yfinance_deleted,
    }
