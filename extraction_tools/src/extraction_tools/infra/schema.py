from datetime import datetime, time
from enum import StrEnum, auto
from typing import Optional

from sqlalchemy import table
from sqlmodel import SQLModel, Field, Relationship


class Status(StrEnum):
    before = auto()
    doing = auto()
    done = auto()


class Issue(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    issue_code: str = Field()
    difficulty: int
    created_at: datetime
    complete: str
    description: str
    xray_type: str = Field(index=True)
    is_package: str = Field(index=True)
    rotate: int = Field(index=True)
    package_link: str = Field(index=True)
    label_status: Status
    label_status_updated_at: datetime
    updated_at: datetime


class IssueTagMatch(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    issue_code: str = Field(index=True)
    tag_code: str = Field(index=True)


class IssueTagMatchMigration(SQLModel, table=True):
    __tablename__ = "issuetagmatch_migration"
    id: Optional[int] = Field(default=None, primary_key=True)
    issue_code: str = Field(index=True)
    tag_code: str = Field(index=True)


class TagLite(SQLModel, table=True):
    __tablename__ = "tag"
    id: Optional[int] = Field(default=None, primary_key=True)
    tag_code: str
    tag_name: str
    barcode: str
    link_barcode: str


class TagFull(SQLModel, table=True):
    __tablename__ = "tag"
    __table_args__ = {"extend_existing": True}

    id: Optional[int] = Field(default=None, primary_key=True)
    tag_code: str
    tag_name: str
    description: str
    barcode: str = Field(index=True)
    link_barcode: str
    tag_type: str
    obj_type: str
    battery_code: str
    created_at: datetime
    updated_at: datetime | None


class TagMigration(SQLModel, table=True):
    __tablename__ = "tag_migration"

    id: Optional[int] = Field(default=None, primary_key=True)
    tag_code: str
    tag_name: str
    description: str
    barcode: str = Field(index=True)
    link_barcode: str
    tag_type: str
    obj_type: str
    battery_code: str
    created_at: datetime
    updated_at: datetime | None


class Language(SQLModel, table=True):
    __tablename__ = 'language'
    seq: int = Field(primary_key=True, default=None)
    kr: str
    en: str
    created_at: datetime


class UpperStrEnum(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name.upper()


class DifficultyEnum(UpperStrEnum):
    상 = auto()
    중 = auto()
    하 = auto()


class Difficulty(SQLModel, table=True):
    __tablename__ = 'difficulty'
    seq: int = Field(primary_key=True, default=None)
    name: DifficultyEnum
    created_at: datetime


class CategoryEnum(UpperStrEnum):
    READING = auto()
    MATERIAL = auto()
    DANGER = auto()


class TemplateEnum(UpperStrEnum):
    READING = auto()
    Q_IMG_TXT_OP_IMG_TXT = auto()
    Q_TXT_OP_IMG = auto()
    Q_TXT_IMG_OP_TXT = auto()
    Q_TXT_OP_TXT = auto()
    Q_TXT_IMG_OP_IMG = auto()
    Q_TXT_OP_TXT_COLOR = auto()
    Q_TXT_IMG_OP_TXT_COLOR = auto()


class Question(SQLModel, table=True):
    __tablename__ = 'question'
    seq: int = Field(primary_key=True, default=None)
    title_seq: int | None = Field(foreign_key='language.seq')
    category: CategoryEnum
    template: TemplateEnum
    difficulty_seq: int = Field(foreign_key='difficulty.seq')
    correct_answer_seq: int | None
    solution_seq: int = Field(foreign_key='language.seq')  # 해설
    made_by: str
    created_at: datetime

    exam: "Exam" = Relationship(back_populates="question_list", link_model="ExamPaper")
    questions_data: list["QuestionData"] | None = Relationship(back_populates="question", cascade_delete=True)
    options: list["Option"] = Relationship(back_populates="question", cascade_delete=True)


class QuestionData(SQLModel, table=True):
    __tablename__ = 'question_data'
    seq: int = Field(primary_key=True, default=None)
    question_seq: int = Field(foreign_key='question.seq')
    image_id: str
    filter: str
    is_main_image: bool
    created_at: datetime
    question: "Question" = Relationship(back_populates="question_data")


class Option(SQLModel, table=True):
    __tablename__ = 'option'
    seq: int = Field(primary_key=True, default=None)
    question_seq: int = Field(foreign_key='question.seq')
    included_text_seq: int = Field(foreign_key='language.seq')
    created_at: datetime

    question: "Question" = Relationship(back_populates="options")
    option_data: list["OptionData"] = Relationship(back_populates="option", cascade_delete=True)


class OptionData(SQLModel, table=True):
    __tablename__ = 'option_data'
    seq: int = Field(primary_key=True, default=None)
    option_seq: int = Field(foreign_key='option.seq')
    image_id: str
    filter: str
    created_at: datetime
    option: "Option" = Relationship(back_populates="option_data")


class ExamPaper(SQLModel, table=True):
    __tablename__ = 'exam_paper'
    seq: int = Field(primary_key=True, default=None)
    exam_id: str = Field(foreign_key='exam.id')
    question_seq: int = Field(foreign_key='question.seq')
    created_at: datetime


class ExamType(UpperStrEnum):
    EXAM = auto()
    MOCK_EXAM = auto()


class Exam(SQLModel, table=True):
    __tablename__ = 'exam'
    id: str = Field(primary_key=True)
    end_date: datetime = Field(nullable=True)
    start_date: datetime = Field(nullable=True)
    time_limit: time
    created_at: datetime
    certification_seq: int = Field(foreign_key='certifacation.seq')
    name_seq: int = Field(foreign_key='language.seq')
    description_seq: int | None = Field(foreign_key='language.seq', nullable=True)
    type: ExamType
    reading_count: int = Field(nullable=True)
    material_count: int = Field(nullable=True)
    danger_count: int = Field(nullable=True)
    total_count: int = Field(nullable=True)
    report_opened_at: datetime | None = Field(nullable=True)
    report_closed_at: datetime | None = Field(nullable=True)

    question_list: list["Question"] = Relationship(back_populates="exam", link_model=ExamPaper,
                                                   cascade_delete=True)
