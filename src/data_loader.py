import pandas as pd
from logger import logger


def load_cd_baby(filepath):
    """Loader for a data file exported from CD Baby
    """
    df = pd.read_csv(
        filepath, 
        delimiter='\t', 
        parse_dates=True, 
        usecols=[1, 2, 4, 11, 12]
    )
    df.columns = [
        'Sales Date',
        'Quantity',
        'Subtotal',
        'Company Name Source',
        'Transaction Type'
    ]
    df['Transaction Type'] = df['Transaction Type'].apply(lambda s: s.replace(' ', '_').lower())
    return df


def load_distrokid(filepath) -> pd.DataFrame:
    """Loader for a data file exported from DistroKid
    """
    df = pd.read_csv(
        filepath,
        delimiter='\t',
        parse_dates=[0],
        usecols=[1, 2, 7, 12]
    )
    df.columns = ['Sales Date', 'Company Name Source', 'Quantity', 'Subtotal']

    # TODO: this is a kludgy attempt to guess transaction type since DistroKid 
    # doesn't provide this level of detail
    df['Transaction Type'] = df['Subtotal'].apply(
        lambda v: 'download' if v > 0.2 else 'stream')

    return df



def load_earnings_report(filepath, distributor, service_map_file) -> pd.DataFrame:
    """Reads earnings report and transforms data, formatting dates,
    and joining streaming company names to use
    """

    distributor_loaders = {
        'cd_baby': load_cd_baby,
        'distrokid': load_distrokid
    }

    logger.info('Loading data using distibutor "%s"', distributor)
    data = distributor_loaders.get(distributor)(filepath)

    logger.info('Using service map file: "%s"', service_map_file)
    service_map = pd.read_csv(service_map_file)
    data['Year'] = pd.DatetimeIndex(data['Sales Date']).year
    data['Month'] = pd.DatetimeIndex(data['Sales Date']).month
    data = data.merge(service_map, how='left')
    data['Company Name'] = data['Company Name'].fillna('Unknown')
    return data
