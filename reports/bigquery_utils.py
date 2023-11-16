from typing import List, Dict
from django.http import JsonResponse, HttpRequest
from google.cloud import bigquery

def get_traffic_violations(request: HttpRequest) -> JsonResponse:
    """
    Query traffic violation data from BigQuery and return as JSON.

    Args:
        request (HttpRequest): The incoming request.

    Returns:
        JsonResponse: The JSON response containing the traffic violation data.
    """
    # Instantiate a BigQuery client.
    client = bigquery.Client()

    # Define the SQL query.
    query = """
    SELECT 
        v.license_plate, 
        v.date, 
        v.time, 
        v.violation, 
        v.status, 
        v.location, 
        v.officer,
        v.traffic_violation_id,
        m.file
    FROM 
        `traffic_violation_db.reports_trafficviolation` v
    LEFT JOIN 
        `traffic_violation_db.reports_mediafile` m ON v.traffic_violation_id = m.traffic_violation_id
    """
    
    # Execute the query.
    query_job = client.query(query)

    # Get the query results.
    results = query_job.result()

    # Prepare the data for the JSON response.
    data = []
    for row in results:
        lat, lng = map(float, row.location.split(','))
        data.append({
            'lat': lat,
            'lng': lng,
            'title': f'{row.license_plate} - {row.violation}',
            'media': row.file if row.file else 'path/to/default/image.jpg'
        })

    # Return the data as a JSON response.
    return JsonResponse(data, safe=False) 

def save_to_bigquery(traffic_violation: 'TrafficViolation', media_files: List['MediaFile']) -> None:
    """
    Save traffic violation and media file data to BigQuery.

    Args:
        traffic_violation (TrafficViolation): The traffic violation data to save.
        media_files (List[MediaFile]): The media file data to save.
    """
    # Instantiate a BigQuery client.
    client = bigquery.Client()

    # Specify the project ID, dataset ID, and table IDs.
    project_id = "pivotal-equinox-404812"
    dataset_id = "traffic_violation_db"
    table_id_violation = "reports_trafficviolation"
    table_id_media = "reports_mediafile"

    # Prepare the traffic violation data to insert.
    rows_to_insert_violation = [
        {
            "license_plate": traffic_violation.license_plate,
            "date": traffic_violation.date.strftime("%Y-%m-%d"),
            "time": traffic_violation.time.strftime("%H:%M:%S"),
            "violation": traffic_violation.violation,
            "status": traffic_violation.status,
            "location": traffic_violation.location,
            "officer": traffic_violation.officer.username if traffic_violation.officer else None,
            "traffic_violation_id": traffic_violation.id,
        },
    ]

    # Insert the traffic violation data.
    dataset_ref = client.dataset(dataset_id, project=project_id)
    table_ref_violation = dataset_ref.table(table_id_violation)
    table_violation = client.get_table(table_ref_violation)
    client.insert_rows_json(table_violation, rows_to_insert_violation)

    # Prepare the media file data to insert.
    rows_to_insert_media = [
        {
            "traffic_violation_id": traffic_violation.id,
            "file": media_file.file.name,
            # Additional fields as needed.
        }
        for media_file in media_files
    ]

    # Insert the media file data.
    table_ref_media = dataset_ref.table(table_id_media)
    table_media = client.get_table(table_ref_media)
    client.insert_rows_json(table_media, rows_to_insert_media)
