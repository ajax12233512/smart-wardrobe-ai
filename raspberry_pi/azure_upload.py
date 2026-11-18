
import os
import uuid
from pathlib import Path
from datetime import datetime, timezone

from dotenv import load_dotenv
from azure.storage.blob import (
    BlobServiceClient,
    ContentSettings,
)
from azure.data.tables import TableServiceClient

load_dotenv()

CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING"
)

CONTAINER_NAME = "clothing-images"
TABLE_NAME = "ClothingReadings"


def upload_clothing_result(
    image_path,
    celsius,
    fahrenheit,
    ai_result
):
    """Upload photo and analysis to Azure Storage."""

    if not CONNECTION_STRING:
        raise RuntimeError(
            "Azure connection string is missing."
        )

    image_path = Path(image_path)

    if not image_path.is_file():
        raise FileNotFoundError(image_path)

    # Unique identifier for every clothing scan
    scan_id = uuid.uuid4().hex

    timestamp = datetime.now(timezone.utc)

    blob_name = f"{scan_id}.jpg"

    # 1. Upload photograph
    blob_service = BlobServiceClient.from_connection_string(
        CONNECTION_STRING
    )

    blob_client = blob_service.get_blob_client(
        container=CONTAINER_NAME,
        blob=blob_name
    )

    print("[AZURE] Uploading photograph...")

    with image_path.open("rb") as photo:
        blob_client.upload_blob(
            photo,
            overwrite=False,
            content_settings=ContentSettings(
                content_type="image/jpeg"
            )
        )

    print("[AZURE] Photograph uploaded!")

    # 2. Upload analysis and sensor data
    table_service = TableServiceClient.from_connection_string(
        CONNECTION_STRING
    )

    table_client = table_service.get_table_client(
        TABLE_NAME
    )

    entity = {
        "PartitionKey": "ClothingScans",
        "RowKey": scan_id,
        "TimestampUTC": timestamp.isoformat(),
        "Device": "RaspberryPi5",
        "TemperatureC": float(celsius),
        "TemperatureF": float(fahrenheit),
        "AIResult": str(ai_result),
        "ImageBlobName": blob_name,
        "ImageURL": blob_client.url,
    }

    print("[AZURE] Saving analysis...")

    table_client.create_entity(entity=entity)

    print("[AZURE] Analysis saved!")

    return {
        "scan_id": scan_id,
        "image_url": blob_client.url,
        "timestamp": timestamp.isoformat()
    }
