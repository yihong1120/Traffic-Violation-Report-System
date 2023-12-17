import re
import random
import os
import uuid
import googlemaps
from django.conf import settings
from django.http import HttpRequest
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from typing import Tuple, Optional, List
from reports.forms import ReportForm
from reports.models import TrafficViolation, MediaFile
from .mysql_utils import (
    update_media_files,
)


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

def coordinates_to_address(lat, lng):
    """
    Convert latitude and longitude to an address using the Google Maps API.

    Args:
        lat (float): The latitude to convert.
        lng (float): The longitude to convert.

    Returns:
        str: The address corresponding to the latitude and longitude, or None if no address was found.
    """
    # 初始化 Google Maps 客户端
    gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

    # 进行反向地理编码查询
    result = gmaps.reverse_geocode((lat, lng))

    if result:
        # 返回第一个结果的格式化地址
        return result[0]['formatted_address']

def extract_lat_long(s):
    """
    Extract latitude and longitude from a string.

    Args:
        s (str): The string to extract latitude and longitude from.

    Returns:
        tuple: The latitude and longitude extracted from the string, or None if no latitude and longitude were found.
    """
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", s)
    coordinates = [float(num) for num in numbers]

    if len(coordinates) >= 2:
        latitude, longitude = coordinates[:2]
        if -90 <= latitude <= 90 and -180 <= longitude <= 180:
            return latitude, longitude

    return None

def process_input(input_string: str) -> str:
    """
    Process an input string, trying to geocode it if it is an address.

    Args:
        input_string (str): The input string to process.

    Returns:
        str: The longitude and latitude of the input string if it is an address, or the original input string otherwise.
    """
    # Check if the input is an address.
    if is_address(input_string):
        # Try to get the longitude and latitude of the input string.
        lat, lng = get_latitude_and_longitude(input_string)
        # If both longitude and latitude were found, return them as a string.
        if lat is not None and lng is not None:
            return input_string, lat, lng, "address" #user_input is address
    else:
        # If the input string could not be geocoded, return it unchanged.
        lat, lng = extract_lat_long(input_string)
        address = coordinates_to_address(lat, lng)
        # f"{lng},{lat}" to address
        # return address, f"{lng},{lat}", #user_input is coords
        return address, lat, lng, "coords"

    return None

class ReportManager:
    """
    Manages the retrieval and processing of traffic violation reports.

    Attributes:
        request (HttpRequest): The HTTP request object.
        username (str): The username of the current user.
    """

    def __init__(self, request: HttpRequest, username: str):
        """
        Initialise the ReportManager with the given request and username.
        """
        self.request = request
        self.username = username

    def get_selected_record(self) -> Optional[TrafficViolation]:
        """
        Retrieve the selected traffic violation record.

        Returns:
            The TrafficViolation instance if found, otherwise None.
        """
        selected_record_id = self.request.GET.get('record_id')
        if selected_record_id:
            return get_object_or_404(TrafficViolation, traffic_violation_id=selected_record_id, username=self.username)
        return None

    def get_media_urls(self, selected_record: TrafficViolation) -> List[str]:
        """
        Get the media URLs associated with the selected record.

        Args:
            selected_record: The TrafficViolation instance.

        Returns:
            A list of media file URLs.
        """
        selected_record_media = MediaFile.objects.filter(traffic_violation=selected_record)
        return [media.file.url for media in selected_record_media]

    def get_initial_form_data(self, selected_record: TrafficViolation) -> dict:
        """
        Prepare the initial data for the report form based on the selected record.

        Args:
            selected_record: The TrafficViolation instance.

        Returns:
            A dictionary with initial data for the form.
        """
        return {
            'license_plate': selected_record.license_plate,
            'date': selected_record.date,
            'hour': selected_record.time.hour,
            'minute': selected_record.time.minute,
            'violation': selected_record.violation,
            'status': selected_record.status,
            #location
            'address': selected_record.address, # user input is address
            'coords': f"{selected_record.latitude}, {selected_record.longitude}",# user input is coords
            'officer': selected_record.officer.username if selected_record.officer else ""
        }

    def handle_form_submission(self, form: ReportForm, selected_record: TrafficViolation) -> ReportForm:
        """
        Process the form submission for a traffic violation report.

        Args:
            form: The form instance to be processed.
            selected_record: The TrafficViolation instance being updated.

        Returns:
            The form instance after processing.
        """
        if self.request.method == 'POST':
            form = ReportForm(self.request.POST, self.request.FILES)
            if form.is_valid():
                self.update_record(form.cleaned_data, selected_record)
                self.handle_media_files(selected_record)
                messages.success(self.request, "The record and media files have been successfully updated.")
                return redirect('edit_report')
        return form

    def update_record(self, cleaned_data: dict, selected_record: TrafficViolation) -> None:
        """
        Update the selected record with cleaned data from the form.

        Args:
            cleaned_data: The validated data from the form.
            selected_record: The TrafficViolation instance to update.
        """
        for field, value in cleaned_data.items():
            setattr(selected_record, field, value)
        selected_record.save()

    def handle_media_files(self, selected_record: TrafficViolation) -> None:
        """
        Handle the uploading and removal of media files associated with the record.

        Args:
            selected_record: The TrafficViolation instance whose media files are being managed.
        """
        fs = FileSystemStorage(location=settings.MEDIA_ROOT)
        saved_files = []

        for media_file in self.request.FILES.getlist('media'):
            _, file_extension = os.path.splitext(media_file.name)
            unique_filename = str(uuid.uuid4()) + file_extension
            fs.save(unique_filename, media_file)
            saved_files.append(unique_filename)

        removed_media = self.request.POST.get('removed_media', '').split(';')
        self.remove_media_files(removed_media)
        update_media_files(selected_record.traffic_violation_id, saved_files, removed_media)

    def remove_media_files(self, removed_media: List[str]) -> None:
        """
        Remove media files that are no longer needed.

        Args:
            removed_media: A list of filenames to be removed.
        """
        for file_name in removed_media:
            if file_name:
                file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                    except PermissionError as e:
                        print(f"Error removing file {file_path}: {e}")
                else:
                    print(f"File not found or is a directory: {file_path}")

    @classmethod
    def get_record_form_and_media(cls, request: HttpRequest, username: str) -> Tuple[Optional[TrafficViolation], Optional[ReportForm], List[str]]:
        """
        Class method to retrieve the selected record, form, and media URLs.

        Args:
            request: The HTTP request object.
            username: The username of the current user.

        Returns:
            A tuple containing the selected record, form, and media URLs.
        """
        manager = cls(request, username)
        selected_record = manager.get_selected_record()
        form = None
        media_urls = []

        if selected_record:
            media_urls = manager.get_media_urls(selected_record)
            initial_data = manager.get_initial_form_data(selected_record)
            form = ReportForm(initial=initial_data)
            form = manager.handle_form_submission(form, selected_record)

        return selected_record, form, media_urls