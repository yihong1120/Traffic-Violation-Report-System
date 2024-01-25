#!/bin/sh
# gcp_entrypoint.sh

# 获取环境变量中的GCP项目ID
PROJECT_ID=$GCP_PROJECT

# 使用gcloud命令获取秘密并导出为环境变量
export SECRET_KEY=$(gcloud secrets versions access latest --secret="SECRET_KEY" --project="$PROJECT_ID")
export EMAIL_HOST_USER=$(gcloud secrets versions access latest --secret="EMAIL_HOST_USER" --project="$PROJECT_ID")
export DEFAULT_FROM_EMAIL=$(gcloud secrets versions access latest --secret="DEFAULT_FROM_EMAIL" --project="$PROJECT_ID")
export EMAIL_HOST_PASSWORD=$(gcloud secrets versions access latest --secret="EMAIL_HOST_PASSWORD" --project="$PROJECT_ID")
export DATABASE_NAME=$(gcloud secrets versions access latest --secret="DATABASE_NAME" --project="$PROJECT_ID")
export DATABASE_USER=$(gcloud secrets versions access latest --secret="DATABASE_USER" --project="$PROJECT_ID")
export DATABASE_PASSWORD=$(gcloud secrets versions access latest --secret="DATABASE_PASSWORD" --project="$PROJECT_ID")
export DATABASE_HOST=$(gcloud secrets versions access latest --secret="DATABASE_HOST" --project="$PROJECT_ID")
export DATABASE_PORT=$(gcloud secrets versions access latest --secret="DATABASE_PORT" --project="$PROJECT_ID")
export GOOGLE_MAPS_API_KEY=$(gcloud secrets versions access latest --secret="GOOGLE_MAPS_API_KEY" --project="$PROJECT_ID")
export GEMINI_API_KEY=$(gcloud secrets versions access latest --secret="GEMINI_API_KEY" --project="$PROJECT_ID")

# 启动Gunicorn服务
exec gunicorn -b :$PORT TrafficViolationReport.wsgi