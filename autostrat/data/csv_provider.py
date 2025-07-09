"""
autostrat.data.csv_provider

Utility class that loads daily OHLCV data for a single symbol from a
`{directory}/{symbol}.csv` file.

CSV format (header row **must** match):

    Date,Open,High,Low,Close,Volume

* Date must be ISO `YYYY-MM-DD`.
* Any extra columns are ignored.
"""

from pathlib import Path
from typing import Final

import pandas as pd
from .provider import DataProvider


class CSVDataProvider(DataProvider):
    """
    Loads historical data from plain CSV files on disk.

    Example
    >>> provider = CSVDataProvider("sample_data")
    >>> df = provider.get_history("UPTREND", "2025-01-01", "2025-03-01")
    >>> print(len(df))      # 60 rows in the demo file
    """

    _DATE_COL: Final[str] = "Date"

    def __init__(self, directory: str | Path):
        self.directory = Path(directory)

    #  PUBLIC API
    def get_history(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """
        Parameters
        symbol : str
            Ticker / file stem (file must be `{symbol}.csv`).
        start, end : str
            Inclusive date range (YYYY-MM-DD).

        Returns
        pd.DataFrame
            Indexed by `pd.DatetimeIndex`, chronologically sorted,
            containing at least a `"Close"` column.
        """
        csv_path = self.directory / f"{symbol}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(
                f"CSV file for symbol '{symbol}' not found: {csv_path}"
            )

        df = (
            pd.read_csv(
                csv_path,
                parse_dates=[self._DATE_COL],
                date_parser=lambda col: pd.to_datetime(
                    col, format="%Y-%m-%d", errors="coerce"
                ),
            )
            .set_index(self._DATE_COL)
            .sort_index()
        )

        # Filter by date range
        start_dt = pd.to_datetime(start)
        end_dt = pd.to_datetime(end)
        mask = (df.index >= start_dt) & (df.index <= end_dt)
        return df.loc[mask]
