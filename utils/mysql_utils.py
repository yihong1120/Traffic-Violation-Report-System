from typing import List, Dict
from django.http import JsonResponse, HttpRequest
from .models import TrafficViolation, MediaFile
from django.conf import settings
from django.db.models import Q
import datetime

def get_user_records(username: str) -> List[Dict]:
    """
    Retrieve records for a specific user from the MySQL database.

    Args:
    - username: A string representing the username for which records are to be retrieved.

    Returns:
    A list of dictionaries representing the records for the specified user.
    """
    records = TrafficViolation.objects.filter(username=username).values()
    return list(records)

def get_media_records(record_id: str) -> List[Dict]:
    """
    Retrieve media records for a specific traffic violation record from the MySQL database.

    Args:
    - record_id: A string representing the ID of the traffic violation record.

    Returns:
    A list of dictionaries representing the media records for the specified traffic violation record.
    """
    media_records = MediaFile.objects.filter(traffic_violation_id=record_id).values()
    return list(media_records)

def update_traffic_violation(data: Dict, selected_record_id: str):
    """
    Update a specific traffic violation record in the MySQL database.

    Args:
    - data: A dictionary containing the updated data for the traffic violation record.
    - selected_record_id: A string representing the ID of the selected traffic violation record.
    """
    TrafficViolation.objects.filter(traffic_violation_id=selected_record_id).update(**data)

def update_media_files(selected_record_id: str, new_media_files: List[str], removed_media: List[str]):
    """
    Updates media files associated with a specific traffic violation record in the MySQL database.

    Args:
    - selected_record_id: A string representing the ID of the selected traffic violation record.
    - new_media_files: A list of strings representing the new media files to be added.
    - removed_media: A list of strings representing the media files to be removed.
    """
    # Deleting removed media files
    for media_url in removed_media:
        MediaFile.objects.filter(file=media_url, traffic_violation_id=selected_record_id).delete()

    # Adding new media files
    for file_name in new_media_files:
        MediaFile.objects.create(traffic_violation_id=selected_record_id, file=file_name)

def search_traffic_violations(request: HttpRequest) -> JsonResponse:
    '''
    This function will search for traffic violations based on a keyword and/or a date range specified in the request parameters.

    Args:
    - request: An instance of HttpRequest containing the request parameters.

    Returns:
    A JsonResponse containing the search results for traffic violations.
    '''
    keyword = request.GET.get('keyword', '')
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Build the query
    violations = TrafficViolation.objects.all()
    if keyword:
        violations = violations.filter(
            Q(license_plate__icontains=keyword) | 
            Q(violation__icontains=keyword) |
            Q(location__icontains=keyword)
        )
    if from_date and to_date:
        violations = violations.filter(date__range=[from_date, to_date])

    # Prepare the response data
    data = list(violations.values())
    return JsonResponse(data, safe=False)


def get_traffic_violation_markers(request: HttpRequest) -> JsonResponse:
    '''
    This function retrieves markers for traffic violations to be displayed on a map.

    Args:
    - request: An instance of HttpRequest containing the request parameters.

    Returns:
    A JsonResponse containing the markers for traffic violations.
    '''
    violations = TrafficViolation.objects.values('traffic_violation_id', 'location')
    markers = [
        {
            'traffic_violation_id': str(v['traffic_violation_id']),  # Convert UUID to string
            'lat': float(v['location'].split(',')[0]),  # Extract and convert latitude to float
            'lng': float(v['location'].split(',')[1])   # Extract and convert longitude to float
        }
        for v in violations
    ]
    return JsonResponse(markers, safe=False)


def get_traffic_violation_details(request: HttpRequest, traffic_violation_id: str) -> JsonResponse:
    '''
    This function provides detailed information about a specific traffic violation.

    Args:
    - request: An instance of HttpRequest containing the request parameters.
    - traffic_violation_id: A string representing the ID of the traffic violation.

    Returns:
    A JsonResponse containing detailed information about the specified traffic violation.
    '''
    try:
        violation = TrafficViolation.objects.get(traffic_violation_id=traffic_violation_id)
        media_files = MediaFile.objects.filter(traffic_violation=violation).values_list('file', flat=True)

        lat, lng = map(float, violation.location.split(','))
        title = f'{violation.license_plate} - {violation.violation}'

        # Construct a list of media files with full paths
        full_media_files = [file_name for file_name in media_files]

        data = {
            'lat': lat,
            'lng': lng,
            'title': title,
            'media': full_media_files,  # Use a list of media files with full paths
            'license_plate': violation.license_plate,
            'date': violation.date,
            'time': violation.time.strftime('%H:%M'),
            'violation': violation.violation,
            'status': violation.status,
            'officer': violation.officer.username if violation.officer else 'None'
        }

        return JsonResponse(data)
    except TrafficViolation.DoesNotExist:
        return JsonResponse({'error': 'Traffic violation not found'}, status=404)

def save_to_mysql(traffic_violation: 'TrafficViolation', media_files: List[str]) -> None:
    """
    Save traffic violation and media file data to the MySQL database.

    Args:
    - traffic_violation: An instance of TrafficViolation representing the traffic violation data to be saved.
    - media_files: A list of strings representing the media files associated with the traffic violation.
    """
    # Save traffic_violation object
    traffic_violation.save()

    # Save each media file
    for file_name in media_files:
        MediaFile.objects.create(traffic_violation=traffic_violation, file=file_name)