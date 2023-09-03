from datetime import date, timedelta
import logging
from pathlib import Path
from random import choice, randrange

from numpy import random as npr
import pandas as pd

logging.basicConfig(level=logging.INFO)

streaming_services = [
    'Spotify',
    'Amazon US Premium Service',
    'iTunes - Apple Music – US',
    'YouTube Music',
    'Tidal'
]

transaction_types = [
    'Download',
    'Royalty',
    'Stream',
    'YouTube Audio Tier'
]

countries = [
    # some country codes used by CD Baby
    'AE', 'AU', 'BE', 'BG', 'CA', 'CH',
    'CO', 'CR', 'CY', 'CZ', 'DE', 'EG',
    'FR', 'GB', 'GE', 'HK', 'HR', 'IL',
    'JP', 'KG', 'KR', 'LT', 'LU', 'LV',
    'MX', 'MY', 'NL', 'RO', 'RU', 'SA',
    'SE', 'SG', 'UA', 'UK', 'US', 'ZA'
]


def get_spotify_rate(year):
    return -0.12 * (year-2000) + 3

def get_amazon_rate(year):
    return 0.013 * (year-2000) - 2

def get_apple_rate(year):
    return 0.03 * (year-2000) + 3

def get_youtube_rate(year):
    return -0.4 * (year-2000) + 2

def get_tidal_rate(year):
    return 0.01 * (year-2000) - 1


rate_function_lookup = {
    'Spotify': get_spotify_rate,
    'Amazon US Premium Service': get_amazon_rate,
    'iTunes - Apple Music – US': get_apple_rate,
    'YouTube Music': get_youtube_rate,
    'Tidal': get_tidal_rate
}

transaction_types_available = {
    'Spotify': ['Stream'],
    'Amazon US Premium Service': ['Stream', 'Download'],
    'iTunes - Apple Music – US': ['Stream'],
    'YouTube Music': ['Stream'],
    'Tidal': ['Stream']
}

artist_name = 'Radioactive Cheese'
albums = {
    'Cheesy Pee (a.k.a. Cheese EP)': {
        'Release Year': 2016,
        'Tracklist': ['Cheddar', 'Swiss Miss', 'G.O.A.T.', 'Cheesy Mac Daddy']
    },
    'Meltdown': {
        'Release Year': 2019,
        'Tracklist': [
            'Fun Do', 'Nuclear Brie-action', 'American Cheese',
            'Cheesy Poofs', 'Mushroom Cloud Burger',
            'Cheddar Shredder', "Rock 'n' Roll Roquefort",
            'Muenster Truck Madness'
        ]
    }
}

def get_available_album(year):
    released = [album for album, metadata in albums.items() if metadata['Release Year'] <= year]
    if not released:
        return None
    return choice(released)


def generate_stream(date):
    streaming_service = choice(streaming_services)
    noise = npr.normal(0, 0.03)
    amt = abs(rate_function_lookup.get(streaming_service)(date.year) + noise)
    qty = randrange(2) + 1
    album = get_available_album(date.year)
    track = choice(albums[album]['Tracklist'])
    transaction_type = choice(transaction_types_available[streaming_service])
    country = choice(countries)
    return {
        'Report Date': date + timedelta(days=24),
        'Sales Date': date,
        'Quantity': qty,
        'Price': round(amt, 3),
        'Subtotal': round(amt * qty, 3),
        'Isrc': '-----',
        'Barcode': '-----',
        'CDBabySku': '-----',
        'Album Name': album,
        'Artist Name': artist_name,
        'Track Name': track,
        'Partner Name': streaming_service,
        'Transaction Type': transaction_type,
        'Delivery Country': country
    }

years = list(range(2017,2024))
months = list(range(1,13))
days = list(range(1,32))

def main():
    logging.info('Generating sample data...')

    all_streams = []
    for year in years:
        logging.debug(f'generating streams for year {year}')
        for month in months:
            logging.debug(f'generating streams for month {month}')
            for day in days:
                logging.debug(f'generating streams for day {day}')
                try:
                    sale_date = date(year=year, month=month, day=day)
                except ValueError: # invalid date
                    pass
                logging.debug(f'stream sale date: {sale_date}')
                all_streams += [generate_stream(sale_date) for _i in range(randrange(20))]

    data = pd.DataFrame(all_streams)
    logging.info('Finished generating sample data.')
    #print(data.head())

    # save data
    outfile_dir = Path('data/sample_data')
    outfile_base = Path('sample_data_cd_baby.txt')
    
    logging.info(f'Saving data to file: {outfile_base}')
    data.to_csv(outfile_dir / outfile_base, sep='\t', index=False)

    logging.info('Sample data saved successfully.')

if __name__ == '__main__':
    main()