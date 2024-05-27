from datetime import datetime

def to_date(date_string: str, date_format="%Y-%m-%d") -> datetime:
    """
    Converts a date formatted as YYYY-MM-DDD
    """
    return datetime.strptime(date_string, date_format).date()
