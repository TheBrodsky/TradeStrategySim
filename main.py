from candlestick_parser import parse_data_into_market_days
from sim_utils import Interval
from config_parser import Config
from strategy_utils import Signal, Listener, Trade
import pandas as pd


DATA_PATH = r"input\MNQ 03-25.Last.txt"


class SimulatedDay():
    def __init__(self, date: str, day_data: pd.DataFrame, config: Config):
        self.date = date
        self.data = day_data
        self.config = config
        
        self.overnight_range = Interval(config.or_start, config.or_end, self.data)
        self.records = []
        for i, signal_config in enumerate(config.signals):
            self.records.append(self._simulate_signal(i, signal_config))

    def _simulate_signal(self, signal_index: int, signal_config) -> 'SimulatedDay.Record':
        signal = Signal(Interval(signal_config['start'], signal_config['end'], self.data), self.overnight_range)
        listener = signal.create_listener(config.listener_timeout, self.data)
        high_trade = listener.create_high_trade(signal.range)
        low_trade = listener.create_low_trade(signal.range)
        return SimulatedDay.Record(signal, listener, high_trade, low_trade)
    
    class Record:
        def __init__(self, signal: Signal, listener: Listener, high_trade: Trade, low_trade: Trade):
            self.signal_high = listener.signal_high
            self.signal_low = listener.signal_low


def process_file(file):
    data_by_day = parse_data_into_market_days(file, config.input_timezone, config.master_timezone, config.market_close_hour)
    skipped_days = 0
    simulated_days = dict()
    
    # Process file day by day
    print(f"Data loaded for {len(data_by_day)} days.")
    for date, one_day_data in data_by_day.items():
        # Cull overly incomplete days
        if len(one_day_data) < config.num_entry_cull_cutoff:
            print(f"Skipping {date} due to insufficient data.")
            skipped_days += 1
            continue
        
        try:
            print(f"Processing data for {date}...")
            simulated_days[date] = SimulatedDay(one_day_data, config)
        except IndexError as e: # Happens when no data exists in a critical interval
            print(f"Skipping {date} due to missing critical data: {e}")
            skipped_days += 1
            continue
    
    print("Processing complete.")
    print(f"Skipped {skipped_days} days.")


if __name__ == "__main__":
    config = Config('config.ini')
    process_file(DATA_PATH)
    