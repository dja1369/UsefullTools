from datetime import datetime, timedelta, date

from sqlalchemy import between, func, exists
from sqlmodel import create_engine, Session, select, desc

from src.extraction_tools.infra.schema import Issue, IssueTagMatch, TagLite, TagFull, TagMigration


class ORM:
    def __init__(self, host:str, db_user: str, db_password: str, port: int, db_name: str):
        self._engine = create_engine(
            url=f"mysql+pymysql://{db_user}:{db_password}@{host}:{port}/{db_name}",
            # echo=True,
        )

    def save(self, obj: list[object] | object):
        with Session(self._engine) as session:
            if isinstance(obj, list):
                session.add_all(obj)
            else:
                session.add(obj)
            session.commit()

    def is_exist_migration_tag(self, tag: TagMigration):
        with Session(self._engine) as session:
            q = select(exists().where(TagMigration.tag_code == tag.tag_code))
            return session.exec(q).one()

    def get_tag_by_description(self, description: str):
        with Session(self._engine) as session:
            q = select(TagMigration).where(TagMigration.description == description)
            result = session.exec(q).fetchall()
            if result.__len__() > 2:
                print('result:', result)
            if result:
                return result[-1]
            else:
                return None

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
                TagLite.tag_name, TagLite.tag_code, TagLite.barcode, TagLite.link_barcode
            ).where(
                (TagLite.tag_code == tag_code) |
                (TagLite.barcode == tag_code) |
                (TagLite.link_barcode == tag_code)
            )
            try: # tag_code가 여러개인 케이스가 존재하면 안되는데 존재함.
                tag = session.exec(q).one_or_none()
            except:
                tag = session.exec(q).fetchall()
                tag = tag[-1]
            return tag

    def get_all_issue_count(self):
        with Session(self._engine) as session:
            q = select(func.count()).select_from(Issue)
            count= session.exec(q)
            return count.fetchall()[0]

    def get_issue_by_id(self, id: int):
        with Session(self._engine) as session:
            q = select(Issue).limit(1).offset(id)
            result = session.exec(q).one_or_none()
            return result

    def get_issue_tag_match_by_issue_code(self, issue_code: str):
        with Session(self._engine) as session:
            q = select(IssueTagMatch).where(IssueTagMatch.issue_code == issue_code)
            result = session.exec(q).fetchall()
            return result

    def get_tag_by_tag_code_or_barcode_or_link_barcode(self, tag_code: str):
        with Session(self._engine) as session:
            q = select(TagFull).where(
                (TagFull.tag_code == tag_code) |
                (TagFull.barcode == tag_code) |
                (TagFull.link_barcode == tag_code)
            )
            result = session.exec(q).fetchall()
            if result:
                return result[-1]
            else:
                return None

    def get_issue_by_tag_type(self, tag_type: str):
        with Session(self._engine) as session:
            q = select(
                Issue.issue_code, Issue.created_at
            ).join(
                IssueTagMatch, Issue.issue_code == IssueTagMatch.issue_code
            ).join(
                TagFull, IssueTagMatch.tag_code == TagFull.tag_code
            ).where(
                TagFull.tag_type == tag_type
            ).order_by(
                desc(Issue.created_at)
            )
            result = session.exec(q).fetchall()
            return result