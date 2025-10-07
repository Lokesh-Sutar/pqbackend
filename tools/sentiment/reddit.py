import logging
from typing import Any

from agno.tools import tool

from core.ticker_store import ticker_store
from tools.helper import SentimentAnalysisBase, logger_hook
from tools.sentiment.db_utils import get_recent_reddit_posts, get_reddit_stats

logger = logging.getLogger(__name__)


class RedditSentimentAnalyzer(SentimentAnalysisBase):
    """Reddit sentiment analyzer using pre-computed database results"""

    def __init__(self):
        super().__init__()

    def analyze_ticker_sentiment(self, ticker: str, days_back: int = 7) -> dict[str, Any]:
        """
        Retrieve and analyze pre-computed Reddit sentiment for a ticker.

        Args:
            ticker: Stock ticker symbol
            days_back: Number of days to look back (default: 7)

        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            stats = get_reddit_stats(ticker, days_back)

            if stats['total_posts'] == 0:
                return {
                    'tool': 'Reddit Sentiment',
                    'description': 'This tool fetches pre-computed sentiment scores for a particular ticker from Reddit',
                    'signal': 'No Data',
                    'justification': f'No Reddit posts found for {ticker} in the last {days_back} days. Please run fetch_sentiment_data.py to collect data.',
                    'details': {
                        'items_analyzed': 0,
                        'last_update': stats['last_update'],
                        'top_items': {'positive': [], 'negative': [], 'neutral': []},
                    },
                }

            posts = get_recent_reddit_posts(ticker, days_back, limit=10)

            post_headlines = {'positive': [], 'negative': [], 'neutral': []}
            analyzed_posts = []

            for post in posts:
                sentiment = post['sentiment']
                label = sentiment['label']

                post_data = {
                    'sentiment': sentiment,
                    'title': post['title'],
                    'score': post['score'],
                    'subreddit': post['subreddit'],
                }
                analyzed_posts.append(post_data)

                if len(post_headlines[label]) < 10:
                    post_headlines[label].append(
                        {
                            'title': post['title'],
                            'score': post['score'],
                            'subreddit': post['subreddit'],
                            'url': post.get('url', ''),
                        }
                    )

            sentiments = self.categorize_sentiment_counts(analyzed_posts)
            confidence_scores = [post['sentiment']['score'] for post in analyzed_posts]

            logger.info('Generating Reddit Sentiment...')
            return self.generate_trading_signal(
                ticker=ticker,
                description=f'This tool fetches pre-computed sentiment scores for {ticker} from Reddit (last {days_back} days). Data last updated: {stats["last_update"]}',
                tool_name='Reddit Sentiment',
                total_items=len(analyzed_posts),
                sentiments=sentiments,
                confidence_scores=confidence_scores,
                item_data={
                    'positive': post_headlines['positive'],
                    'negative': post_headlines['negative'],
                    'neutral': post_headlines['neutral'],
                },
                positive_threshold=60.0,
                negative_threshold=60.0,
                mixed_threshold=10.0,
            )

        except Exception as e:
            logger.error(f'Error retrieving Reddit sentiment: {e}', exc_info=True)
            return self.create_error_response(
                'Reddit Sentiment', f'Failed to retrieve sentiment data: {str(e)}'
            )


_analyzer = None


def get_analyzer() -> RedditSentimentAnalyzer:
    """Get or create the global analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = RedditSentimentAnalyzer()
    return _analyzer


@tool(
    name='get_reddit_sentiment',
    description='Returns a JSON object with a trading signal, confidence, justification, and top Reddit post headlines for a given stock ticker. Uses pre-computed sentiment analysis from database (updated every 12 hours). Output includes percentages, average confidence, and up to 10 headlines for positive, negative, and neutral sentiment.',
    tool_hooks=[logger_hook],
)
def get_reddit_sentiment(ticker: str, days_back: int = 7) -> dict[str, Any]:
    """
    Retrieve pre-computed Reddit sentiment for a stock ticker from database.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
        days_back: Number of days to look back (default: 7)

    Returns:
        Dictionary with sentiment analysis results
    """
    if not ticker:
        temp_analyzer = RedditSentimentAnalyzer()
        return temp_analyzer.create_error_response(
            'Reddit Sentiment', 'Invalid ticker provided'
        )
    ticker = ticker.upper().strip()
    ticker_store.add_ticker(ticker)
    days_back = max(1, min(days_back, 90))

    analyzer: RedditSentimentAnalyzer = get_analyzer()
    logger.info('Reddit Sentiment Generated!!')

    # random delay to not overwhelm LLM
    import random
    import time

    time.sleep(random.uniform(5, 15))

    return analyzer.analyze_ticker_sentiment(ticker, days_back)
