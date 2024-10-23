from typing import Sequence

from sqlalchemy import Row

from src.extraction_tools.client.ssh_client import SSHClient
from src.extraction_tools.infra.orm import ORM
from src.extraction_tools.infra.schema import Question, Option, QuestionData
from src.extraction_tools.util.directory_util import DirectoryUtil


class ImageExtractService:
    def __init__(self, db_client: ORM, directory_util: DirectoryUtil, ssh_client: SSHClient):
        self.db_client = db_client
        self.directory_util = directory_util
        self.ssh_client = ssh_client

    def extract_target_questions_and_option_images(self, target_question_seq: list[int], download_path: str, upload_path: str):
        for question_seq in target_question_seq:
            question_image: QuestionData.image_id = self.db_client.get_question_data_by_question_seq(question_seq)
            if not question_image:
                continue
            options: list[Option] = self.db_client.get_options_by_question_seq(question_seq)

    def extract_category_question_images(self, category: str, download_path: str, upload_path: str):
        pass

    def extract_all_option_images(self):
        pass

