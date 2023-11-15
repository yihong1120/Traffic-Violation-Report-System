from django.http import JsonResponse
from google.cloud import bigquery

def get_traffic_violations(request):
    client = bigquery.Client()
    query = """
    SELECT license_plate, date, time, violation, status, location, officer
    FROM traffic_violation_db.reports_trafficviolation
    """
    query_job = client.query(query)
    results = query_job.result()

    data = []
    for row in results:
        lat, lng = map(float, row.location.split(','))
        data.append({
            'lat': lat,
            'lng': lng,
            'title': f'{row.license_plate} - {row.violation}'
        })
    
    return JsonResponse(data, safe=False) 

def save_to_bigquery(traffic_violation):
    client = bigquery.Client()

    # 指定你的 dataset ID 和 table ID
    project_id = "pivotal-equinox-404812"
    dataset_id = "traffic_violation_db"
    table_id = "reports_trafficviolation"

    dataset_ref = client.dataset(dataset_id, project=project_id)
    table_ref = dataset_ref.table(table_id)

    table = client.get_table(table_ref)  # API 请求

    rows_to_insert = [
        {
            "license_plate": traffic_violation.license_plate,
            "date": traffic_violation.date.strftime("%Y-%m-%d"),
            "time": traffic_violation.time.strftime("%H:%M:%S"),
            "violation": traffic_violation.violation,
            "status": traffic_violation.status,
            "location": traffic_violation.location,
            "officer": traffic_violation.officer.username if traffic_violation.officer else None,
        },
        # 可以添加更多的行
    ]

    errors = client.insert_rows_json(table, rows_to_insert)

    if errors != []:
        print("Errors occurred:", errors)
    else:
        print("New rows have been added.")