import re
import googlemaps
from django.conf import settings

def is_address(address):
    pattern = re.compile(r"[街道|路|巷|弄|號|樓|室|樓層|棟|單元|號|樓|室|房間|門牌|鄉鎮市區|區|縣市|省]|[0-9]+[街道|路|巷|弄|號|樓|室|樓層|棟|單元|號|樓|室|房間|門牌|鄉鎮市區|區|縣市|省]|[0-9]+[街道|路|巷|弄|號|樓|室|樓層|棟|單元|號|樓|室|房間|門牌|鄉鎮市區|區|縣市|省]-[0-9]+")
    return pattern.search(address)

def get_latitude_and_longitude(address):
    if is_address(address):
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
        geocode_result = gmaps.geocode(address)

        if not geocode_result:
            return None, None

        location = geocode_result[0]['geometry']['location']
        return location['lng'], location['lat']
    else:
        return None, None

def process_input(input_string):
    lat, lng = get_latitude_and_longitude(input_string)
    if lat is not None and lng is not None:
        return f"{lng},{lat}"
    else:
        return input_string
