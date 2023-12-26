"""
This script is used to backup MySQL data to Google BigQuery. It first sets up the Django environment and imports the necessary Django models. 
Then, it sets up Google Cloud authentication and initializes the BigQuery client. It defines the BigQuery dataset and tables, 
prepares the BigQuery data by converting Django model instances to a format suitable for BigQuery, and finally inserts the data into BigQuery.
"""

import os
import django
from datetime import date, datetime, time
import uuid
from google.cloud import bigquery

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TrafficViolationReport.settings')

# Initialise Django
django.setup()

# Now you can import your Django models
from reports.models import TrafficViolation, MediaFile

# Set up Google Cloud authentication
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'static/pivotal-equinox-404812-6722b643b8f4.json'

# BigQuery client
bigquery_client = bigquery.Client()

# 定义BigQuery数据集和表
dataset_id = 'pivotal-equinox-404812.traffic_violation_db'
table_id_trafficviolation = f'{dataset_id}.reports_trafficviolation'
table_id_mediafile = f'{dataset_id}.reports_mediafile'

# 准备BigQuery数据
def prepare_bigquery_data(queryset, model_fields, related_field_mappings=None):
    if related_field_mappings is None:
        related_field_mappings = {}

    bigquery_data = []
    for instance in queryset:
        row_data = {}
        for field in model_fields:
            value = getattr(instance, field)
            # Convert date and datetime objects to string in ISO format
            if isinstance(value, (date, datetime)):
                value = value.isoformat()
            # Convert time objects to string in the format 'HH:MM:SS'
            elif isinstance(value, time):
                value = value.isoformat()
            # Convert UUID objects to string
            elif isinstance(value, uuid.UUID):
                value = str(value)
            # Convert Django model instances to their primary key value
            elif isinstance(value, django.db.models.Model):
                bigquery_field = related_field_mappings.get(field, field)
                value = str(value.pk)
            # Convert file objects to their string path
            elif isinstance(value, django.db.models.fields.files.FieldFile):
                value = value.name if value else None
            row_data[field] = value
        bigquery_data.append(row_data)
    return bigquery_data

# 将数据写入BigQuery
def insert_into_bigquery(table_id, data):
    table = bigquery_client.get_table(table_id)
    errors = bigquery_client.insert_rows_json(table, data)
    if errors:
        print('Errors:', errors)

# Define the mapping for related fields
related_field_mappings = {
    'traffic_violation': 'traffic_violation_id',  # Adjust the field name as per your BigQuery schema
}

# 同步TrafficViolation模型
traffic_violations = TrafficViolation.objects.all()
model_fields = [field.name for field in TrafficViolation._meta.fields]
bigquery_data = prepare_bigquery_data(traffic_violations, model_fields)
insert_into_bigquery(table_id_trafficviolation, bigquery_data)

# 同步MediaFile模型
media_files = MediaFile.objects.all()
model_fields = [field.name for field in MediaFile._meta.fields]
bigquery_data = prepare_bigquery_data(media_files, model_fields, related_field_mappings)
insert_into_bigquery(table_id_mediafile, bigquery_data)