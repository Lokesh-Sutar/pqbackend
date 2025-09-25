import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests
from agno.tools import tool

from config import FINNHUB_API_KEY
from tools.utils import SentimentAnalysisBase, logger_hook


class FinHubSentimentAnalyzer(SentimentAnalysisBase):
    """FinHub news sentiment analyzer using FinBERT with rate limiting and error handling"""

    def __init__(self):
        super().__init__()
        self.api_key = FINNHUB_API_KEY
        self.base_url = 'https://finnhub.io/api/v1'
        self.last_request_time = 0
        self.min_request_interval = 1.0

    def _rate_limit_delay(self):
        """Implement rate limiting to avoid API throttling"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with rate limiting and error handling"""
        self._rate_limit_delay()

        params['token'] = self.api_key
        url = f'{self.base_url}/{endpoint}'

        try:
            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 429:
                print('Rate limit exceeded, waiting 60 seconds...')
                time.sleep(60)
                response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                print(
                    f'API request failed with status {response.status_code}: {response.text}'
                )
                return {}

        except requests.exceptions.Timeout:
            print('API request timed out')
            return {}
        except requests.exceptions.RequestException as e:
            print(f'API request failed: {e}')
            return {}

    def analyze_ticker_news_sentiment(
        self, ticker: str, days_back: int = 30, max_articles: int = 20
    ) -> Dict[str, Any]:
        """Analyze news sentiment for a specific ticker from FinHub"""
        if not self.finbert:
            return self.create_error_response(
                'FinHub News Sentiment', 'Failed to initialize sentiment model'
            )

        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        news_data = self._make_api_request(
            'company-news', {'symbol': ticker, 'from': start_date, 'to': end_date}
        )

        if not news_data or not isinstance(news_data, list):
            return self.generate_trading_signal(
                ticker=ticker,
                tool_name='FinHub News Sentiment',
                total_items=0,
                sentiments={'positive': 0, 'negative': 0, 'neutral': 0},
                confidence_scores=[],
                item_data={'positive': [], 'negative': [], 'neutral': []},
            )

        if isinstance(news_data, list) and len(news_data) > 0:
            limited_articles = []
            for i, article in enumerate(news_data):
                if i >= max_articles:
                    break
                limited_articles.append(article)
            return self._analyze_articles(ticker, limited_articles)
        else:
            return self._analyze_articles(ticker, [])

    def _analyze_articles(
        self, ticker: str, articles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze sentiment for a list of articles"""
        analyzed_articles = []
        article_data = {'positive': [], 'negative': [], 'neutral': []}

        for article in articles:
            try:
                headline = article.get('headline', '')
                summary = article.get('summary', '')
                source = article.get('source', 'Unknown')
                url = article.get('url', '')
                published_date = article.get('datetime', 0)

                if not headline:
                    continue

                text_to_analyze = f'{headline} {summary}'.strip()
                sentiment_result = self.analyze_text_sentiment(text_to_analyze)

                if sentiment_result:
                    article_date = (
                        datetime.fromtimestamp(published_date).strftime('%Y-%m-%d')
                        if published_date
                        else 'Unknown'
                    )

                    article_info = {
                        'headline': headline,
                        'source': source,
                        'date': article_date,
                        'url': url,
                        'confidence': round(sentiment_result['score'], 3),
                    }

                    analyzed_article = {
                        'sentiment': sentiment_result,
                        'data': article_info,
                    }
                    analyzed_articles.append(analyzed_article)

                    label = sentiment_result['label']
                    if len(article_data[label]) < 10:
                        article_data[label].append(article_info)

            except Exception as e:
                print(f'Error processing article: {e}')
                continue

        sentiments = self.categorize_sentiment_counts(analyzed_articles)
        confidence_scores = [
            article['sentiment']['score'] for article in analyzed_articles
        ]

        return self.generate_trading_signal(
            ticker=ticker,
            tool_name='FinHub News Sentiment',
            total_items=len(analyzed_articles),
            sentiments=sentiments,
            confidence_scores=confidence_scores,
            item_data=article_data,
            positive_threshold=60.0,
            negative_threshold=60.0,
            mixed_threshold=15.0,
        )


_analyzer = None


def get_analyzer():
    """Get or create the global analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = FinHubSentimentAnalyzer()
    return _analyzer


@tool(
    name='get_finnhub_news_sentiment',
    description='Returns a JSON object with trading signal, confidence, justification, and top news article headlines for a given stock ticker. Sentiment is analyzed using FinBERT on recent financial news from FinHub API. Output includes percentages, average confidence, and up to 10 articles for positive, negative, and neutral sentiment categories.',
    tool_hooks=[logger_hook],
)
def get_finnhub_news_sentiment(ticker: str, days_back: int = 90, max_articles: int = 50):
    """
    Analyze FinHub news sentiment for a stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
        days_back: Number of days to look back for news (default: 30)
        max_articles: Maximum number of articles to analyze (default: 20)

    Returns:
        Dictionary with sentiment analysis results and top articles
    """
    if not ticker or not isinstance(ticker, str):
        temp_analyzer = FinHubSentimentAnalyzer()
        return temp_analyzer.create_error_response(
            'FinHub News Sentiment', 'Invalid ticker provided'
        )

    days_back = max(1, min(days_back, 365))
    max_articles = max(1, min(max_articles, 100))

    ticker = ticker.upper().strip()
    analyzer = get_analyzer()
    return analyzer.analyze_ticker_news_sentiment(ticker, days_back, max_articles)
