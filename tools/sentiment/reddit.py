from typing import Any, Dict, List

import praw
from agno.tools import tool
from praw.exceptions import PRAWException

from config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
from tools.utils import SentimentAnalysisBase, logger_hook


class RedditSentimentAnalyzer(SentimentAnalysisBase):
    """Simplified Reddit sentiment analyzer using FinBERT"""

    def __init__(self):
        super().__init__()
        self.reddit = None
        self._initialize_reddit()

    def _initialize_reddit(self):
        """Initialize Reddit API connection with error handling"""
        try:
            client_id = REDDIT_CLIENT_ID
            client_secret = REDDIT_CLIENT_SECRET
            user_agent = REDDIT_USER_AGENT

            self.reddit = praw.Reddit(
                client_id=client_id, client_secret=client_secret, user_agent=user_agent
            )
            self.reddit.read_only = True
        except Exception as e:
            print(f'Failed to initialize Reddit API: {e}')
            self.reddit = None

    def analyze_ticker_sentiment(self, ticker: str, limit: int = 150) -> Dict[str, Any]:
        """Analyze sentiment for a specific ticker from Reddit"""
        if not self.reddit or not self.finbert:
            return self.create_error_response(
                'Reddit Sentiment', 'Failed to initialize Reddit API or sentiment model'
            )

        subreddits = ['stocks', 'investing', 'StockMarket', 'wallstreetbets']
        analyzed_posts = []
        post_headlines = {'positive': [], 'negative': [], 'neutral': []}

        try:
            for sub_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(sub_name)
                    posts_found = 0

                    for post in subreddit.top(limit=limit):
                        if (
                            ticker.lower() in post.title.lower()
                            or ticker.lower() in post.selftext.lower()
                        ):
                            text = f'{post.title} {post.selftext}'.strip()
                            sentiment_result = self.analyze_text_sentiment(text)

                            if sentiment_result:
                                post_data = {
                                    'sentiment': sentiment_result,
                                    'title': post.title,
                                    'score': post.score,
                                    'subreddit': sub_name,
                                }
                                analyzed_posts.append(post_data)

                                label = sentiment_result['label']
                                if len(post_headlines[label]) < 10:
                                    post_headlines[label].append(
                                        {
                                            'title': post.title,
                                            'score': post.score,
                                            'subreddit': sub_name,
                                        }
                                    )

                                posts_found += 1

                    if posts_found > 0:
                        print(
                            f'Found {posts_found} posts mentioning {ticker} in r/{sub_name}'
                        )

                except Exception as e:
                    print(f'Error accessing subreddit {sub_name}: {e}')
                    continue

            sentiments: Dict[str, int] = self.categorize_sentiment_counts(analyzed_posts)
            confidence_scores: list[Any] = [
                post['sentiment']['score'] for post in analyzed_posts
            ]

            return self.generate_trading_signal(
                ticker=ticker,
                description='This tool is used to fetch and measure the sentiment score of a particular ticker from Reddit',
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
            return self.create_error_response(
                'Reddit Sentiment', f'Failed to analyze sentiment: {str(e)}'
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
    description='Returns a JSON object with a trading signal, confidence, justification, and top Reddit post headlines for a given stock ticker. Sentiment is analyzed using FinBERT on recent posts from major finance subreddits. Output includes percentages, average confidence, and up to 10 headlines for positive, negative, and neutral sentiment.',
    tool_hooks=[logger_hook],
)
def get_reddit_sentiment(ticker: str) -> Dict[str, Any]:
    """
    Analyze Reddit sentiment for a stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'TSLA')

    Returns:
        Dictionary with sentiment analysis results
    """
    if not ticker or not isinstance(ticker, str):
        temp_analyzer = RedditSentimentAnalyzer()
        return temp_analyzer.create_error_response(
            'Reddit Sentiment', 'Invalid ticker provided'
        )

    ticker = ticker.upper().strip()
    analyzer: RedditSentimentAnalyzer = get_analyzer()
    return analyzer.analyze_ticker_sentiment(ticker)
