from datetime import datetime, timedelta
import pandas as pd
from enum import Enum
from candlestick_parser import aggregate_data
from pandas.api.extensions import register_dataframe_accessor

"""
Objects for simulating trading, agnostic of strategy.
Assumes the data is in a pandas DataFrame with a datetime index and columns: Open, High, Low, Close, Volume.
"""

@register_dataframe_accessor("ext")
class DFAccessor:
    """
    A DataFrame accessor for additional functionality.
    """
    def __init__(self, pandas_obj: pd.DataFrame):
        self._obj = pandas_obj
    
    def first_or_none(self):
        return self._obj.iloc[0] if not self._obj.empty else None


class Interval:
    """
    A market interval defined by a start and end time. Contains aggregated data for the interval.
    """
    def __init__(self, start: datetime, end: datetime, df: pd.DataFrame):
        self.start = start
        self.end = end
        self.interval = df.between_time(self.start.time(), self.end.time())
        
        agg = aggregate_data(self.interval)
        self.agg_high = agg['High']
        self.agg_low = agg['Low']
        self.agg_open = agg['Open']
        self.agg_close = agg['Close']
        self.agg_volume = agg['Volume']
        self.range = self.agg_high - self.agg_low
    
    def is_price_inside(self, price: float) -> bool:
        return self.agg_low <= price <= self.agg_high

    def __getitem__(self, item):
        return self.interval[item]