from datetime import datetime

from pydantic import BaseModel

from src.extraction_tools.infra.schema import CategoryEnum, TemplateEnum


class HostInformation(BaseModel):
    ip: str
    name: str
    password: str

class DatabaseInformation(BaseModel):
    host_ip: str
    user: str
    password: str
    db_name: str
    port: int

class IssueTagResult(BaseModel):
    issue_code: str
    rotate: int
    tag_code: str

class IssueCodeNTime(BaseModel):
    issue_code: str
    created_at: datetime

class IssueLinkTagCode(BaseModel):
    issue_code: str
    issue_created_at: datetime
    rotate: int
    package_link: str | None
    tag_code: str

class LanguageVo(BaseModel):
    name: str | None

class DifficultyVo(BaseModel):
    name: str


class QuestionDataVo(BaseModel):
    image_id: str
    filter_name: str
    is_main_image: bool


class OptionVo(BaseModel):
    include_text: LanguageVo | None
    option_data: QuestionDataVo | None


class QuestionVo(BaseModel):
    title: LanguageVo | None
    category: CategoryEnum
    template: TemplateEnum
    difficulty: DifficultyVo
    correct_answer: OptionVo
    solution: LanguageVo
    question_data: list[QuestionDataVo]
    options: list[OptionVo]



class ExamDataVo(BaseModel):
    questions: list[QuestionVo]