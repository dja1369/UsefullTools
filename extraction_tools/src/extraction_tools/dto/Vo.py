from datetime import datetime

from pydantic import BaseModel

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