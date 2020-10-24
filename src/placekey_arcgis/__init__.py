__title__ = 'placekey_arcgis'
__version__ = '0.2.0-dev0'
__author__ = 'Joel McCune'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2020 by Joel McCune'

from .main import get_placekey_from_address, get_placekey_from_geometry

__all__ = ['get_placekey_from_geometry', 'get_placekey_from_address']
