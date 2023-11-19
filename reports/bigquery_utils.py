from typing import List, Dict
from django.http import JsonResponse, HttpRequest
from django.core.files.uploadedfile import InMemoryUploadedFile
from google.cloud import bigquery
import datetime

def get_user_records(username: str) -> List[Dict]:
    """
    Retrieve records for a specific user from BigQuery.

    This function executes a query to fetch all traffic violation records
    associated with the given username from the BigQuery table.

    Args:
        username (str): The username to query for.

    Returns:
        List[Dict]: A list of dictionaries, each representing a traffic violation record.
    """
    client = bigquery.Client()
    query = (
        f"SELECT * FROM `pivotal-equinox-404812.traffic_violation_db.reports_trafficviolation` "
        f"WHERE username = '{username}'"
    )
    query_job = client.query(query)
    return [dict(row) for row in query_job.result()]

def get_media_records() -> List[Dict]:
    """
    Retrieve all media records from BigQuery.

    This function fetches media file information related to traffic violations
    from the BigQuery table. It's limited to a maximum of 1000 records for performance.

    Returns:
        List[Dict]: A list of dictionaries, each representing a media file record.
    """
    client = bigquery.Client()
    media_query = (
        "SELECT * FROM `pivotal-equinox-404812.traffic_violation_db.reports_mediafile` "
        "LIMIT 1000"
    )
    media_query_job = client.query(media_query)
    return [dict(row) for row in media_query_job.result()]

def update_traffic_violation(data: Dict, selected_record_id: str):
    """
    Update a specific traffic violation record in BigQuery.

    This function constructs and executes a SQL query to update a traffic violation record
    in BigQuery based on the provided data dictionary and record ID.

    Args:
        data (Dict): The data dictionary containing traffic violation information.
        selected_record_id (str): The ID of the traffic violation record to update.
    """
    client = bigquery.Client()

    # Construct the update statement and parameters
    update_query = """
        UPDATE `pivotal-equinox-404812.traffic_violation_db.reports_trafficviolation`
        SET license_plate = @license_plate, 
            date = @date, 
            time = @time, 
            violation = @violation, 
            status = @status, 
            location = @location, 
            officer = @officer
        WHERE traffic_violation_id = @traffic_violation_id
    """

    params = [
        bigquery.ScalarQueryParameter("license_plate", "STRING", data['license_plate']),
        bigquery.ScalarQueryParameter("date", "DATE", data['date']),
        bigquery.ScalarQueryParameter("time", "STRING", data['time'].strftime("%H:%M:%S")),
        bigquery.ScalarQueryParameter("violation", "STRING", data['violation']),
        bigquery.ScalarQueryParameter("status", "STRING", data['status']),
        bigquery.ScalarQueryParameter("location", "STRING", data['location']),
        bigquery.ScalarQueryParameter("officer", "STRING", data['officer']),
        bigquery.ScalarQueryParameter("traffic_violation_id", "STRING", selected_record_id),
    ]

    job_config = bigquery.QueryJobConfig(query_parameters=params)

    # Execute the update
    client.query(update_query, job_config=job_config).result()

def update_media_files(selected_record_id: str, media_files: List[InMemoryUploadedFile]):
    """
    Update media files associated with a specific traffic violation record in BigQuery.

    This function first deletes any existing media files associated with the traffic violation
    record and then inserts the new media file information.

    Args:
        selected_record_id (str): The ID of the traffic violation record.
        media_files (List[InMemoryUploadedFile]): A list of media files to be associated with the record.
    """
    client = bigquery.Client()

    # Delete existing media files
    delete_query = """
        DELETE FROM `pivotal-equinox-404812.traffic_violation_db.reports_mediafile`
        WHERE traffic_violation_id = @traffic_violation_id
    """
    delete_params = [
        bigquery.ScalarQueryParameter("traffic_violation_id", "STRING", selected_record_id),
    ]
    delete_job_config = bigquery.QueryJobConfig(query_parameters=delete_params)
    client.query(delete_query, delete_job_config).result()

    # Insert new media files
    for media_file in media_files:
        insert_query = """
            INSERT INTO `pivotal-equinox-404812.traffic_violation_db.reports_mediafile` (file, traffic_violation_id)
            VALUES (@file, @traffic_violation_id)
        """
        insert_params = [
            bigquery.ScalarQueryParameter("file", "STRING", media_file.name),
            bigquery.ScalarQueryParameter("traffic_violation_id", "STRING", selected_record_id),
        ]
        insert_job_config = bigquery.QueryJobConfig(query_parameters=insert_params)
        client.query(insert_query, insert_job_config).result()

def search_traffic_violations(request: HttpRequest) -> JsonResponse:
    """
    Retrieve filtered traffic violation data from BigQuery based on the search parameters.

    This function constructs a SQL query to filter traffic violation records by a keyword
    and/or a date range. The date range can be a predefined range such as '1day' or '1week',
    or a custom range provided by the user. It then executes the query and returns the results.

    Args:
        request: The incoming HTTP request containing GET parameters for keyword search
                 and date range filtering.

    Returns:
        JsonResponse containing a list of traffic violations that match the search criteria.
    """

    # Initialise a BigQuery client
    client = bigquery.Client()

    # Fetch GET parameters from the request
    keyword: str = request.GET.get('keyword', '')
    time_range: str = request.GET.get('timeRange', 'all')
    from_date: str = request.GET.get('fromDate', '')
    to_date: str = request.GET.get('toDate', '')

    # Build WHERE clauses based on the provided time range
    where_clauses: List[str] = []
    if time_range != 'all':
        # Process the time range
        if time_range == 'custom':
            where_clauses.append(f"DATE(date) BETWEEN '{from_date}' AND '{to_date}'")
        else:
            # Get the current date
            current_date: datetime.date = datetime.datetime.now().date()

            # Calculate the date range
            if time_range == '1day':
                date_from = current_date - datetime.timedelta(days=1)
                where_clauses.append(f"DATE(date) = '{date_from}'")
            elif time_range == '1week':
                date_from = current_date - datetime.timedelta(weeks=1)
                where_clauses.append(f"DATE(date) >= '{date_from}'")
            elif time_range == '1month':
                date_from = current_date - datetime.timedelta(days=30)  # 假设每个月30天
                where_clauses.append(f"DATE(date) >= '{date_from}'")
            elif time_range == '6months':
                date_from = current_date - datetime.timedelta(days=30*6)  # 假设每个月30天
                where_clauses.append(f"DATE(date) >= '{date_from}'")
            elif time_range == '1year':
                date_from = current_date - datetime.timedelta(days=365)  # 假设每年365天
                where_clauses.append(f"DATE(date) >= '{date_from}'")
            elif time_range == 'custom':
                where_clauses.append(f"DATE(date) BETWEEN '{from_date}' AND '{to_date}'")

    # Process the keyword for filtering
    if keyword:
        where_clauses.append(
            f"(license_plate LIKE '%{keyword}%' OR "
            f"violation LIKE '%{keyword}%' OR "
            f"location LIKE '%{keyword}%')"
        )

    # Construct the complete SQL query
    where_clause: str = ' AND '.join(where_clauses) if where_clauses else 'TRUE'
    query: str = (
        f"SELECT license_plate, date, time, violation, status, location, traffic_violation_id "
        f"FROM `traffic_violation_db.reports_trafficviolation` "
        f"WHERE {where_clause}"
    )

    # Execute the query
    query_job = client.query(query)
    results = query_job.result()

    # Build the response data
    data: List[Dict[str, str]] = [
        {
            'lat': float(location.split(',')[0]),
            'lng': float(location.split(',')[1]),
            'title': f'{license_plate} - {violation}',
            'date': date,
            'time': time,
            'traffic_violation_id': traffic_violation_id
        }
        for row in results
        for license_plate, date, time, violation, status, location, traffic_violation_id in [(row.license_plate, row.date, row.time, row.violation, row.status, row.location, row.traffic_violation_id)]
    ]

    # Log the data for debugging purposes
    print(f"data: {data}")

    # Return the data as a JSON response
    return JsonResponse(data, safe=False)

def get_traffic_violation_markers(request: HttpRequest) -> JsonResponse:
    """
    Get traffic violation markers from BigQuery and return as JSON.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        JsonResponse: The JSON response containing traffic violation markers.
    """
    # Create a BigQuery client.
    client = bigquery.Client()
    
    # Define the SQL query to retrieve traffic violation markers.
    query = """
    SELECT traffic_violation_id, location
    FROM `traffic_violation_db.reports_trafficviolation`
    """
    
    # Execute the query.
    query_job = client.query(query)
    results = query_job.result()

    data = []
    for row in results:
        lat, lng = map(float, row.location.split(','))
        data.append({
            'lat': lat,
            'lng': lng,
            'traffic_violation_id': row.traffic_violation_id
        })

    return JsonResponse(data, safe=False)

def get_traffic_violation_details(request: HttpRequest, traffic_violation_id: int) -> JsonResponse:
    """
    Get details of a traffic violation from BigQuery and return as JSON.

    Args:
        request (HttpRequest): The incoming HTTP request.
        traffic_violation_id (int): The ID of the traffic violation to retrieve details for.

    Returns:
        JsonResponse: The JSON response containing traffic violation details.
    """
    # Create a BigQuery client.
    client = bigquery.Client()
    
    # Define the SQL query to retrieve traffic violation details based on ID.
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
    WHERE 
        v.traffic_violation_id = @violation_id
    """
    
    # Configure the query with a parameter for the traffic violation ID.
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("violation_id", "INT64", traffic_violation_id)
        ]
    )
    
    # Execute the query.
    query_job = client.query(query, job_config=job_config)
    result = query_job.result()

    # Process the query result.
    row = list(result)[0]
    lat, lng = map(float, row.location.split(','))

    data = {
        'lat': lat,
        'lng': lng,
        'title': f'{row.license_plate} - {row.violation}',
        'media': row.file if row.file else 'path/to/default/image.jpg'
    }

    return JsonResponse(data)

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
            "username": traffic_violation.username,
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