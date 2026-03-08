import asyncio
from azure.storage.blob import BlobServiceClient, ContentSettings
from app.config import settings

_client: BlobServiceClient | None = None


def _get_client() -> BlobServiceClient | None:
    global _client
    if _client is None and settings.azure_storage_connection_string:
        _client = BlobServiceClient.from_connection_string(settings.azure_storage_connection_string)
    return _client


def get_blob_url(container: str, blob_name: str) -> str:
    return f"https://{settings.azure_storage_account_name}.blob.core.windows.net/{container}/{blob_name}"


async def upload_blob(container: str, blob_name: str, data: bytes, content_type: str) -> str:
    """Upload bytes to blob storage and return the public URL."""
    client = _get_client()
    if client is None:
        raise RuntimeError("Azure Blob Storage not configured (AZURE_STORAGE_CONNECTION_STRING missing)")
    blob_client = client.get_blob_client(container=container, blob=blob_name)
    cs = ContentSettings(content_type=content_type)
    await asyncio.to_thread(blob_client.upload_blob, data, overwrite=True, content_settings=cs)
    return get_blob_url(container, blob_name)


async def delete_blob(container: str, blob_name: str) -> None:
    """Delete a blob silently (no-op if missing or storage not configured)."""
    client = _get_client()
    if client is None:
        return
    try:
        blob_client = client.get_blob_client(container=container, blob=blob_name)
        await asyncio.to_thread(blob_client.delete_blob)
    except Exception:
        pass
