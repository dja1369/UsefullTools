from typing import Sequence

from sqlmodel import Session

from src.extraction_tools.infra.orm import ORM
from src.extraction_tools.infra.schema import Question




class ExamBuildService:
    def __init__(self, db_client: ORM):
        self.db_client = db_client


    def extract_exam_data(self):
        with Session(self.db_client._engine) as session:
            question_data: Sequence[Question] = self.db_client.get_all_question_by_type(session)
        # save to Json File
        with open("exam_data.json", "w") as f:
            for data in question_data:
                f.write(data.model_dump_json())
        print("Done")



    def make_mock_exam(self):
        # 모의고사 생성
        """
        501680
        501681
        501682
        501683
        501684
        501685
        501686
        501687
        501688
        501689
        501690
        501691
        501692
        501693
        501694
        501698
        501699
        501700
        501701
        501702
        convert to list = (501680, 501681, 501682)
        """
        pass