import json
import datetime
import requests

from caching import disk_cache
from logger import logger

class CustomError(Exception):
    """Base class for custom exceptions."""
    pass


class APICallError(CustomError):
    """Exception raised for errors during API calls."""
    def __init__(self, message="Error during API call."):
        self.message = message
        super().__init__(self.message)



@disk_cache
def get_cpi_values_for_year(year: int, series='CUUR0000SA0') -> dict:
    """
    TODO: validate inputs and response data
    """
    headers = {'Content-type': 'application/json'}
    data = json.dumps(
        {
            "seriesid": [series],
            "startyear": year,
            "endyear": year
        }
    )
    response = requests.post(
        url='https://api.bls.gov/publicAPI/v2/timeseries/data/',
        data=data,
        headers=headers,
        timeout=3.0
    )
    response_json = json.loads(response.text)
    if response_json['status'] == 'REQUEST_NOT_PROCESSED':
        logger.info(response_json['message'])
        raise APICallError

    cpi_values = response_json['Results']['series'][0]['data']
    return cpi_values


def restructure_cpi_dict(cpi_values: dict) -> dict:
    """
    Restructure CPI dictionary so the years and months are 
    keys rather than values in a list of dictionaries
    """
    years = list(set(i['year'] for i in cpi_values))
    months = list(set(i['period'] for i in cpi_values))
    years.sort()
    months.sort()
    cpi = {}
    for yy in years:
        y = int(yy)
        cpi[y] = {}
        for mm in months:
            m = int(mm[1:])
            values = [
                d['value'] for d in cpi_values if
                    (d['year'] == yy) and (d['period'] == mm)
            ]
            if values:
                cpi[y][m] = float(values[0])
    return cpi


def get_cpi_data(start_year: int, end_year: int, series='CUUR0000SA0') -> dict:
    """
    TODO: validate inputs and response data
    """

    all_years = []
    for year in range(start_year, end_year):
        all_years.append(get_cpi_values_for_year(year, series=series))

    cpi_data = {}
    for year in all_years:
        cpi_data[year] = year

    return all_years


def get_most_recent_cpi(cpi_data: dict, year: int, month: int) -> float:
    """
    Look up the CPI value for a given year and month. If the CPI data
    is not available, then the function will check to see if CPI data
    is available for up to 3 months prior
    """

    tries = 0
    recent_cpi = None
    while not recent_cpi and tries < 3:
        logger.info('Looking up CPI for date: %s', f'{year}-{month}')
        try:
            recent_cpi = cpi_data[year][month]
        except KeyError:
            if month == 1:
                # go to Dec of previous year
                month = 12
                year -= 1
            else:
                # go to previous month in year
                month -= 1
            tries += 1

    return recent_cpi


def adjust_amount(
        cpi_data: dict,
        amount: float,
        from_date: datetime.date,
        to_date: datetime.date
    ) -> float:
    """
    Adjusts an amount using the Consumer Price Index across two dates
    """
    from_cpi = get_most_recent_cpi(cpi_data, from_date.year, from_date.month)
    to_cpi = get_most_recent_cpi(cpi_data, to_date.year, to_date.month)
    return amount * (to_cpi / from_cpi)
