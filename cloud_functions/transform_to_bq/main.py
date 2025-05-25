import os
import json
import pandas as pd
from google.cloud import storage, bigquery

def transform_to_bq_entrypoint(request):
    bucket_name = os.environ.get("BUCKET_NAME")
    dataset_id = os.environ.get("BQ_DATASET")
    table_id = os.environ.get("BQ_TABLE")

    storage_client = storage.Client()
    bq_client = bigquery.Client()
    bucket = storage_client.bucket(bucket_name)

    messages = []

    # Đọc file JSON mới nhất trong thư mục raw/
    try:
        print(" Tìm file dữ liệu giao thông mới nhất trong GCS...")
        blobs = list(storage_client.list_blobs(bucket_name, prefix="raw/"))
        blobs = [b for b in blobs if b.name.endswith(".json")]
        if not blobs:
            messages.append("Không tìm thấy file dữ liệu giao thông.")
            return "\n".join(messages), 404

        latest_blob = max(blobs, key=lambda b: b.updated)
        print(f"Đọc file: {latest_blob.name}")
        traffic_json = json.loads(latest_blob.download_as_text())

        # Transform dữ liệu
        rows = []
        source_updated = traffic_json.get("sourceUpdated")
        for item in traffic_json.get("results", []):
            location = item.get("location", {})
            current_flow = item.get("currentFlow", {})
            row = {
                "source_updated": source_updated,
                "description": location.get("description"),
                "location_length": location.get("length"),
                "speed": current_flow.get("speed"),
                "speed_uncapped": current_flow.get("speedUncapped"),
                "free_flow": current_flow.get("freeFlow"),
                "jam_factor": current_flow.get("jamFactor"),
                "confidence": current_flow.get("confidence"),
                "traversability": current_flow.get("traversability"),
            }
            rows.append(row)
        df = pd.DataFrame(rows)
        if not df.empty:
            df["source_updated"] = pd.to_datetime(df["source_updated"], errors="coerce")
            
        # Ghi vào BigQuery
        bq_client.load_table_from_dataframe(df, f"{dataset_id}.{table_id}").result()
        messages.append(f"Uploaded {len(df)} rows to {dataset_id}.{table_id}.")
    except Exception as e:
        messages.append(f"Error: {str(e)}")

    print("Transformation Summary:")
    for msg in messages:
        print(msg)

    return "\n".join(messages), 200 if any("Uploaded" in msg for msg in messages) else 500