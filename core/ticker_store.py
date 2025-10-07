import json
import logging
import os
from threading import Lock
from typing import List, Set

logger = logging.getLogger(__name__)


class TickerStore:
    def __init__(self, file_path: str = 'data/tickers.json'):
        self.file_path = file_path
        self._lock = Lock()
        self._tickers: Set[str] = set()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create the data directory and file if they don't exist."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            self._write_to_file(set())

    def _write_to_file(self, tickers: Set[str]):
        """Write tickers to JSON file (backup only)."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(
                    {'tickers': sorted(list(tickers)), 'count': len(tickers)}, f, indent=2
                )
                f.flush()
                os.fsync(f.fileno())
        except Exception as e:
            logger.error(f'Failed to write tickers to file: {e}', exc_info=True)

    def add_ticker(self, ticker: str) -> None:
        """Add a ticker to the store."""
        with self._lock:
            normalized_ticker = ticker.upper().strip()
            self._tickers.add(normalized_ticker)
            self._write_to_file(self._tickers)
            logger.info(
                f'Stored ticker: {normalized_ticker} (Total: {len(self._tickers)})'
            )

    def get_tickers(self) -> List[str]:
        """Get all tickers from in-memory store."""
        with self._lock:
            result = sorted(list(self._tickers))
            return result

    def clear(self) -> None:
        """Clear all tickers."""
        with self._lock:
            self._tickers.clear()
            self._write_to_file(set())
            logger.info('Cleared all tickers')

    def get_count(self) -> int:
        """Get the count of tickers."""
        with self._lock:
            return len(self._tickers)


ticker_store = TickerStore()
