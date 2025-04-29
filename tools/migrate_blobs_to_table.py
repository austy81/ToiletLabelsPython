import os
import re
import sys
# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables from .env or secrets.env
try:
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'secrets.env')
    if not os.path.exists(dotenv_path):
        dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path)
except ImportError:
    print("[ERROR] python-dotenv is not installed. Please run: pip install python-dotenv")
    exit(1)

from azure.storage.blob import BlobServiceClient
from gallery.services.azure_table import AzureTableManager

def get_blob_metadata(container_client, blob_name):
    blob = container_client.get_blob_client(blob_name)
    props = blob.get_blob_properties()
    return props.metadata

def main():
    AZURE_CONNECTION_STRING = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    CONTAINER_NAME = "toiletlabels-backup"
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    blobs = list(container_client.list_blobs())

    # Group blobs by prefix (e.g., '1', '2', ...)
    pairs = {}
    for blob in blobs:
        match = re.match(r"([0-9]+)([fm])\.(jpg|jpeg|png)$", blob.name, re.IGNORECASE)
        if match:
            number, gender, ext = match.groups()
            if number not in pairs:
                pairs[number] = {}
            pairs[number][gender] = blob

    table_manager = AzureTableManager()
    dest_container_name = "toiletlabels"
    dest_container_client = blob_service_client.get_container_client(dest_container_name)
    try:
        dest_container_client.create_container()
    except Exception:
        pass  # Already exists

    for number, pair in pairs.items():
        men_blob = pair.get("m")
        women_blob = pair.get("f")
        if not men_blob or not women_blob:
            print(f"Skipping pair {number}: missing m or f image.")
            continue

        # Copy blobs only if not already present in destination
        for blob_obj in [men_blob, women_blob]:
            dest_blob_client = dest_container_client.get_blob_client(blob_obj.name)
            if not dest_blob_client.exists():
                src_blob_client = container_client.get_blob_client(blob_obj.name)
                src_url = src_blob_client.url
                dest_blob_client.start_copy_from_url(src_url)
                print(f"Copied {blob_obj.name} to {dest_container_name}")
            else:
                print(f"{blob_obj.name} already exists in {dest_container_name}, skipping copy.")

        # Read metadata (assuming 'place' is present in both, or pick one)
        men_metadata = men_blob.metadata if hasattr(men_blob, "metadata") and men_blob.metadata else get_blob_metadata(container_client, men_blob.name)
        place = men_metadata.get("place", "Unknown")

        # Insert into Table Storage
        table_manager.upsert_label(
            label_id=number,
            place=place,
            description="",
            men_image_url=men_blob.name,
            women_image_url=women_blob.name,
            num_voters=0,
            avg_vote=0,
        )
        print(f"Migrated pair {number}: {men_blob.name}, {women_blob.name}, place={place}")

if __name__ == "__main__":
    main()
