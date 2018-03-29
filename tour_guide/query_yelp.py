from __future__ import print_function

import requests
from typing import List

from urllib.parse import quote
from urllib.parse import urlencode

from deprecation import deprecated


@deprecated(details='As of 2018-03-01, Yelp uses API Keys instead of OAuth '
                    'tokens. Please see '
                    'https://www.yelp.com/developers/documentation/v3/authentication '
                    'for details.')
def obtain_bearer_token(host: str, path: str, CLIENT_ID: str,
                        CLIENT_SECRET: str, GRANT_TYPE: str) -> str:
    """Given a bearer token, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        str: OAuth bearer token, obtained using client_id and client_secret.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
    })
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    return bearer_token


def request(host: str, path: str, bearer_token: str,
            url_params: dict=None) -> dict:
    """Given a bearer token, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        bearer_token (str): the API's authentication token
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % bearer_token,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(categories: List[str], lat: float, lng: float, radius: int,
           API_HOST: str, SEARCH_PATH: str, API_KEY: str) -> dict:
    """Query the Search API by a search categories and location.
    Args:
        categories (List[str]): The search categories passed to the API.
        lat (float): The latitude of the search location
        lng (float): The longitude of the search location
        radius (int): The maximum distance from the search location in km
        API_HOST (str): The domain host of Yelp's API.
        SEARCH_PATH (str): The path of Yelp's API after the domain.
        API_KEY (str): The Yelp app's API Key
    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'categories': '+'.join(categories),
        'latitude': lat,
        'longitude': lng,
        'radius': radius,
        # To be updated with pagination functionality in a future PR.
        'limit': 50
    }
    return request(API_HOST, SEARCH_PATH, API_KEY, url_params=url_params)


def pare_businesses(businesses: dict):
    removals = ['distance', 'phone', 'image_url', 'display_phone',
                'id', 'location']
    for item in businesses:
        for r in removals:
            del item[r]


def determine_categories(data: dict) -> List[str]:
    """Determine for which categories to query Yelp's API.

    Args:
        data (dict): Data specifying which categories to query (details TBD)
    """
    # To be updated once decision logic has been determine
    return ['zoos', 'beaches', 'restaurants']


def query_api(data: dict, parameters: dict,
              API_HOST: str, SEARCH_PATH: str, API_KEY: str) -> dict:
    """Queries the API by the input values from the user.
    Args:
        data (dict): Data specifying which categories to query (details TBD)
        parameters (dict): An object specifying the circle to query. Example:
            {'response': {'circle': {'center': {'lat': 41.9, 'lng': -87.6},
                                     'radius': 10}}}
        API_HOST (str): The domain host of Yelp's API.
        SEARCH_PATH (str): The path of Yelp's API after the domain.
        API_KEY (str): The Yelp app's API Key
    """
    categories = determine_categories(data)

    lat = parameters['response']['circle']['center']['lat']
    lng = parameters['response']['circle']['center']['lng']
    radius = parameters['response']['circle']['radius'] + 100

    response = search(categories, lat, lng, radius,
                      API_HOST, SEARCH_PATH, API_KEY)

    businesses = response.get('businesses')

    if not businesses:
        message = u'No businesses for {0} in {1} found.'
        message = message.format(categories, parameters)
        print(message)
        return

    pare_businesses(businesses)

    return businesses
