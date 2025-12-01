from dataclasses import dataclass
from uuid import uuid4

from seedwork.application.object_storage import ObjectStorage

from ...domain.aggregates import User


@dataclass
class UserService:
    object_storage: ObjectStorage

    async def upload_avatar(
        self, user: User, content_type: str, image_data: bytes
    ) -> tuple[str, str]:
        file_extension = self._get_extension_from_content_type(content_type)
        filename = f"user-avatars/{user.id}/{uuid4()}{file_extension}"

        url = await self.object_storage.upload_file(
            key=filename,
            data=image_data,
            content_type=content_type,
        )

        return filename, url

    async def get_avatar_url(self, user: User) -> str | None:
        if not user.avatar:
            return None
        return await self.object_storage.get_file_url(key=user.avatar)

    def _get_extension_from_content_type(self, content_type: str) -> str:
        extensions = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
        }
        return extensions.get(content_type, ".jpg")
