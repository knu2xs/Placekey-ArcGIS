import importlib
import os

from arcgis import GeoAccessor
from arcgis.geometry import Geometry
from requests import post

if importlib.util.find_spec("dotenv") is not None:
    from dotenv import find_dotenv, load_dotenv
    load_dotenv(find_dotenv())

# try to load the placekey_arcgis key from the environment variables
pk_key = os.getenv('PLACEKEY_KEY') if 'PLACEKEY_KEY' in os.environ.keys() else None

# save the url for ease of use
pk_url = 'https://api.placekey.io/v1/placekey'


def _get_headers(new_key:str=None)->dict:
    """Helper to make it easier to handle ad hoc api keys."""
    if new_key is not None:
        headers = {'apikey': new_key}
    elif pk_key is not None:
        headers = {'apikey': pk_key}
    else:
        raise Exception('A Placekey API key must be provided with the post request. You can get one at '
                        'https://placekey.io')

    headers['Content-Type'] = 'application/json'

    return headers


def _get_placekey(body:dict, placekey_api_key:str = None) -> str:
    """
    Helper function to look up placekeys.
    :param body:
    :param placekey_api_key:
    :return:
    """
    # put the api key in the header
    headers = _get_headers(placekey_api_key)

    # post the request
    res = post(pk_url, headers=headers, json=body)

    # attempt to extract the placekey and handle errors
    if res.status_code == 200:
        pk = res.json()['placekey']

    elif res.status_code == 400:
        res_d = res.json()
        if 'error' in res_d.keys():
            raise Exception(res_d['error'])
        elif 'message' in res_d.keys():
            raise Exception(res_d['message'])
        else:
            raise Exception('Bad request. Recieved 400 response.')

    elif res.status_code == 401:
        raise Exception('Unauthorized request. Please check Placekey Key.')

    elif res.status_code == 439:
        raise Exception('Too Many Requests')

    elif str(res.status_code).startswith('5'):
        raise Exception('Internal Server Error')

    return pk


def get_placekey_from_geometry(geometry: Geometry, placekey_api_key: str = None) -> str:
    """
    Lookup the full Placekey for a given Esri Point Geometry.

    :param geometry: ArcGIS Python API geometry.
    :param placekey_api_key: Placekey API key for making requests.

    :return: String with full Placekey for given location.
    """
    # pull out the centroid coordinates
    x, y = geometry.centroid

    # populate the coordinates in the body
    body = {"query": {"latitude": y, "longitude": x}}

    pk = _get_placekey(body, placekey_api_key)

    return pk


def get_placekey_from_address(street_address:str, city:str, state:str, postal_code:str, iso_country_code:str='US',
                              placekey_api_key: str = None) -> str:
    """
    Look up the full Placekey for a given address string.

    :param street_address: Street address with suite, floor, or apartment.
    :param city: The city.
    :param state: Two character state identifier.
    :param postal_code: Postal code identifier; typically five numbers.
    :param iso_country_code: Two character country identifier. Defaults to "US".
    :param placekey_api_key: Placekey API key for making requests.

    :return: Placekey string.
    """
    # check a couple of things for the parameter inputs
    assert len(state) == 2, f'state must be two character identifier, not "{state}".'
    assert len(iso_country_code) == 2, 'iso_country_code must be two character identifier, not ' \
                                       f'"{iso_country_code}".'

    body = {
        "query": {
            "street_address": street_address,
            "city": city,
            "region": state,
            "postal_code": postal_code,
            "iso_country_code": iso_country_code
        }
    }

    pk = _get_placekey(body, placekey_api_key)

    return pk
