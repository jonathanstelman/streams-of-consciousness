from datetime import date, timedelta
from random import choice, randrange
from time import mktime

from numpy import random as npr
import pandas as pd

streaming_services = [
    'Spotify Stream',
    'Amazon US Premium Service',
    'iTunes - Apple Music – US',
    'YouTube Music',
    'Tidal'
]

countries = [
    'AE', 'AU', 'BE', 'BG', 'CA', 'CH',
    'CO', 'CR', 'CY', 'CZ', 'DE', 'EG',
    'FR', 'GB', 'GE', 'HK', 'HR', 'IL',
    'JP', 'KG', 'KR', 'LT', 'LU', 'LV',
    'MX', 'MY', 'NL', 'RO', 'RU', 'SA',
    'SE', 'SG', 'UA', 'UK', 'US', 'ZA'
]


def get_spotify_rate(year):
    return -0.12 * year + 3

def get_amazon_rate(year):
    return 0.013 * year - 2

def get_apple_rate(year):
    return 0.05 * year + 3

def get_youtube_rate(year):
    return -0.4 * year + 2

def get_tidal_rate(year):
    return 0.01 * year - 1


rate_function_lookup = {
    'Spotify Stream': get_spotify_rate,
    'Amazon US Premium Service': get_amazon_rate,
    'iTunes - Apple Music – US': get_apple_rate,
    'YouTube Music': get_youtube_rate,
    'Tidal': get_tidal_rate
}

artist_name = 'Radioactive Cheese'
albums = {
    'Cheesy Pee': {
        'Release Year': 2016,
        'Tracklist': ['Cheddar', 'Swiss', 'G.O.A.T.', 'Cheesy Mac']
    },
    'Meltdown': {
        'Release Year': 2019,
        'Tracklist': ['Fun Do', 'Nuclear Brie-action', 'American Cheese',
                      'Cheesy Poofs', 'Mushroom Cloud Burger',
                      'Cheddar Shredder', "Rock 'n' Roll Roquefort",
                      'Muenster Truck Madness']
        }
}

def get_album(year):
    released = [album for album, metadata in albums.items() if metadata['Release Year'] <= year]
    if not released:
        return None
    return choice(released)


def generate_stream(date):
    streaming_service = choice(streaming_services)
    noise = npr.normal(0, 0.03)
    amt = rate_function_lookup.get(streaming_service)(date.year) + noise
    qty = randrange(2) + 1
    album = get_album(date.year)
    track = choice(albums[album]['Tracklist'])
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
        'Partner Name': '-----',
        'Transaction Type': '-----',
        'Delivery Country': '-----'
    }

years = list(range(2017,2024))
months = list(range(1,13))
days = list(range(1,31))

def main():

    all_streams = []
    for year in years[2:5]:
        print(f'generating streams for year {year}')
        for month in months[:3]:
            print(f'generating streams for month {month}')
            for day in days[:10]:
                print(f'generating streams for day {day}')
                try:
                    sale_date = date(year=year, month=month, day=day)
                except ValueError: # invalid date
                    pass
                print(sale_date)
                all_streams += [generate_stream(sale_date) for _i in range(randrange(20))]

    data = pd.DataFrame(all_streams)
    print(data.head())


if __name__ == '__main__':
    main()