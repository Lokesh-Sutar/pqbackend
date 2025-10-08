import logging
import threading
from pathlib import Path
from typing import Any, Callable, List, Optional

import pandas as pd
import yfinance as yf
from pandas import DataFrame

from utils.ticker_store import ticker_store

logger = logging.getLogger(__name__)


def logger_hook(function_name: str, function_call: Callable, arguments: dict[str, Any]):
    """Hook function that wraps the tool execution"""
    logger.info(f'Calling {function_name} with arguments: {arguments}')
    result = function_call(**arguments)
    logger.debug(f'Function {function_name} completed')
    return result


def get_ticker(ticker: str) -> pd.DataFrame:
    """Load ticker data from Yahoo Finance, fallback to CSV file"""

    ticker_store.add_ticker(ticker)
    logger.info(f'Called ticker_store.add_ticker({ticker})')

    try:
        logger.info(f'Fetching {ticker} from yfinance')
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period='2y')
        df.columns = df.columns.str.lower()
        return df
    except Exception as e:
        logger.warning(f'Failed to fetch {ticker} from yfinance: {e}, trying local CSV')
        data_dir = Path(__file__).resolve().parent.parent / 'data' / 'cache'
        df_file = data_dir / f'{ticker}.csv'
        df: pd.DataFrame = pd.read_csv(df_file)
        logger.info(f'Loaded {ticker} from CSV')
        return df


def validate_data(
    df: DataFrame, required_columns: list, min_periods: int, tool_name: str
) -> dict | None:
    """Centralized data validation"""
    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        return {
            'tool': tool_name,
            'signal': 'Insufficient Data',
            'justification': f'Missing required columns: {missing_cols}',
            'details': {},
        }

    if len(df) < min_periods:
        return {
            'tool': tool_name,
            'signal': 'Insufficient Data',
            'justification': f'Requires at least {min_periods} data points, got {len(df)}',
            'details': {},
        }

    return None


_shared_finbert_model: Any = None
_model_lock = threading.Lock()


class SentimentAnalysisBase:
    """Base class for sentiment analysis with shared FinBERT functionality"""

    def __init__(self):
        self.finbert: Any = None
        self._model_initialized = False

    def _ensure_model_loaded(self):
        """Lazy load FinBERT model (shared singleton pattern)"""
        if self._model_initialized:
            return

        global _shared_finbert_model
        with _model_lock:
            if _shared_finbert_model is None:
                logger.info(
                    'Loading FinBERT model (first time only, may take 10-15s)...'
                )
                try:
                    from transformers import (
                        AutoModelForSequenceClassification,
                        AutoTokenizer,
                        pipeline,
                    )

                    tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert')
                    model = AutoModelForSequenceClassification.from_pretrained(
                        'ProsusAI/finbert', num_labels=3
                    )
                    _shared_finbert_model = pipeline(
                        'sentiment-analysis',  # type: ignore[arg-type]
                        model=model,
                        tokenizer=tokenizer,
                        device='cpu',  # pyright: ignore[reportArgumentType]
                    )  # type: ignore[call-overload]
                    logger.info('FinBERT model loaded successfully')
                except Exception as e:
                    logger.error(f'Failed to initialize sentiment model: {e}')
                    _shared_finbert_model = None

            self.finbert = _shared_finbert_model
            self._model_initialized = True

    def analyze_text_sentiment(self, text: str) -> Optional[dict[str, Any]]:
        """Analyze sentiment of a single text using FinBERT"""
        self._ensure_model_loaded()

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

    def categorize_sentiment_counts(
        self, items: List[dict[str, Any]], sentiment_key: str = 'sentiment'
    ) -> dict[str, int]:
        """Count sentiment categories from a list of analyzed items"""
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}

        for item in items:
            sentiment = item.get(sentiment_key, {})
            if isinstance(sentiment, dict):
                label = sentiment.get('label')
                if label in sentiments:
                    sentiments[label] += 1

        return sentiments

    def generate_trading_signal(
        self,
        ticker: str,
        tool_name: str,
        total_items: int,
        description: str,
        sentiments: dict[str, int],
        confidence_scores: List[float],
        item_data: dict[str, List],
        positive_threshold: float = 60.0,
        negative_threshold: float = 60.0,
        mixed_threshold: float = 15.0,
    ) -> dict[str, Any]:
        """Generate standardized trading signal based on sentiment analysis"""

        if total_items == 0:
            return {
                'tool': tool_name,
                'description': description,
                'signal': 'No Data',
                'justification': f'No analyzable data found for {ticker}',
                'details': {
                    'items_analyzed': 0,
                    'top_items': {'positive': [], 'negative': [], 'neutral': []},
                },
            }

        positive_pct = (sentiments['positive'] / total_items) * 100
        negative_pct = (sentiments['negative'] / total_items) * 100
        neutral_pct = (sentiments['neutral'] / total_items) * 100

        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        )

        if positive_pct > positive_threshold:
            signal = 'Bullish'
            confidence = 'High' if avg_confidence > 0.8 else 'Medium'
            justification = f'{positive_pct:.1f}% of analyzed content shows positive sentiment toward {ticker}'
        elif negative_pct > negative_threshold:
            signal = 'Bearish'
            confidence = 'High' if avg_confidence > 0.8 else 'Medium'
            justification = f'{negative_pct:.1f}% of analyzed content shows negative sentiment toward {ticker}'
        elif abs(positive_pct - negative_pct) < mixed_threshold:
            signal = 'Neutral'
            confidence = 'Medium'
            justification = f'Mixed sentiment: {positive_pct:.1f}% positive, {negative_pct:.1f}% negative'
        else:
            signal = 'Weak Bullish' if positive_pct > negative_pct else 'Weak Bearish'
            confidence = 'Low'
            justification = f'Slight sentiment bias: {positive_pct:.1f}% positive, {negative_pct:.1f}% negative'

        return {
            'tool': tool_name,
            'description': description,
            'signal': signal,
            'confidence': confidence,
            'justification': justification,
            'details': {
                'items_analyzed': total_items,
                'positive_percentage': round(positive_pct, 1),
                'negative_percentage': round(negative_pct, 1),
                'neutral_percentage': round(neutral_pct, 1),
                'average_confidence': round(avg_confidence, 3),
                'top_items': item_data,
            },
        }

    def create_error_response(self, tool_name: str, message: str) -> dict[str, Any]:
        """Create standardized error response"""
        return {
            'tool': tool_name,
            'description': 'An error occured by a tool. Please check.',
            'signal': 'error',
            'justification': message,
            'details': {},
        }
