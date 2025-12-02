from dataclasses import dataclass
from uuid import uuid4

from seedwork.application.object_storage import ObjectStorage


@dataclass
class MessageService:
    object_storage: ObjectStorage

    async def upload_image(
        self, content_type: str, image_data: bytes
    ) -> tuple[str, str]:
        file_extension = self._get_extension_from_content_type(content_type)
        filename = f"message-images/{uuid4()}{file_extension}"

        url = await self.object_storage.upload_file(
            key=filename,
            data=image_data,
            content_type=content_type,
        )

        return filename, url

    async def upload_images(self, images: list[tuple[bytes, str]]) -> list[str]:
        keys = []
        for image_data, content_type in images:
            key, _ = await self.upload_image(content_type, image_data)
            keys.append(key)
        return keys

    async def get_image_url(self, key: str) -> str:
        """Get public URL for an image key."""
        return await self.object_storage.get_file_url(key=key)

    def _get_extension_from_content_type(self, content_type: str) -> str:
        extensions = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
        }
        return extensions.get(content_type, ".jpg")
