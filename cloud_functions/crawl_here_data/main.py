import os
import json
import requests
from datetime import datetime
from google.cloud import storage

# === Lấy biến môi trường ===
API_KEY = os.environ["HERE_API_KEY"]
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
GCS_PREFIX = os.environ.get("GCS_PREFIX", "raw")

BBOX_POINTS = [
    (10.820, 106.66),   # (latitude, longitude)
    (10.838, 106.68),
]

min_lat = min(BBOX_POINTS[0][0], BBOX_POINTS[1][0])
max_lat = max(BBOX_POINTS[0][0], BBOX_POINTS[1][0])
min_lon = min(BBOX_POINTS[0][1], BBOX_POINTS[1][1])
max_lon = max(BBOX_POINTS[0][1], BBOX_POINTS[1][1])

BBOX_PARAM = f"bbox:{min_lon},{min_lat},{max_lon},{max_lat}"

def get_traffic_flow_data(api_key: str) -> dict:
    url = "https://data.traffic.hereapi.com/v7/flow"
    params = {
        "locationReferencing": "shape",
        "in": BBOX_PARAM,
        "apiKey": api_key
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def upload_to_gcs(bucket_name: str, content: dict, prefix: str = "raw") -> str:
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{prefix}/govap_traffic_raw_{timestamp}.json"
    blob = bucket.blob(filename)

    blob.upload_from_string(json.dumps(content, indent=2), content_type="application/json")
    print(f"✅ Uploaded to GCS: gs://{bucket_name}/{filename}")
    return filename

def fetch_and_upload_traffic_data(request):
    try:
        print("🚦 Fetching traffic data for Gò Vấp...")
        traffic_data = get_traffic_flow_data(API_KEY)

        print("☁️ Uploading to GCS...")
        filename = upload_to_gcs(GCS_BUCKET_NAME, traffic_data, GCS_PREFIX)

        return (f"✅ Successfully uploaded to: gs://{GCS_BUCKET_NAME}/{filename}", 200)

    except Exception as e:
        print(f"❌ Error: {e}")
        return (f"❌ Error: {str(e)}", 500)

