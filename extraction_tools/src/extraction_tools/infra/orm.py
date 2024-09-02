from datetime import datetime, timedelta

from sqlalchemy import between
from sqlmodel import create_engine, Session, select

from src.extraction_tools.infra.schema import Issue


class ORM:
    def __init__(self, host:str, db_user: str, db_password: str, port: int, db_name: str):
        self._engine = create_engine(
            url=f"mysql+pymysql://{db_user}:{db_password}@{host}:{port}/{db_name}",
            # echo=True,
        )

    def get_issue_id_and_created_time(self, day: datetime):
        with (Session(self._engine) as session):
            q = select(
                Issue.issue_code, Issue.created_at
            ).where(
                between(
                    Issue.created_at,
                    day , day + timedelta(minutes=1440)
                )
            ).order_by(Issue.created_at)
            issue = session.exec(q).fetchall()
            return issue


