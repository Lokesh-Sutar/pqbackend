import logging
from typing import Any

from agno.tools import tool

from tools.helper import SentimentAnalysisBase, logger_hook
from tools.sentiment.db_utils import get_recent_yfinance_news, get_yfinance_stats

logger = logging.getLogger(__name__)


class YFinanceSentimentAnalyzer(SentimentAnalysisBase):
    """YFinance news sentiment analyzer using pre-computed database results"""

    def __init__(self):
        super().__init__()

    def analyze_ticker_news_sentiment(
        self, ticker: str, days_back: int = 7
    ) -> dict[str, Any]:
        """
        Retrieve and analyze pre-computed YFinance news sentiment for a ticker.

        Args:
            ticker: Stock ticker symbol (including suffix like .NS, .BSE, .BO for Indian stocks)
            days_back: Number of days to look back (default: 7)

        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            stats = get_yfinance_stats(ticker, days_back)

            if stats['total_articles'] == 0:
                logger.info(
                    f'No YFinance news found for {ticker} in the last {days_back} days.'
                )
                return {
                    'tool': 'YFinance News Sentiment',
                    'description': 'This tool fetches pre-computed sentiment scores for a particular ticker from YFinance news',
                    'signal': 'No Data',
                    'justification': f'No YFinance news found for {ticker} in the last {days_back} days. Please run fetch_sentiment_data.py to collect data.',
                    'details': {
                        'items_analyzed': 0,
                        'last_update': stats['last_update'],
                        'top_items': {'positive': [], 'negative': [], 'neutral': []},
                    },
                }

            articles = get_recent_yfinance_news(ticker, days_back, limit=10)

            article_data = {'positive': [], 'negative': [], 'neutral': []}
            analyzed_articles = []

            for article in articles:
                sentiment = article['sentiment']
                label = sentiment['label']

                article_info = {
                    'title': article['title'],
                    'publisher': article['publisher'],
                    'date': article['published_date'],
                    'link': article['link'],
                    'confidence': round(sentiment['score'], 3),
                }

                analyzed_article = {'sentiment': sentiment, 'data': article_info}
                analyzed_articles.append(analyzed_article)

                if len(article_data[label]) < 10:
                    article_data[label].append(article_info)

            sentiments = self.categorize_sentiment_counts(analyzed_articles)
            confidence_scores = [
                article['sentiment']['score'] for article in analyzed_articles
            ]

            logger.info('Generating YFinance Sentiment...')

            return self.generate_trading_signal(
                ticker=ticker,
                description=f'This tool fetches pre-computed sentiment scores for {ticker} from YFinance news (last {days_back} days). Data last updated: {stats["last_update"]}. Particularly useful for Indian stocks with suffixes like .NS, .BSE, or .BO',
                tool_name='YFinance News Sentiment',
                total_items=len(analyzed_articles),
                sentiments=sentiments,
                confidence_scores=confidence_scores,
                item_data=article_data,
                positive_threshold=60.0,
                negative_threshold=60.0,
                mixed_threshold=15.0,
            )

        except Exception as e:
            logger.error(f'Error retrieving YFinance sentiment: {e}', exc_info=True)
            return self.create_error_response(
                'YFinance News Sentiment', f'Failed to retrieve sentiment data: {str(e)}'
            )


_analyzer = None


def get_analyzer():
    """Get or create the global analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = YFinanceSentimentAnalyzer()
    return _analyzer


@tool(
    name='get_yfinance_news_sentiment',
    description='Returns a JSON object with trading signal, confidence, justification, and top news article titles for a given stock ticker. Uses pre-computed sentiment analysis from database (updated every 12 hours). Output includes percentages, average confidence, and up to 10 articles for positive, negative, and neutral sentiment categories. Particularly useful for Indian stocks with suffixes like .NS (NSE), .BSE, or .BO (Bombay Stock Exchange), such as RELIANCE.NS, TCS.NS, INFY.NS, etc.',
    tool_hooks=[logger_hook],
)
def get_yfinance_news_sentiment(ticker: str, days_back: int = 7):
    """
    Retrieve pre-computed YFinance news sentiment for a stock ticker from database.

    Args:
        ticker: Stock ticker symbol (e.g., 'RELIANCE.NS', 'TCS.NS', 'AAPL')
        days_back: Number of days to look back (default: 7)

    Returns:
        Dictionary with sentiment analysis results and top articles
    """
    if not ticker:
        temp_analyzer = YFinanceSentimentAnalyzer()
        return temp_analyzer.create_error_response(
            'YFinance News Sentiment', 'Invalid ticker provided'
        )

    days_back = max(1, min(days_back, 90))

    ticker = ticker.upper().strip()
    analyzer = get_analyzer()
    logger.info('YFinance Sentiment Generated!!')

    # random delay to not overwhelm LLM
    import random
    import time

    time.sleep(random.uniform(5, 15))

    return analyzer.analyze_ticker_news_sentiment(ticker, days_back)
