import asyncio
from typing import Sequence, Coroutine

from src.extraction_tools.client.ssh_client import SSHClient
from src.extraction_tools.infra.orm import ORM
from src.extraction_tools.infra.schema import Option, QuestionData
from src.extraction_tools.util.directory_util import DirectoryUtil


class ImageExtractService:
    def __init__(self, db_client: ORM, directory_util: DirectoryUtil, ssh_client: SSHClient):
        self.db_client = db_client
        self.directory_util = directory_util
        self.ssh_client = ssh_client

    def extract_target_questions_and_option_images(self, target_question_seq: list[int], download_path: str,
                                                   upload_path: str):
        coroutines: list[Coroutine] = []
        for question_seq in target_question_seq:
            questions_image: Sequence[QuestionData.image_id] = self.db_client.get_question_data_img_id_by_question_seq(
                question_seq)
            if not questions_image:
                continue
            options_image: Sequence[Option] = self.db_client.get_all_option_data_img_id_by_question_seq(question_seq)
            if not options_image:
                continue
            for question_image in questions_image:
                coroutines.append(
                    self.ssh_client.folder_download(
                    remote_path=f"{download_path}",
                    local_path=f"{upload_path}",
                    img_id=question_image )
                )
            for option_image in options_image:
                coroutines.append(
                    self.ssh_client.folder_download(
                    remote_path=f"{download_path}",
                    local_path=f"{upload_path}",
                    img_id=option_image.image_id )
                )
        asyncio.gather(*coroutines)

