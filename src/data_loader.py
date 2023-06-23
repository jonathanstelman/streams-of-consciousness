import logging
import pandas as pd


        
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
    

def load_earnings_report(filepath, distributor, service_map_file):
    """
    Reads earnings report and transforms data, formatting dates,
    and joining streaming company names to use
    """
    
    distributor_loaders = {
        'cd_baby': load_cd_baby
    }
    data = distributor_loaders.get(distributor)(filepath)
    
    service_map = pd.read_csv(service_map_file)
    data['Year'] = pd.DatetimeIndex(data['Sales Date']).year
    data['Month'] = pd.DatetimeIndex(data['Sales Date']).month
    data = data.merge(service_map, how='left')
    data['Company Name'] = data['Company Name'].fillna('Unknown')
    return data
