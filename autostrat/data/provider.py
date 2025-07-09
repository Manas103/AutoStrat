from abc import ABC, abstractmethod
import pandas as pd


class DataProvider(ABC):
    """Return historical OHLCV data as a DataFrame."""

    @abstractmethod
    def get_history(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """DataFrame indexed by date with at least a 'Close' column."""
        raise NotImplementedError
