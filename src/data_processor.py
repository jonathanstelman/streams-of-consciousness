from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd

from data_loader import load_earnings_report
import enums
from inflation import adjust_amount, get_cpi_data
from logger import logger
from utils import to_date


@dataclass
class DistributorReport():
    """Container for all distributor reports
    """
    filepath: Path
    distributor: enums.Distributor = enums.Distributor.CD_BABY
    filters: tuple[enums.Transaction] = field(default_factory=[enums.Transaction.STREAM])
    source_data: pd.DataFrame = field(init=False)

    # Derived reports
    count_report: pd.DataFrame = field(init=False)
    rate_report: pd.DataFrame = field(init=False)
    earnings_report: pd.DataFrame = field(init=False)
    rate_report_cpi_adj: pd.DataFrame = field(init=False)
    earnings_report_cpi_adj: pd.DataFrame = field(init=False)

    def __post_init__(self):
        self.source_data = load_earnings_report(self.filepath, self.distributor)
        reports = generate_reports(
            self.source_data,
            transactions=self.filters,
            adjust_for_inflation=True
        )
        self.count_report = reports['counts']
        self.rate_report = reports['rates']
        self.earnings_report = reports['earnings']
        self.rate_report_cpi_adj = reports['cpi_adjusted_rates']
        self.earnings_report_cpi_adj = reports['cpi_adjusted_earnings']


def adjust_report_for_inflation(report: pd.DataFrame, target_date: date):
    """
    Iterate over all columns (years) and adjusts the amount to the target year value
    """
    df = report.copy()
    years = report.columns
    cpi_data = get_cpi_data(years.min(), date.today().year)
    for year in years:
        from_date = to_date(f'{year}-06-30')
        df[year] = df[year].apply(
            lambda amt:
                amt if pd.isnull(amt)
                else adjust_amount(cpi_data, amt, from_date, target_date)
        )
    return df


def generate_reports(data, transactions=('stream'), adjust_for_inflation=True):
    """Aggregate all-time data by counts, earnings, and rates

    TODO: separate reports into different functions
    """
    if transactions:
        # filter transactions
        tr = [t.lower() for t in transactions]
        data = data[data['Transaction Type'].str.lower().isin(tr)]

    # create dataframes
    earnings_df = data.pivot_table(
        values='Subtotal',
        index='Company Name',
        columns='Year',
        aggfunc='sum'
    )
    for c in earnings_df.columns:
        earnings_df[c] = earnings_df[c].astype(float)

    counts_df = data.pivot_table(
        values='Quantity',
        index='Company Name',
        columns='Year',
        aggfunc='sum'
    )
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
        logger.debug('Adding CPI adjusted reports')
        reports['cpi_adjusted_rates'] = adjust_report_for_inflation(reports['rates'], date.today())
        reports['cpi_adjusted_earnings'] = adjust_report_for_inflation(reports['earnings'], date.today())

    return reports
