from datetime import datetime, timedelta, date

from sqlalchemy import between
from sqlmodel import create_engine, Session, select

from src.extraction_tools.infra.schema import Issue, IssueTagMatch, Tag

class ORM:
    def __init__(self, host:str, db_user: str, db_password: str, port: int, db_name: str):
        self._engine = create_engine(
            url=f"mysql+pymysql://{db_user}:{db_password}@{host}:{port}/{db_name}",
            # echo=True,
        )


    def get_package_data_by_created_at_range(self, day: datetime):
        with (Session(self._engine) as session):
            q = select(
                Issue.issue_code, Issue.created_at
            ).where(
                Issue.is_package == 0,
                between(
                    Issue.created_at,
                    day, day + timedelta(minutes=1440)
                )
            ).order_by(Issue.created_at)

            issue = session.exec(q).fetchall()
            return issue
    def get_sample_data_by_created_at_range(self, day: datetime):
        with (Session(self._engine) as session):
            q = select(Issue.issue_code, Issue.created_at
           ).where(
                between(
                    Issue.created_at,
                    day, day + timedelta(minutes=1440)
                )
            ).where(
                Issue.is_package == 1
            ).order_by(Issue.created_at)
            issue = session.exec(q).fetchall()
            return issue

    def get_all_sample_date_by_issue_tag_match(self, day: datetime):
        with (Session(self._engine) as session):
            q = select(Issue.issue_code, Issue.created_at, Issue.rotate, Issue.package_link,
                       IssueTagMatch.tag_code
           ).join(
                IssueTagMatch, Issue.issue_code == IssueTagMatch.issue_code
            ).where(
                between(
                    Issue.created_at,
                    day, day + timedelta(minutes=1440)
                )
            ).where(
                Issue.is_package == 1
            ).order_by(Issue.created_at)
            issue = session.exec(q).fetchall()
            return issue
    def get_all_sample_date_by_package_link(self, package_link: str):
        with (Session(self._engine) as session):
            q = select(Issue.issue_code, Issue.created_at, Issue.rotate, Issue.package_link
            ).where(
                Issue.package_link == package_link
            ).where(
                Issue.is_package == 1
            ).order_by(Issue.created_at)

            issue = session.exec(q).fetchall()
            return issue

    def get_barcode_by_issue_code(self, issue_code: str):
        with (Session(self._engine) as session):
            q = select(
                IssueTagMatch.tag_code
            ).where(IssueTagMatch.issue_code == issue_code)
            barcode = session.exec(q).one_or_none()
            return barcode

    def get_tag_by_tag_code(self, tag_code: str):
        with (Session(self._engine) as session):
            q = select(
                Tag.tag_name, Tag.tag_code, Tag.barcode, Tag.link_barcode
            ).where(
                (Tag.tag_code == tag_code) |
                (Tag.barcode == tag_code) |
                (Tag.link_barcode == tag_code)
            )
            try: # tag_code가 여러개인 케이스가 존재하면 안되는데 존재함.
                tag = session.exec(q).one_or_none()
            except:
                tag = session.exec(q).fetchall()
                tag = tag[-1]
            return tag


