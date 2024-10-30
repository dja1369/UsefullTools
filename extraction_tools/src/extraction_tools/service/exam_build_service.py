from datetime import datetime
from typing import Sequence

from sqlmodel import Session

from extraction_tools.dto.Vo import ExamPaperVo
from src.extraction_tools.dto.Vo import QuestionVo, QuestionDataVo, LanguageVo, DifficultyVo, OptionVo, ExamDataVo
from src.extraction_tools.infra.orm import ORM
from src.extraction_tools.infra.schema import Question, Option, Language, QuestionData, OptionData, CategoryEnum, \
    DifficultyEnum


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
                    option_data=QuestionDataVo(
                        image_id=option.option_data.image_id,
                        filter_name=option.option_data.filter,
                        is_main_image=False
                    ) if option.option_data else None
                )

    def option_mapper(self, options: Sequence[Option]):
        if not options:
            return []
        return [
            OptionVo(
                include_text=LanguageVo(
                    name=option.included_text.kr if option.included_text else None
                ),
                option_data=QuestionDataVo(
                    image_id=option.option_data.image_id,
                    filter_name=option.option_data.filter,
                    is_main_image=False
                ) if option.option_data else None
            )
            for option in options
        ]

    def question_data_mapper(self, question_data):
        result = []
        if not question_data:
            return []
        for data in question_data:
            result.append(
                QuestionDataVo(
                    image_id=data.image_id,
                    filter_name=data.filter,
                    is_main_image=data.is_main_image
                )
            )
        return result

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
                        question_data=self.question_data_mapper(obj.questions_data),
                        options=self.option_mapper(obj.options)
                    )
                )
        return ExamDataVo(questions=result)

    def make_question_data(self, session, question_seq, question_data: list[QuestionDataVo]):
        for data in question_data:
            q_d = QuestionData(
                question_seq=question_seq,
                image_id=data.image_id,
                filter=data.filter_name,
                is_main_image=data.is_main_image,
                created_at=datetime.now()
            )
            session.add(q_d)
        session.commit()


    def make_option(self, session, question_seq: int, correct_answer: OptionVo, options: list[OptionVo]):
        result = None
        for option in options:
            included_text = None
            if option.include_text.name:
                included_text = Language(kr=option.include_text.name,
                                         en='translation do not exist',
                                         created_at=datetime.now()
                                         ) if option.include_text else None
                session.add(included_text)
                session.flush()

            option_obj = Option(
                question_seq=question_seq,
                included_text=included_text,
                created_at=datetime.now()
            )
            session.add(option_obj)
            session.flush()
            option_data = None
            if option.option_data:
                option_data = OptionData(
                    option_seq=option_obj.seq,
                    image_id=option.option_data.image_id,
                    filter=option.option_data.filter_name,
                    created_at=datetime.now()
                )
                session.add(option_data)
                session.flush()
            if correct_answer.include_text.name == option.include_text.name:
                if not option_data:
                    result = option_obj.seq
                else:
                    if correct_answer.option_data.image_id == option_data.image_id:
                        result = option_obj.seq
        return result

    def merge_exam_data(self, exam_data: ExamDataVo):
        # 시험 데이터 병합
        with Session(self.db_client._engine) as session:
            for data in exam_data.questions:
                title = None
                if data.title.name:
                    title = Language(kr=data.title.name,
                                     en='translation do not exist',
                                     created_at=datetime.now()
                                     )
                    session.add(title)
                    session.flush()
                solution = Language(kr=data.solution.name,
                                    en='translation do not exist',
                                    created_at=datetime.now()
                                    ) if data.solution else None
                session.add(solution)
                session.flush()

                difficulty = self.db_client.get_difficulty_by_name(session, data.difficulty.name)
                question = Question(
                    title=title,
                    category=data.category,
                    template=data.template,
                    difficulty=difficulty,
                    solution=solution,
                    correct_answer_seq=1,
                    created_at=datetime.now()
                )
                session.add(question)
                session.flush()
                if data.question_data:
                    self.make_question_data(session, question.seq, data.question_data)
                correct_answer = self.make_option(session, question.seq, data.correct_answer, data.options)
                question.correct_answer_seq = correct_answer
                session.add(question)
                session.flush()
            # raise Exception("just Test")
            session.commit()

    def clean_exam_data(self):
        pass
        # with Session(self.db_client._engine) as session:
        #     q = select(Question).where(Question.created_at > "2024-10-28 00:00:00")
        #     result = session.exec(q).scalars().all()
        #     for obj in result:
        #         session.delete(obj)
        #     session.commit()


    def update_exam_paper(self, exam_category: ExamPaperVo, obj: Question):
        category: ExamPaperVo.QuestionPaperVo = exam_category.__dict__[obj.category.name]
        match obj.difficulty_seq:
            case 1:
                category.high_count += 1
            case 2:
                category.middle_count += 1
            case 3:
                category.low_count += 1
        category.question.append(obj)

    def make_mock_exam(self):
        # 모의고사 생성
        """
        origin 501680 = update: 502733,
        origin 501681 = update: 502734,
        origin 501682 = update: 502735,
        origin 501683 = update: 502736,
        origin 501684 = update: 502737,
        origin 501685 = update: 502738,
        origin 501686 = update: 502739,
        origin 501687 = update: 502740,
        origin 501688 = update: 502741,
        origin 501689 = update: 502742,
        origin 501690 = update: 502743,
        origin 501691 = update: 502744,
        origin 501692 = update: 502745,
        origin 501693 = update: 502746,
        origin 501694 = update: 502747,
        origin 501698 = update: 502751,
        origin 501699 = update: 502752,
        origin 501700 = update: 502753,
        origin 501701 = update: 502754,
        origin 501702 = update: 502755
        """
        mock_question_seq_list = [
            502733, 502734, 502735, 502736, 502737, 502738, 502739, 502740, 502741, 502742,
            502743, 502744, 502745, 502746, 502747, 502751, 502752, 502753, 502754, 502755
        ]
        exam_category = ExamPaperVo()
        mock_list = self.db_client.get_all_question_by_seq_in(mock_question_seq_list)

        for obj in mock_list:
            self.update_exam_paper(exam_category, obj)

        for k, v in exam_category.model_dump().items():
            print(f"category: {k}")
            print(f"value: {v}")
            print(f"sum: {v['high_count'] + v['middle_count'] + v['low_count']}")
            print("===")






