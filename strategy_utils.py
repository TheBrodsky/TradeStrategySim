from sim_utils import Interval
from datetime import timedelta
import datetime
import pandas as pd


"""
Objects for simulating trading, specific to a strategy.
"""


class Signal():
    def __init__(self, interval: Interval, overnight_range: Interval):
        self.interval = interval
        self.high = interval.agg_high
        self.low = interval.agg_low
        self.range = interval.range
        self.high_in_range = overnight_range.is_price_inside(self.high)
        self.low_in_range = overnight_range.is_price_inside(self.low)


class Listener():
    timeout = 2
    
    def __init__(self, interval_start: datetime, high_threshold: float, low_threshold: float, df: pd.DataFrame):
        self.interval = Interval(interval_start, interval_start + timedelta(hours=Listener.timeout), df)
        self.high = high_threshold
        self.low = low_threshold
        
        # Find the first row in the interval where the price exceeds the signal high or low
        self.high_trigger = self.interval[self.interval['High'].ge(self.high)].ext.first_or_none()
        self.low_trigger = self.interval[self.interval['Low'].le(self.low)].ext.first_or_none()
        
        # Price and time where price in the interval first exceeds the signal high or low
        self.high_trigger_price = self.high_trigger['High'] if self.high_trigger is not None else None
        self.low_trigger_price = self.low_trigger['Low'] if self.low_trigger is not None else None
        self.high_trigger_time = self.high_trigger.name if self.high_trigger is not None else None
        self.low_trigger_time = self.low_trigger.name if self.low_trigger is not None else None


class Trade(Listener):
    def __init__(self, triggered_time: datetime, triggered_price: float, signal_range: float, df: pd.DataFrame):
        self.high = triggered_price + signal_range
        self.low = triggered_price - signal_range
        super().__init__(triggered_time, self.high, self.low, df)