import re
import random
import googlemaps
from django.conf import settings
from typing import Tuple, Optional

def generate_random_code() -> str:
    """
    Generate a random 6-digit code.

    Returns:
        str: The generated random code.
    """
    # Use list comprehension to generate a list of 6 random digits, then join them into a string.
    return ''.join(random.choice('0123456789') for _ in range(6))

def is_address(address: str) -> bool:
    """
    Check if a string is likely to be an address based on a regular expression.

    Args:
        address (str): The string to check.

    Returns:
        bool: True if the string matches the address pattern, False otherwise.
    """
    # Compile a regular expression pattern for addresses.
    pattern = re.compile(r"[街道|路|巷|弄|號|樓|室|樓層|棟|單元|號|樓|室|房間|門牌|鄉鎮市區|區|縣市|省]|[0-9]+[街道|路|巷|弄|號|樓|室|樓層|棟|單元|號|樓|室|房間|門牌|鄉鎮市區|區|縣市|省]|[0-9]+[街道|路|巷|弄|號|樓|室|樓層|棟|單元|號|樓|室|房間|門牌|鄉鎮市區|區|縣市|省]-[0-9]+")
    # Search the input string for the address pattern.
    return pattern.search(address) is not None

def get_latitude_and_longitude(address: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Get the latitude and longitude of an address using the Google Maps API.

    Args:
        address (str): The address to geocode.

    Returns:
        tuple: The longitude and latitude of the address, or (None, None) if the address could not be geocoded.
    """
    # Check if the input is an address.
    if is_address(address):
        # Create a client for the Google Maps API.
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        # Get the geocoding result for the address.
        geocode_result = gmaps.geocode(address)

        # If no result was found, return None for both longitude and latitude.
        if not geocode_result:
            return None, None

        # Extract the location from the geocoding result.
        location = geocode_result[0]['geometry']['location']
        # Return the longitude and latitude.
        return location['lng'], location['lat']
    else:
        # If the input is not an address, return None for both longitude and latitude.
        return None, None

def process_input(input_string: str) -> str:
    """
    Process an input string, trying to geocode it if it is an address.

    Args:
        input_string (str): The input string to process.

    Returns:
        str: The longitude and latitude of the input string if it is an address, or the original input string otherwise.
    """
    # Try to get the longitude and latitude of the input string.
    lat, lng = get_latitude_and_longitude(input_string)
    # If both longitude and latitude were found, return them as a string.
    if lat is not None and lng is not None:
        return f"{lng},{lat}"
    else:
        # If the input string could not be geocoded, return it unchanged.
        return input_string
