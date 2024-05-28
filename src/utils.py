from datetime import datetime

import pandas as pd

def to_date(date_string: str, date_format="%Y-%m-%d") -> datetime:
    """
    Converts a date formatted as YYYY-MM-DDD
    """
    return datetime.strptime(date_string, date_format).date()


def convert_df_to_csv(df: pd.DataFrame):
    """
    Convert a pandas DataFrame to a csv file
    """
    return df.to_csv(index=False).encode('utf-8')
