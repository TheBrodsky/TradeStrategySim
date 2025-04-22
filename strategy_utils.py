from sim_utils import Interval
from datetime import timedelta
import pandas as pd

class Signal():
    def __init__(self, interval: Interval, overnight_range: Interval):
        self.interval = interval
        self.high = interval.agg_high
        self.low = interval.agg_low
        self.range = interval.range
        self.high_in_range = overnight_range.is_price_inside(self.high)
        self.low_in_range = overnight_range.is_price_inside(self.low)
    
    def create_listener(self, duration: float, df: pd.DataFrame) -> 'Listener':
        listener_interval = Interval(self.interval.end, self.interval.end + timedelta(hours=duration), df)
        return Listener(listener_interval, self.high, self.low)


class Listener():
    def __init__(self, interval: Interval, signal_high: float, signal_low: float):
        # Find the first row in the interval where the price exceeds the signal high or low
        self.high_trigger = interval[interval.high().ge(signal_high)].ext.first_or_none()
        self.low_trigger = interval[interval.low().le(signal_low)].ext.first_or_none()
        
        # Price and time where price in the interval first exceeds the signal high or low
        self.high_trigger_price = self.high_trigger['High'] if self.high_trigger is not None else None
        self.low_trigger_price = self.low_trigger['Low'] if self.low_trigger is not None else None
        self.high_trigger_time = self.high_trigger.name if self.high_trigger is not None else None
        self.low_trigger_time = self.low_trigger.name if self.low_trigger is not None else None
    
    def create_high_trade(self, signal_range: float) -> 'Trade':
        return Trade(self.high_trigger_price, signal_range) if self.high_trigger_price is not None else None
    
    def create_low_trade(self, signal_range: float) -> 'Trade':
        return Trade(self.low_trigger_price, signal_range) if self.low_trigger_price is not None else None


class Trade():
    def __init__(self, triggered_price: float, signal_range: float):
        self.high = triggered_price + signal_range
        self.low = triggered_price - signal_range