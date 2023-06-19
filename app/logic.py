from dataclasses import dataclass, field
from enum import Enum
import logging

from cpi import inflate
import numpy as np
import pandas as pd
from pathlib import Path


class Distributor(Enum):
    CD_BABY = 'cd_baby'
    DISTRO_KID = 'distro_kid'

class Transaction(Enum):
    STREAM = 'stream'
    DOWNLOAD = 'download'
    ROYALTY = 'royalty'
    YOUTUBE_AUDIO = 'youtube_audio_tier'


@dataclass
class DistributorReport():
    
    filepath: Path
    distributor: Distributor = Distributor.CD_BABY
    filters: list[Transaction] = field(default_factory=[Transaction.STREAM])
    source_data: pd.DataFrame = field(init=False)

    # Derived reports
    count_report: pd.DataFrame = field(init=False)
    rate_report: pd.DataFrame = field(init=False)
    earnings_report: pd.DataFrame = field(init=False)
    rate_report_cpi_adj: pd.DataFrame = field(init=False)
    earnings_report_cpi_adj: pd.DataFrame = field(init=False)
        
    def __post_init__(self):
        self.source_data = load_earnings_report(self.filepath, self.distributor)
        reports = generate_reports(self.source_data, transactions=self.filters, adjust_for_inflation=True)
        self.count_report = reports['counts']
        self.rate_report = reports['rates']
        self.earnings_report = reports['earnings']
        self.rate_report_cpi_adj = reports['cpi_adjusted_rates']
        self.earnings_report_cpi_adj = reports['cpi_adjusted_earnings']
        
        
def load_cd_baby(filepath):
    """Loader for a data file exported from CD Baby
    """
    try:
        df = pd.read_csv(
            filepath, 
            delimiter='\t', 
            parse_dates=True, 
            usecols=[1, 2, 3, 4, 11, 12]
        )
        df['Transaction Type'] = df['Transaction Type'].apply(lambda s: s.replace(' ', '_').lower())
        return df
    
    except Exception as e:
        logging.error('could not read file!')
        raise Exception('Unexpected file format!')
    

def load_earnings_report(filepath, distributor, partner_map_file):
    """Reads earnings report and formats data
    """
    
    distributor_loaders = {
        'cd_baby': load_cd_baby
    }
    data = distributor_loaders.get(distributor)(filepath)
    
    partner_map = pd.read_csv(partner_map_file)
    data['Year'] = pd.DatetimeIndex(data['Sales Date']).year
    data['Month'] = pd.DatetimeIndex(data['Sales Date']).month
    data = data.merge(partner_map, how='left')
    data['Company Name'] = data['Company Name'].fillna('Unknown')
    return data


def adjust_report_for_inflation(report: pd.DataFrame, target_year: int):
    df = report.copy()
    for year in report.columns:
        df[year] = df[year].apply(lambda amt: convert_rate(amt, year, target_year))
    return df


def generate_reports(data, transactions=['stream'], adjust_for_inflation=True):
    """Aggregate all-time data by counts, earnings, and rates
    """
    if transactions:
        tr = [t.lower() for t in transactions]
        data = data[data['Transaction Type'].str.lower().isin(tr)]
    
    reports = dict()
    reports['counts'] = data.pivot_table(values='Quantity', index='Company Name', columns='Year', aggfunc='sum')
    reports['earnings'] = data.pivot_table(values='Subtotal', index='Company Name', columns='Year', aggfunc='sum')
    reports['rates'] = pd.DataFrame(reports['earnings'] / reports['counts'])

    if adjust_for_inflation:
        reports['cpi_adjusted_rates'] = adjust_report_for_inflation(reports['rates'], 2022)
        reports['cpi_adjusted_earnings'] = adjust_report_for_inflation(reports['earnings'], 2022)

    return reports



def convert_rate(raw_currency_amt: float, raw_currency_year: int, convert_year: int):

    if not raw_currency_amt:
        return np.nan
    conv_currency_amt = None
    while not conv_currency_amt and convert_year > 1970:
        logging.debug(f'Converting currency to rate for year {convert_year}...')
        try: 
            conv_currency_amt = inflate(raw_currency_amt, raw_currency_year, to=convert_year)
        except Exception as e: # KeyError or CPIObjectDoesNotExist?
            print(f'Could not convert. Failed with {e}')
            print('  ERROR - Rate conversion not available. Trying previous year.')
            convert_year -= 1

    return conv_currency_amt