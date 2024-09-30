from datetime import datetime
from enum import StrEnum, auto
from typing import Optional

from sqlmodel import SQLModel, Field


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

