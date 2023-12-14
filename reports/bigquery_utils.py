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
    query = """
        SELECT * 
        FROM `pivotal-equinox-404812.traffic_violation_db.reports_trafficviolation` 
        WHERE username = @username
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("username", "STRING", username)
        ]
    )
    query_job = client.query(query, job_config=job_config)
    return [dict(row) for row in query_job.result()]

def get_media_records(record_id: int) -> List[Dict]:
    """
    Retrieve media records for a specific traffic violation record from BigQuery.
    """
    client = bigquery.Client()
    media_query = """
        SELECT * 
        FROM `pivotal-equinox-404812.traffic_violation_db.reports_mediafile` 
        WHERE traffic_violation_id = @record_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("record_id", "INT64", record_id)
        ]
    )
    media_query_job = client.query(media_query, job_config=job_config)
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

    #Convert string to integer
    selected_record_id_int = int(selected_record_id)

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
        bigquery.ScalarQueryParameter("traffic_violation_id", "INT64", selected_record_id_int),
    ]

    job_config = bigquery.QueryJobConfig(query_parameters=params)

    # Execute the update
    client.query(update_query, job_config=job_config).result()

def update_media_files(selected_record_id: str, new_media_files: List[InMemoryUploadedFile], removed_media: List[str]):
    """
    Updates media files associated with a specific traffic violation record in BigQuery.

    This function first deletes any existing media files linked to the traffic violation record 
    and then inserts the information for the new media files.

    Args:
        selected_record_id (str): The ID of the traffic violation record.
        new_media_files (List[InMemoryUploadedFile]): A list of new media files to be associated with the record.
        removed_media (List[str]): A list of URLs of media files to be removed.
    """
    client = bigquery.Client()

    # Converting the selected record ID to an integer for BigQuery compatibility
    selected_record_id_int = int(selected_record_id)

    # Processing the deletion of existing media files
    for media_url in removed_media:
        if media_url:
            # Constructing the delete query for BigQuery
            delete_query = """
                DELETE FROM `pivotal-equinox-404812.traffic_violation_db.reports_mediafile`
                WHERE file = @file
            """
            delete_params = [
                bigquery.ScalarQueryParameter("file", "STRING", media_url),
            ]
            delete_job_config = bigquery.QueryJobConfig(query_parameters=delete_params)
            # Executing the delete query
            client.query(delete_query, delete_job_config).result()

    # Processing the addition of new media files
    for filename in new_media_files:
        # Constructing the insert query for BigQuery
        insert_query = """
            INSERT INTO `pivotal-equinox-404812.traffic_violation_db.reports_mediafile` (file, traffic_violation_id)
            VALUES (@file, @traffic_violation_id)
        """
        insert_params = [
            bigquery.ScalarQueryParameter("file", "STRING", filename),
            bigquery.ScalarQueryParameter("traffic_violation_id", "INT64", selected_record_id_int),
        ]
        insert_job_config = bigquery.QueryJobConfig(query_parameters=insert_params)
        # Executing the insert query
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
    keyword: str = request.GET.get('keyword', '')  # Get the 'keyword' parameter from the request
    time_range: str = request.GET.get('timeRange', 'all')  # Get the 'timeRange' parameter with a default value of 'all'
    from_date: str = request.GET.get('fromDate', '')  # Get the 'fromDate' parameter from the request
    to_date: str = request.GET.get('toDate', '')  # Get the 'toDate' parameter from the request

    # Define the base SQL query
    query = """
        SELECT license_plate, date, time, violation, status, location, traffic_violation_id
        FROM `traffic_violation_db.reports_trafficviolation`
        WHERE TRUE
    """

    # Initialise a list to hold query parameters
    params = []

    # Check if a specific time range is selected
    if time_range != 'all':
        current_date: datetime.date = datetime.datetime.now().date()
        date_from = None
        
        # Calculate the date range based on the selected time range
        if time_range == '1day':
            date_from = current_date - datetime.timedelta(days=1)
        elif time_range == '1week':
            date_from = current_date - datetime.timedelta(weeks=1)
        elif time_range == '1month':
            date_from = current_date - datetime.timedelta(days=30)
        elif time_range == '6months':
            date_from = current_date - datetime.timedelta(days=30*6)
        elif time_range == '1year':
            date_from = current_date - datetime.timedelta(days=365)
        elif time_range == 'custom':
            date_from = from_date
            to_date = to_date

        # Add date filters to the query
        if time_range != 'custom':
            query += " AND DATE(date) >= @date_from"
            params.append(bigquery.ScalarQueryParameter('date_from', 'DATE', date_from))
        else:
            query += " AND DATE(date) BETWEEN @from_date AND @to_date"
            params.append(bigquery.ScalarQueryParameter('from_date', 'DATE', from_date))
            params.append(bigquery.ScalarQueryParameter('to_date', 'DATE', to_date))

    # Check if a keyword is provided for filtering
    if keyword:
        query += """
            AND (license_plate LIKE CONCAT('%', @keyword, '%')
            OR violation LIKE CONCAT('%', @keyword, '%')
            OR location LIKE CONCAT('%', @keyword, '%'))
        """
        params.append(bigquery.ScalarQueryParameter('keyword', 'STRING', keyword))

    # Configure the BigQuery job
    job_config = bigquery.QueryJobConfig(query_parameters=params)
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    # Create a list of dictionaries containing query results
    data = [{
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
        ARRAY_AGG(m.file) AS media_files
    FROM 
        `traffic_violation_db.reports_trafficviolation` v
    LEFT JOIN 
        `traffic_violation_db.reports_mediafile` m ON v.traffic_violation_id = m.traffic_violation_id
    WHERE 
        v.traffic_violation_id = @violation_id
    GROUP BY v.license_plate, v.date, v.time, v.violation, v.status, v.location, v.officer, v.traffic_violation_id
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

    # Process query results
    row = list(result)[0]
    lat, lng = map(float, row.location.split(','))
    media_files = row.media_files if row.media_files else ['path/to/default/image.jpg']

    data = {
        'lat': lat,
        'lng': lng,
        'title': f'{row.license_plate} - {row.violation}',
        'media': media_files,
        'license_plate': row.license_plate,
        'date': row.date,
        'time': row.time,
        'violation': row.violation,
        'status': row.status,
        'officer': row.officer,
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