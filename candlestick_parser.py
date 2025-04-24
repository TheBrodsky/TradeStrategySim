import pandas as pd
import datetime as dt


"""
Utility functions for parsing and processing market data.
Assumes the data is in a pandas DataFrame with a datetime index and columns: Open, High, Low, Close, Volume.
"""


def parse_data_into_market_days(file_path: str, from_zone: str, to_zone: str, cutoff_hour: int) -> dict:
    """Parses a data file into a dictionary of dataframes, each representing a trading day."""
    df = parse_data(file_path)
    df = convert_timezone(df, from_zone, to_zone)
    return groupby_trading_day(df, cutoff_hour)
    

def parse_data(file_path: str) -> pd.DataFrame:
    """Parse the data file into a DataFrame."""
    # Parse the semicolon-separated data
    df = pd.read_csv(file_path, sep=';', names=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    
    # Convert timestamp to datetime and index it
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d %H%M%S') # format YYYYMMDD HHMMSS
    df.set_index('timestamp', inplace=True)
    
    # Convert UTC to PST
    #pst = pytz.timezone('US/Pacific')
    #df.index = df.index.tz_localize('UTC').tz_convert(pst)
    
    return df


def convert_timezone(df: pd.DataFrame, from_zone: str, to_zone: str) -> pd.DataFrame:
    """Converts the timezone of the DataFrame index."""
    # Ensure timestamp is in datetime format
    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    
    df.index = df.index.tz_localize(from_zone)
    df.index = df.index.tz_convert(to_zone)
    
    return df


def groupby_trading_day(df: pd.DataFrame, cutoff_hour: int) -> dict:
    """Breaks the data into multiple DataFrames by trading day based on the cutoff hour."""
    # Extract date and hour
    df['date'] = df.index.date
    df['hour'] = df.index.hour
    
    # If hour is >= cutoff_hour, use current date, else use previous date
    df['trading_day'] = df.apply(
        lambda row: row['date'] if row['hour'] > cutoff_hour 
                    else row['date'] - dt.timedelta(days=1), 
        axis=1
    )
    
    # Group by trading day
    grouped = {}
    for day, group in df.groupby('trading_day'):
        grouped[day] = group.drop(['date', 'hour', 'trading_day'], axis=1)
    
    return grouped


def aggregate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate data to OHLCV format."""
    aggregated = pd.Series({
        'Open': df['Open'].iloc[0],
        'High': df['High'].max(),
        'Low': df['Low'].min(),
        'Close': df['Close'].iloc[-1],
        'Volume': df['Volume'].sum()
    })
    return aggregated


def resample_data(df: pd.DataFrame, interval: str) -> pd.DataFrame:
    """Resample data to a specified interval (e.g., '5T' for 5 minutes, '15T' for 15 minutes)"""
    resampled = df.resample(interval).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    })
    return resampled