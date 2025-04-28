import os
from azure.storage.blob import BlobServiceClient

def get_blob_service_client():
    # Use the new unified storage connection string
    connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING")
    return BlobServiceClient.from_connection_string(connection_string)

def upload_image(file, container_name, blob_name):
    blob_service_client = get_blob_service_client()
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
    except Exception:
        pass  # Container may already exist
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(file, overwrite=True)
    return blob_client.url
