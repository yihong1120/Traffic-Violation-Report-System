from typing import List, Dict, Optional
from django.http import JsonResponse, HttpRequest
from reports.models import TrafficViolation, MediaFile
from django.db.models import QuerySet, Q
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from datetime import datetime, timedelta

def get_user_records(id: int) -> List[Dict]:
    """
    Retrieve records for a specific user from the MySQL database.

    Args:
        id: The id of user for which records are to be retrieved.

    Returns:
        A list of dictionaries representing the user's records.
    """
    return list(TrafficViolation.objects.filter(id=id).values())

def get_media_records(record_id: str) -> List[Dict]:
    """
    Retrieve media records for a specific traffic violation record from the MySQL database.

    Args:
        record_id: The ID of the traffic violation record.

    Returns:
        A list of dictionaries representing the media records for the specified record.
    """
    return list(MediaFile.objects.filter(traffic_violation_id=record_id).values())

def update_traffic_violation(data: Dict, selected_record_id: str):
    """
    Update a specific traffic violation record in the MySQL database.

    Args:
        data: The updated data for the traffic violation record.
        selected_record_id: The ID of the selected traffic violation record.
    """
    updated_rows = TrafficViolation.objects.filter(
        traffic_violation_id=selected_record_id
    ).update(**data)

    if not updated_rows:
        raise ObjectDoesNotExist(f"Record with ID {selected_record_id} does not exist.")

@transaction.atomic
def update_media_files(selected_record_id: str, new_media_files: List[str], removed_media: List[str]):
    """
    Updates media files associated with a specific traffic violation record in the MySQL database.

    Args:
        selected_record_id: The ID of the selected traffic violation record.
        new_media_files: The new media files to be added.
        removed_media: The media files to be removed.
    """
    MediaFile.objects.filter(
        file__in=removed_media, traffic_violation_id=selected_record_id
    ).delete()

    MediaFile.objects.bulk_create([
        MediaFile(traffic_violation_id=selected_record_id, file=file_name)
        for file_name in new_media_files
    ])

def search_traffic_violations(keyword: str = '', time_range: str = 'all', 
                             from_date: Optional[datetime] = None, 
                             to_date: Optional[datetime] = None) -> JsonResponse:
    """
    Searches for traffic violations based on various filters such as keywords and time range.

    Args:
        keyword: A string for filtering the violations. Defaults to an empty string.
        time_range: A string indicating the time range for the filter. Can be '1day', '1week', 
                    '1month', '6months', '1year', or 'all'. Defaults to 'all'.
        from_date: The starting date for custom time range filter. Defaults to None.
        to_date: The ending date for custom time range filter. Defaults to None.

    Returns:
        JsonResponse: A JSON response containing the list of traffic violations that match the filters.

    """

    violations: QuerySet = TrafficViolation.objects.all()

    # Keyword search
    if keyword:
        violations = violations.filter(
            Q(license_plate__icontains=keyword) | 
            Q(violation__icontains=keyword) |
            Q(location__icontains=keyword) |
            Q(officer__icontains=keyword)
        )

    # Time range search
    if time_range == 'custom' and from_date and to_date:
        # Custom date range
        violations = violations.filter(date__range=[from_date, to_date])
    else:
        # Pre-set date ranges
        end_date: datetime = datetime.now()
        start_date: Optional[datetime] = {
            '1day': end_date - timedelta(days=1),
            '1week': end_date - timedelta(weeks=1),
            '1month': end_date - timedelta(days=30),
            '6months': end_date - timedelta(days=180),
            '1year': end_date - timedelta(days=365)
        }.get(time_range)

        if start_date:
            violations = violations.filter(date__range=[start_date, end_date])

    # Transform data into the required format
    markers: List[dict] = [
        {
            'traffic_violation_id': str(violation.traffic_violation_id),  # Convert UUID to string
            'lat': violation.latitude,  # Extract and convert latitude to float
            'lng': violation.longtitude,  # Extract and convert longitude to float
        }
        for violation in violations
    ]

    return markers


def get_traffic_violation_markers(request: HttpRequest) -> JsonResponse:
    """
    Retrieves markers for traffic violations to be displayed on a map.

    Args:
        request: The HttpRequest containing the request parameters.

    Returns:
        A JsonResponse containing the markers for traffic violations.
    """
    violations = TrafficViolation.objects.values('traffic_violation_id', 'latitude', 'longtitude')
    markers = [
        {
            'traffic_violation_id': str(v['traffic_violation_id']),
            'lat': float(v['latitude']),
            'lng': float(v['longtitude']),
        }
        for v in violations
    ]

    return markers


def get_traffic_violation_details(request: HttpRequest, traffic_violation_id: str) -> JsonResponse:
    """
    Provides detailed information about a specific traffic violation.

    Args:
        request: The HttpRequest containing the request parameters.
        traffic_violation_id: The ID of the traffic violation.

    Returns:
        A JsonResponse containing detailed information about the specified traffic violation.
    """
    try:
        violation = TrafficViolation.objects.get(traffic_violation_id=traffic_violation_id)
        media_files = list(MediaFile.objects.filter(traffic_violation=violation).values_list('file', flat=True))

        location = (violation.address if violation.user_input_type == "address"
            else f"{violation.latitude}, {violation.longtitude}")

        lat, lng = violation.latitude, violation.longtitude
        data = {
            'lat': lat,
            'lng': lng,
            'title': f'{violation.license_plate} - {violation.violation}',
            'media': media_files,
            'license_plate': violation.license_plate,
            'date': violation.date,
            'time': violation.time.strftime('%H:%M'),
            'violation': violation.violation,
            'location': location,
            'status': violation.status,
            'officer': violation.officer.username if violation.officer else 'None'
        }

        return data

    except TrafficViolation.DoesNotExist:
        return JsonResponse({'error': 'Traffic violation not found'}, status=404)

@transaction.atomic
def save_to_mysql(traffic_violation: TrafficViolation, media_files: List[str]) -> None:
    """
    Save traffic violation and media file data to the MySQL database.

    Args:
        traffic_violation: The traffic violation data to be saved.
        media_files: The media files associated with the traffic violation.
    """
    traffic_violation.save()
    MediaFile.objects.bulk_create([
        MediaFile(traffic_violation=traffic_violation, file=file_name)
        for file_name in media_files
    ])
