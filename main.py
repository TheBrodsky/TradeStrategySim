from candlestick_parser import parse_data_into_market_days
from sim_utils import Interval
from config_parser import Config
from strategy_utils import Signal, Listener, Trade
import datetime
import pandas as pd
import os


class SimulatedDay():
    """
    A simulated day of trading. Contains tools for outputting the simulation to a CSV.
    """
    def __init__(self, date: str, day_data: pd.DataFrame, config: Config):
        self.date = date
        self.data = day_data
        self.config = config
        
        self.overnight_range = Interval(config.or_start, config.or_end, self.data)
        self.records = [self._simulate_signal(i, signal_config) for i, signal_config in enumerate(config.signals)]

    def _simulate_signal(self, signal_index: int, signal_config) -> 'SimulatedDay.Record':
        """Determine trades for a given signal."""
        signal = Signal(Interval(signal_config['start'], signal_config['end'], self.data), self.overnight_range)
        listener = Listener(signal.interval.end, signal.high, signal.low, self.data)
        high_trade = Trade(listener.high_trigger_time, listener.high_trigger_price, signal.range, self.data) if listener.high_trigger_price is not None else None
        low_trade = Trade(listener.low_trigger_time, listener.low_trigger_price, signal.range, self.data) if listener.low_trigger_price is not None else None
        return SimulatedDay.Record(signal_index, signal, listener, high_trade, low_trade)
    
    def to_csv(self) -> str:
        """Convert the simulation results to CSV format."""
        csv_rows = []
        for record in self.records:
            csv_rows.append(f"{self.date}, {record.high_row_to_csv()}")
            csv_rows.append(f"{self.date}, {record.low_row_to_csv()}")
        
        return "\n".join(csv_rows)
    
    
    class Record:
        """
        Encapsulates the results of the simulation for a single signal, organizing into rows for high and low trades.
        """
        def __init__(self, signal_id: int, signal: Signal, listener: Listener, high_trade: Trade, low_trade: Trade):
            self.signal_id = signal_id
            self.high_row = SimulatedDay.Record.Row(signal.high, signal.high_in_range, listener.high_trigger_price, listener.high_trigger_time, high_trade)
            self.low_row = SimulatedDay.Record.Row(signal.low, signal.low_in_range, listener.low_trigger_price, listener.low_trigger_time, low_trade)
            
        def high_row_to_csv(self) -> dict:
            return ", ".join([str(self.signal_id), "High", self.high_row.to_csv_row()])
        
        def low_row_to_csv(self) -> dict:
            return ", ".join([str(self.signal_id), "Low", self.low_row.to_csv_row()])
        
        
        class Row:
            """
            A single row of data in a CSV, representing either a high or low trade from a single signal.
            """
            def __init__(self, signal_price: float, is_in_OR: bool, trade_enter_price: float, trade_enter_time: datetime, trade: Trade):
                self.signal_price = signal_price
                self.is_in_OR = is_in_OR
                self.trade_enter_price = trade_enter_price
                self.trade_enter_time = trade_enter_time
                self.trade = trade
            
            def to_csv_row(self) -> dict:
                return ", ".join([str(self.signal_price),
                                  str(self.is_in_OR),
                                  str(self.trade_enter_time.time()) if self.trade_enter_time else "",
                                  str(self.trade_enter_price) if self.trade_enter_price else "",
                                  self._trade_to_csv(),
                ])
            
            def _trade_to_csv(self) -> str:
                if not self.trade:
                    return ", , , , "  # No trade, return empty values
                else:
                    return ", ".join([
                        self._get_trade_outcome(),
                        str(self.trade.high_trigger_time.time()) if self.trade.high_trigger_time else "",
                        str(self.trade.high_trigger_price) if self.trade.high_trigger_price else "",
                        str(self.trade.low_trigger_time.time()) if self.trade.low_trigger_time else "",
                        str(self.trade.low_trigger_price) if self.trade.low_trigger_price else ""
                    ])

            def _get_trade_outcome(self) -> str:
                """Determine the trade outcome, showing whether the trade hit the high and/or low price and in what order."""
                if not self.trade:
                    return ""  # No trade, return an empty string

                outcomes = []
                if self.trade.high_trigger_price is not None:
                    outcomes.append(("High", self.trade.high_trigger_time))
                if self.trade.low_trigger_price is not None:
                    outcomes.append(("Low", self.trade.low_trigger_time))

                # Sort outcomes by the time they occurred
                outcomes.sort(key=lambda x: x[1])

                # Return the outcomes in the correct order
                return ";".join([outcome[0] for outcome in outcomes])


def process_file(file) -> dict:
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
            simulated_days[date] = SimulatedDay(date, one_day_data, config)
        except IndexError as e: # Happens when no data exists in a critical interval
            print(f"Skipping {date} due to missing critical data: {e}")
            skipped_days += 1
            continue
    
    print(f"Processing complete. Skipped {skipped_days} days.")

    return simulated_days



if __name__ == "__main__":
    config = Config('config.ini')
    Listener.timeout = config.listener_timeout
    
    # Initialize input and output directories, simulated day dictionary
    input_dir = os.path.abspath(config.input_directory)
    output_dir = os.path.abspath(config.output_directory)
    os.makedirs(output_dir, exist_ok=True)
    all_simulated_days = {}

    # Iterate through all files in the input directory
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        if os.path.isfile(file_path):
            print(f"Processing file: {file_name}")
            simulated_days = process_file(file_path)
            all_simulated_days.update(simulated_days)

    # Convert all SimulatedDays to CSV format
    csv_rows = []
    for date, simulated_day in all_simulated_days.items():
        csv_rows.append(simulated_day.to_csv())

    # Write the combined CSV to the output directory
    output_file = os.path.join(output_dir, "simulation_results.csv")
    with open(output_file, "w") as f:
        f.write("\n".join(csv_rows))

    print(f"Simulation results written to {output_file}")
    