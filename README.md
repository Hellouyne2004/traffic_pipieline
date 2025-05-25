# GOVAP Traffic Pipeline: Real-time Traffic Monitoring

A fully serverless data pipeline that crawls HERE traffic data for Go Vap, stores raw data in GCS, transforms it with Cloud Functions using Pandas, loads it into BigQuery, and visualizes it in Looker Studio. The pipeline is orchestrated by Cloud Workflows and monitored via Slack notifications.

## Table of Contents
- [Features](#features)
- [Architecture Diagram](#architecture-diagram)
- [Demo Dashboard](#demo-dashboard)
- [Schedule](#schedule)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Deployment (Manual)](#deployment-manual)
  - [1. Deploy crawl function](#1-deploy-crawl-function)
  - [2. Deploy transform function](#2-deploy-transform-function)
  - [3. Deploy Workflow](#3-deploy-workflow)
  - [4. Setup Scheduler](#4-setup-scheduler)
- [GitHub Actions (CI/CD)](#github-actions-cicd)

## Features
- ✅ Automated traffic data collection from HERE API for Go Vap
- ✅ GCS for raw data storage
- ✅ Cloud Function ETL with Pandas
- ✅ Cloud Workflows + Scheduler orchestration
- ✅ Slack notification after pipeline completes
- ✅ BigQuery as central warehouse
- ✅ Looker Studio dashboard
- ✅ CI/CD with GitHub Actions

## Architecture Diagram

## Demo Dashboard


## Schedule
- Runs every day (6 am and 18 pm) using **Cloud Scheduler**
- Executes `Cloud Workflow` which:
  1. Triggers traffic data crawling from HERE API
  2. Transforms and loads data to BigQuery
  3. Sends a Slack alert

## Tech Stack
| Component      | Tool                        |
|----------------|----------------------------|
| Crawl data     | Cloud Functions (Python)    |
| Raw storage    | GCS                        |
| Transform      | Cloud Function + Pandas     |
| Warehouse      | BigQuery                   |
| Orchestration  | Cloud Workflows            |
| Automation     | Cloud Scheduler            |
| CI/CD          | GitHub Actions             |
| Monitoring     | Slack Webhook              |
| Visualization  | Looker Studio              |

## Repository Structure
```
traffic-pipeline/
├── .gitignore                 
├── README.md                  
├── .github/
│   └── workflows/
│       └── deploy.yml          
├── cloud_functions/
│   ├── crawl_here_data/
│   │   ├── main.py             
│   │   └── requirements.txt         
│   └── transform_to_bq/
│       ├── main.py             
│       └── requirements.txt    
├── cloud_workflows/
│   └── workflow.yaml           
└── img/

```

## Deployment (Manual)

### 1. Deploy crawl function:
```bash
gcloud functions deploy fetch_and_upload_traffic_data \
  --runtime python310 \
  --region asia-southeast1 \
  --trigger-http \
  --entry-point fetch_and_upload_traffic_data \
  --source=cloud_functions/crawl_here_data \
  --set-env-vars HERE_API_KEY=xxx,GCS_BUCKET_NAME=traffic-pipeline-data \
  --allow-unauthenticated
```

### 2. Deploy transform function:
```bash
gcloud functions deploy transform_to_bq_entrypoint \
  --runtime python310 \
  --region asia-southeast1 \
  --trigger-http \
  --entry-point transform_to_bq_entrypoint \
  --source=cloud_functions/transform_to_bq \
  --set-env-vars BUCKET_NAME=traffic-pipeline-data,BQ_DATASET=traffic,BQ_TABLE=traffic_flow_data \
  --allow-unauthenticated
```

### 3. Deploy Workflow:
```bash
gcloud workflows deploy traffic_pipeline_workflow \
  --source=cloud_workflows/workflow.yaml \
  --location=asia-southeast1 \
  --set-env-vars SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
```

### 4. Setup Scheduler:
```bash
gcloud scheduler jobs create http traffic-pipeline-job \
  --schedule="0 6,18 * * *" \ 
  --uri="https://workflowexecutions.googleapis.com/v1/projects/PROJECT_ID/locations/asia-southeast1/workflows/stock_pipeline_workflow/executions" \
  --http-method=POST \
  --oauth-service-account-email=YOUR_SA_EMAIL \
  --location=asia-southeast1
  --time-zone="Asia/Bangkok"
```

## GitHub Actions (CI/CD)
- Auto deploy Cloud Functions & Workflows when folders are modified.
- Uses `google-github-actions/auth` and `gcloud` CLI
- Secrets required:
  - `GCP_SA_KEY`
  - `HERE_API_KEY`
  - `SLACK_WEBHOOK_URL`

  
