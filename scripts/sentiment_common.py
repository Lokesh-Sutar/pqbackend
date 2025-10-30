import logging
import sys
from pathlib import Path

from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

logger = logging.getLogger(__name__)

DEFAULT_TICKERS = [
    'AAPL',
    'AMD',
    'AMZN',
    'GOOGL',
    'GOOG',
    'IBM',
    'META',
    'MSFT',
    'NFLX',
    'NVDA',
    'ORCL',
    'PYPL',
    'QCOM',
    'TSLA',
    'UBER',
    'LMT',
    'NOC',
    'BA',
    'RTX',
    'DE',
    'AGCO',
    'CTVA',
    'JNJ',
    'PFE',
    'MRK',
]

INDIAN_TICKERS = [
    'RELIANCE.NS',
    'ADANIENT.NS',
    'TATAMOTORS.NS',
    'TATASTEEL.NS',
    'TCS.NS',
    'INFY.NS',
    'WIPRO.NS',
    'HCLTECH.NS',
    'TECHM.NS',
    'HDFCBANK.NS',
    'ICICIBANK.NS',
    'SBIN.NS',
    'KOTAKBANK.NS',
    'BAJFINANCE.NS',
    'HINDUNILVR.NS',
    'ITC.NS',
    'ASIANPAINT.NS',
    'DABUR.NS',
    'NESTLEIND.NS',
    'SUNPHARMA.NS',
    'DRREDDY.NS',
    'CIPLA.NS',
    'DIVISLAB.NS',
    'LUPIN.NS',
    'BEL.NS',
    'HAL.NS',
    'LT.NS',
    'BEML.NS',
    'MAZDOCK.NS',
    'ONGC.NS',
    'NTPC.NS',
    'POWERGRID.NS',
    'IOC.NS',
]

TICKER_TO_COMPANY = {
    'AAPL': 'Apple',
    'AMD': 'Advanced Micro Devices',
    'AMZN': 'Amazon',
    'GOOGL': 'Google',
    'GOOG': 'Google',
    'IBM': 'IBM',
    'META': 'Meta',
    'MSFT': 'Microsoft',
    'NFLX': 'Netflix',
    'NVDA': 'Nvidia',
    'ORCL': 'Oracle',
    'PYPL': 'PayPal',
    'QCOM': 'Qualcomm',
    'TSLA': 'Tesla',
    'UBER': 'Uber',
    'LMT': 'Lockheed Martin',
    'NOC': 'Northrop Grumman',
    'BA': 'Boeing',
    'RTX': 'Raytheon Technologies',
    'DE': 'Deere & Company',
    'AGCO': 'AGCO Corporation',
    'CTVA': 'Corteva',
    'JNJ': 'Johnson & Johnson',
    'PFE': 'Pfizer',
    'MRK': 'Merck & Co.',
    'RELIANCE.NS': 'Reliance Industries',
    'ADANIENT.NS': 'Adani Enterprises',
    'TATAMOTORS.NS': 'Tata Motors',
    'TATASTEEL.NS': 'Tata Steel',
    'TCS.NS': 'Tata Consultancy Services',
    'INFY.NS': 'Infosys',
    'WIPRO.NS': 'Wipro',
    'HCLTECH.NS': 'HCL Technologies',
    'TECHM.NS': 'Tech Mahindra',
    'HDFCBANK.NS': 'HDFC Bank',
    'ICICIBANK.NS': 'ICICI Bank',
    'SBIN.NS': 'State Bank of India',
    'KOTAKBANK.NS': 'Kotak Mahindra Bank',
    'BAJFINANCE.NS': 'Bajaj Finance',
    'HINDUNILVR.NS': 'Hindustan Unilever',
    'ITC.NS': 'ITC Limited',
    'ASIANPAINT.NS': 'Asian Paints',
    'DABUR.NS': 'Dabur',
    'NESTLEIND.NS': 'Nestlé India',
    'SUNPHARMA.NS': 'Sun Pharmaceutical',
    'DRREDDY.NS': "Dr. Reddy's Laboratories",
    'CIPLA.NS': 'Cipla',
    'DIVISLAB.NS': "Divi's Laboratories",
    'LUPIN.NS': 'Lupin',
    'BEL.NS': 'Bharat Electronics',
    'HAL.NS': 'Hindustan Aeronautics',
    'LT.NS': 'Larsen & Toubro',
    'BEML.NS': 'BEML',
    'MAZDOCK.NS': 'Mazagon Dock Shipbuilders',
    'ONGC.NS': 'Oil & Natural Gas Corporation',
    'NTPC.NS': 'NTPC Limited',
    'POWERGRID.NS': 'Power Grid Corporation',
    'IOC.NS': 'Indian Oil Corporation',
}


def setup_logging(log_file='./logs/sentiment_fetch.log'):
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)],
    )


def initialize_finbert():
    """Initialize FinBERT model for sentiment analysis"""
    logger.info('Loading FinBERT model...')
    import torch

    try:
        tokenizer = AutoTokenizer.from_pretrained('ProsusAI/finbert')
        model = AutoModelForSequenceClassification.from_pretrained(
            'ProsusAI/finbert', num_labels=3
        )
        finbert = pipeline(
            'sentiment-analysis',  # type: ignore
            model=model,
            tokenizer=tokenizer,
            device='cuda' if torch.cuda.is_available() else 'cpu',
        )  # type: ignore
        logger.info('FinBERT model loaded successfully')
        return finbert
    except Exception as e:
        logger.error(f'Failed to initialize FinBERT: {e}')
        return None


def analyze_sentiment(finbert, text: str) -> dict | None:
    """Analyze sentiment of text using FinBERT"""
    if not finbert or not text or len(text.strip()) < 10:
        return None

    try:
        result = finbert(text[:512])[0]
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
