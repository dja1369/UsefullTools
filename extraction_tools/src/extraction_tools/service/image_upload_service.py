import asyncio
from datetime import date

from src.extraction_tools.client.ssh_client import SSHClient
from src.extraction_tools.dto.Vo import IssueTagResult, IssueCodeNTime, IssueLinkTagCode
from src.extraction_tools.infra.orm import ORM
from src.extraction_tools.util.directory_util import DirectoryUtil


class ImageUploadService:
    def __init__(self, directory_util: DirectoryUtil, ssh_client: SSHClient, db_client: ORM):
        self.directory_util = directory_util
        self.ssh_client = ssh_client
        self.db_client = db_client

    async def upload_all_sample_images(self, target_date: dict[str, list[date]], download_path: str, upload_path: str):
        img_group: dict[date, list[IssueTagResult]] = self.db_client.get_image_group_by_date(
            target_date,
            self.db_client.get_sample_data_by_created_at_range
        )
        await self._validate_sample_images(img_group, download_path, upload_path)

    async def _validate_sample_images(self, img_group: dict[date, list[IssueTagResult]], download_path: str, upload_path: str):
        coroutines = []

        for k, v in img_group.items():
            if not v:
                continue
            self.directory_util.make_directory_if_not_exists(download_path)
            for issue_tag_result in v:
                for position in "top", "side":
                    remote_path = f"{download_path}/{issue_tag_result.issue_code}/{position}/color.jpg"
                    local_path = (f"{upload_path}/{issue_tag_result.tag_code}_color"
                                  f"_{issue_tag_result.rotate}_{position}"
                                  f"_{issue_tag_result.issue_code}.jpg")
                    if self.ssh_client.is_exist(remote_path):
                        coroutines.append(self.ssh_client.download(remote_path, local_path))
        await asyncio.gather(*coroutines)
        print("Done")

    async def upload_all_package_images(self, target_date: dict[str, list[date]], download_path: str, upload_path: str):
        img_group: dict[date, list[IssueCodeNTime]] = self.db_client.get_image_group_by_date(
            target_date,
            self.db_client.get_package_data_by_created_at_range
        )
        await self._validate_package_images(img_group, download_path, upload_path)

    async def _validate_package_images(self, img_group: dict[date, list[IssueCodeNTime]], download_path: str, upload_path: str):
        coroutines = []

        for k, v in img_group.items():
            if not v:
                continue
            year, month, day = k.year, k.month, k.day
            self.directory_util.make_directory_if_not_exists(download_path)
            for obj in v:
                for position in "none", "none":
                    if self.ssh_client.is_exist(download_path):
                        coroutines.append(self.ssh_client.download(download_path, upload_path))

        results = await asyncio.gather(*coroutines)
        for result in results:
            if not result:
                print(f"Failed to download {result}")
                continue
        print("Done")
