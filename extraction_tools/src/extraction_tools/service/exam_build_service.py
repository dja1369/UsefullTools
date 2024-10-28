from typing import Sequence

from sqlmodel import Session

from src.extraction_tools.dto.Vo import QuestionVo, QuestionDataVo, LanguageVo, DifficultyVo, OptionVo, ExamDataVo
from src.extraction_tools.infra.orm import ORM
from src.extraction_tools.infra.schema import Question, Option


class ExamBuildService:
    def __init__(self, db_client: ORM):
        self.db_client = db_client

    def correct_answer_mapper(self, answer: int, options: Sequence[Option]):
        for option in options:
            if option.seq == answer:
                return OptionVo(
                    include_text=LanguageVo(
                        name=option.included_text.kr if option.included_text else None
                    ) or None,
                    option_data=[
                        QuestionDataVo(
                            image_id=option_data.image_id,
                            filter_name=option_data.filter,
                            is_main_image=option_data.is_main_image
                        )
                        for option_data in option.option_data
                    ] if option.option_data else []
                )
    def option_mapper(self, options: Sequence[Option]):
        if not options:
            return []
        return [
            OptionVo(
                include_text=LanguageVo(
                    name=option.included_text.kr if option.included_text else None
                ),
                option_data=[
                    QuestionDataVo(
                        image_id=option_data.image_id,
                        filter_name=option_data.filter_name,
                        is_main_image=option_data.is_main_image
                    )
                    for option_data in option.option_data
                ] if option.option_data else []
            )
            for option in options
        ]


    def extract_exam_data(self):
        result = []
        with Session(self.db_client._engine) as session:
            questions: Sequence[Question] = self.db_client.get_all_question_by_type(session)
            for obj in questions:
                result.append(
                    QuestionVo(
                        title=LanguageVo(
                            name=obj.title.kr if obj.title else None
                        ),
                        category=obj.category,
                        template=obj.template,
                        difficulty=DifficultyVo(
                            name=obj.difficulty.name
                        ),
                        correct_answer=self.correct_answer_mapper(obj.correct_answer_seq, obj.options),
                        solution=LanguageVo(
                            name=obj.solution.kr
                        ),
                        question_data=[
                            QuestionDataVo(
                                image_id=question_data.image_id,
                                filter_name=question_data.filter,
                                is_main_image=question_data.is_main_image
                            )
                            for question_data in obj.questions_data
                        ] if obj.questions_data else [],
                        options=self.option_mapper(obj.options)
                    )
                )
        return ExamDataVo(questions=result)

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
