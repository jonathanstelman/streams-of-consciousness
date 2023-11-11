from dataclasses import dataclass, field
import logging

import numpy as np
import pandas as pd
from pathlib import Path

from data_loader import load_earnings_report
import enums


@dataclass
class DistributorReport():
    
    filepath: Path
    distributor: enums.Distributor = enums.Distributor.CD_BABY
    filters: list[enums.Transaction] = field(default_factory=[enums.Transaction.STREAM])
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



def adjust_report_for_inflation(report: pd.DataFrame, target_year: int):
    df = report.copy()
    for year in report.columns:
        df[year] = df[year].apply(lambda amt: convert_rate(amt, year, target_year))
    return df


def generate_reports(data, transactions=['stream'], adjust_for_inflation=True):
    """Aggregate all-time data by counts, earnings, and rates

    TODO: separate reports into different functions
    """
    if transactions:
        # filter transactions
        tr = [t.lower() for t in transactions]
        data = data[data['Transaction Type'].str.lower().isin(tr)]
    

    # create dataframes
    earnings_df = data.pivot_table(values='Subtotal', index='Company Name', columns='Year', aggfunc='sum')
    for c in earnings_df.columns:
        earnings_df[c] = earnings_df[c].astype(float)
    
    counts_df = data.pivot_table(values='Quantity', index='Company Name', columns='Year', aggfunc='sum')
    for c in counts_df.columns:
        counts_df[c] = counts_df[c].astype(float)

    rates_df = earnings_df / counts_df

    # structure reports in a dictionary
    reports = dict()
    reports['counts'] = counts_df
    reports['earnings'] = earnings_df
    reports['rates'] = rates_df

    # append inflation-adjusted reports
    if adjust_for_inflation:
        # hardcode inflation year to 2022 because cpi library doesn't have more recent data
        reports['cpi_adjusted_rates'] = adjust_report_for_inflation(reports['rates'], 2022)
        reports['cpi_adjusted_earnings'] = adjust_report_for_inflation(reports['earnings'], 2022)

    return reports


def convert_rate(raw_currency_amt: float, raw_currency_year: int, convert_year: int):
    from cpi import inflate
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