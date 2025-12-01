from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob.aio import BlobServiceClient

from seedwork.application.object_storage import ObjectStorage


class AzureBlobStorage(ObjectStorage):
    """
    Azure Blob Storage implementation for object storage.

    Provides compatibility with Azure Blob Storage service.
    """

    def __init__(
        self,
        connection_string: str | None = None,
        account_name: str | None = None,
        account_key: str | None = None,
        container_name: str | None = None,
        public_url: str | None = None,
        default_bucket: str | None = None,
    ):
        self.container_name = container_name
        self.default_bucket = default_bucket
        self.public_url = public_url or f"https://{account_name}.blob.core.windows.net"

        if connection_string:
            self._client = BlobServiceClient.from_connection_string(connection_string)
        elif account_name and account_key:
            self._client = BlobServiceClient(
                account_url=f"https://{account_name}.blob.core.windows.net",
                credential=account_key,
            )
        else:
            raise ValueError(
                "Either connection_string or (account_name and account_key) must be provided"
            )

    async def upload_file(
        self,
        key: str,
        data: bytes,
        bucket: str | None = None,
        content_type: str | None = None,
    ) -> str:
        container_name = bucket or self.default_bucket or self.container_name
        if not container_name:
            raise ValueError(
                "Bucket must be provided or default_bucket/container_name must be set"
            )

        async with self._client:
            blob_client = self._client.get_blob_client(
                container=container_name, blob=key
            )

            content_settings = None
            if content_type:
                from azure.storage.blob import ContentSettings

                content_settings = ContentSettings(content_type=content_type)

            await blob_client.upload_blob(
                data, overwrite=True, content_settings=content_settings
            )

        return f"{self.public_url}/{container_name}/{key}"

    async def delete_file(self, key: str, bucket: str | None = None) -> None:
        container_name = bucket or self.default_bucket or self.container_name
        if not container_name:
            raise ValueError(
                "Bucket must be provided or default_bucket/container_name must be set"
            )

        async with self._client:
            blob_client = self._client.get_blob_client(
                container=container_name, blob=key
            )
            try:
                await blob_client.delete_blob()
            except ResourceNotFoundError:
                # Ignore if file doesn't exist
                pass

    async def get_file(self, key: str, bucket: str | None = None) -> bytes:
        container_name = bucket or self.default_bucket or self.container_name
        if not container_name:
            raise ValueError(
                "Bucket must be provided or default_bucket/container_name must be set"
            )

        async with self._client:
            blob_client = self._client.get_blob_client(
                container=container_name, blob=key
            )
            stream = await blob_client.download_blob()
            return await stream.readall()

    async def file_exists(self, key: str, bucket: str | None = None) -> bool:
        container_name = bucket or self.default_bucket or self.container_name
        if not container_name:
            raise ValueError(
                "Bucket must be provided or default_bucket/container_name must be set"
            )

        async with self._client:
            blob_client = self._client.get_blob_client(
                container=container_name, blob=key
            )
            try:
                await blob_client.get_blob_properties()
                return True
            except ResourceNotFoundError:
                return False

    async def get_file_url(self, key: str, bucket: str | None = None) -> str:
        container_name = bucket or self.default_bucket or self.container_name
        if not container_name:
            raise ValueError(
                "Bucket must be provided or default_bucket/container_name must be set"
            )

        return f"{self.public_url}/{container_name}/{key}"

    async def ensure_container_exists(self, container: str) -> None:
        """
        Ensure a container exists, create it if it doesn't.
        """
        async with self._client:
            container_client = self._client.get_container_client(container)
            try:
                await container_client.get_container_properties()
            except ResourceNotFoundError:
                await container_client.create_container(public_access="blob")
