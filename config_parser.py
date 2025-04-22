import configparser
from datetime import datetime

MARKET_DAY_MINUTES = 23 * 60 # Assuming market is open for 23 hours

class Config:
    def __init__(self, config_file: str):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # Parse general configs
        self.input_timezone = self.config['General']['input_timezone']
        self.master_timezone = self.config['General']['master_timezone']
        self.market_close_hour = int(self.config['General']['market_close_hour'])
        self.partial_day_cutoff = float(self.config['General']['partial_day_cutoff'])
        self.num_entry_cull_cutoff = int(MARKET_DAY_MINUTES * self.partial_day_cutoff)
        
        # Parse overnight range times
        or_section = self.config['OvernightRange']
        self.or_start = self._parse_time(or_section['start_time'])
        self.or_end = self._parse_time(or_section['end_time'])
        
        # Parse listener and trade timeouts
        listener_section = self.config['Listener']
        trade_section = self.config['Trade']
        self.listener_timeout = int(listener_section['timeout_hours'])
        self.trade_timeout = int(trade_section['timeout_hours'])
        
        # Parse signals
        self.signals = []
        signals_section = self.config['Signals']
        signal_count = int(signals_section['count'])
        
        for i in range(1, signal_count + 1):
            start = self._parse_time(signals_section[f'signal{i}_start'])
            end = self._parse_time(signals_section[f'signal{i}_end'])
            
            self.signals.append({
                "start": start,
                "end": end
            })

    def _parse_time(self, time_str: str) -> datetime:
        """
        Parse a time string in HH:MM format into a datetime.time object.
        """
        return datetime.strptime(time_str, "%H:%M")