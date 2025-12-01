from typing import Protocol


class ObjectStorage(Protocol):
    """
    Protocol for object storage operations (S3-compatible).

    This provides an abstraction over S3-compatible storage services
    like AWS S3, MinIO, Azure Blob Storage, etc.

    This is a shared infrastructure concern that can be used across
    different bounded contexts.
    """

    async def upload_file(
        self,
        key: str,
        data: bytes,
        bucket: str | None = None,
        content_type: str | None = None,
    ) -> str:
        """
        Upload a file to object storage.

        Args:
            bucket: The bucket/container name (uses default_bucket if None)
            key: The object key (path)
            data: The file content as bytes
            content_type: Optional MIME type of the file

        Returns:
            The public URL of the uploaded file
        """
        ...

    async def delete_file(self, key: str, bucket: str | None = None) -> None:
        """
        Delete a file from object storage.

        Args:
            bucket: The bucket/container name (uses default_bucket if None)
            key: The object key (path)
        """
        ...

    async def get_file(self, key: str, bucket: str | None = None) -> bytes:
        """
        Get file content from object storage.

        Args:
            bucket: The bucket/container name (uses default_bucket if None)
            key: The object key (path)

        Returns:
            The file content as bytes
        """
        ...

    async def file_exists(self, key: str, bucket: str | None = None) -> bool:
        """
        Check if a file exists in object storage.

        Args:
            bucket: The bucket/container name (uses default_bucket if None)
            key: The object key (path)

        Returns:
            True if the file exists, False otherwise
        """
        ...

    async def get_file_url(self, key: str, bucket: str | None = None) -> str:
        """
        Get the public URL for a file.

        Args:
            bucket: The bucket/container name (uses default_bucket if None)
            key: The object key (path)

        Returns:
            The public URL of the file
        """
        ...
