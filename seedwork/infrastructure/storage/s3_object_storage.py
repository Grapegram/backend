from typing import Any

import aioboto3
from botocore.exceptions import ClientError

from seedwork.application.object_storage import ObjectStorage


class S3ObjectStorage(ObjectStorage):
    """
    S3-compatible object storage implementation.

    Supports AWS S3, MinIO, and other S3-compatible services.
    """

    def __init__(
        self,
        endpoint_url: str,
        access_key_id: str,
        secret_access_key: str,
        region_name: str,
        public_url: str,
        use_ssl: bool = False,
        default_bucket: str | None = None,
    ):
        self.endpoint_url = endpoint_url
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region_name = region_name
        self.public_url = public_url
        self.use_ssl = use_ssl
        self.default_bucket = default_bucket
        self._session = aioboto3.Session()

    def _get_client_config(self) -> dict[str, Any]:
        return {
            "endpoint_url": self.endpoint_url,
            "aws_access_key_id": self.access_key_id,
            "aws_secret_access_key": self.secret_access_key,
            "region_name": self.region_name,
            "use_ssl": self.use_ssl,
        }

    async def upload_file(
        self,
        key: str,
        data: bytes,
        bucket: str | None = None,
        content_type: str | None = None,
    ) -> str:
        bucket_name = bucket or self.default_bucket
        if not bucket_name:
            raise ValueError("Bucket must be provided or default_bucket must be set")

        await self.ensure_bucket_exists(bucket_name)
        async with self._session.client("s3", **self._get_client_config()) as s3:
            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type

            await s3.put_object(Bucket=bucket_name, Key=key, Body=data, **extra_args)

        return f"{self.public_url}/{bucket_name}/{key}"

    async def delete_file(self, key: str, bucket: str | None = None) -> None:
        bucket_name = bucket or self.default_bucket
        if not bucket_name:
            raise ValueError("Bucket must be provided or default_bucket must be set")

        async with self._session.client("s3", **self._get_client_config()) as s3:
            try:
                await s3.delete_object(Bucket=bucket_name, Key=key)
            except ClientError:
                # Ignore if file doesn't exist
                pass

    async def get_file(self, key: str, bucket: str | None = None) -> bytes:
        bucket_name = bucket or self.default_bucket
        if not bucket_name:
            raise ValueError("Bucket must be provided or default_bucket must be set")

        async with self._session.client("s3", **self._get_client_config()) as s3:
            response = await s3.get_object(Bucket=bucket_name, Key=key)
            async with response["Body"] as stream:
                return await stream.read()

    async def file_exists(self, key: str, bucket: str | None = None) -> bool:
        bucket_name = bucket or self.default_bucket
        if not bucket_name:
            raise ValueError("Bucket must be provided or default_bucket must be set")

        async with self._session.client("s3", **self._get_client_config()) as s3:
            try:
                await s3.head_object(Bucket=bucket_name, Key=key)
                return True
            except ClientError:
                return False

    async def get_file_url(self, key: str, bucket: str | None = None) -> str:
        bucket_name = bucket or self.default_bucket
        if not bucket_name:
            raise ValueError("Bucket must be provided or default_bucket must be set")

        return f"{self.public_url}/{bucket_name}/{key}"

    async def ensure_bucket_exists(self, bucket: str) -> None:
        """
        Ensure a bucket exists, create it if it doesn't.
        """
        async with self._session.client("s3", **self._get_client_config()) as s3:
            try:
                await s3.head_bucket(Bucket=bucket)
            except ClientError:
                await s3.create_bucket(Bucket=bucket)
                # Make bucket public for read access (MinIO)
                policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": "*"},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{bucket}/*"],
                        }
                    ],
                }
                import json

                await s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))
