from django.http import JsonResponse
from google.cloud import bigquery

def get_traffic_violations(request):
    client = bigquery.Client()
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
    query_job = client.query(query)

    results = query_job.result()

    data = []
    for row in results:
        lat, lng = map(float, row.location.split(','))
        data.append({
            'lat': lat,
            'lng': lng,
            'title': f'{row.license_plate} - {row.violation}',
            'media': row.file if row.file else 'path/to/default/image.jpg'
        })

    # return data
    return JsonResponse(data, safe=False) 

def save_to_bigquery(traffic_violation, media_files):
    client = bigquery.Client()

    # 指定 dataset ID 和 table ID
    project_id = "pivotal-equinox-404812"
    dataset_id = "traffic_violation_db"
    table_id_violation = "reports_trafficviolation"
    table_id_media = "reports_mediafile"

    # 准备要插入的违章数据
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

    # 插入违章数据
    dataset_ref = client.dataset(dataset_id, project=project_id)
    table_ref_violation = dataset_ref.table(table_id_violation)
    table_violation = client.get_table(table_ref_violation)
    client.insert_rows_json(table_violation, rows_to_insert_violation)

    # 准备要插入的媒体文件数据
    rows_to_insert_media = [
        {
            "traffic_violation_id": traffic_violation.id,
            "file": media_file.file.name,
            # 其他需要的字段
        }
        for media_file in media_files
    ]

    # 插入媒体文件数据
    table_ref_media = dataset_ref.table(table_id_media)
    table_media = client.get_table(table_ref_media)
    client.insert_rows_json(table_media, rows_to_insert_media)