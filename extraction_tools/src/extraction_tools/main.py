import asyncio
import sys
from datetime import datetime, date

import sqlalchemy

from src.extraction_tools.dto.Vo import HostInformation, DatabaseInformation, IssueTagResult, IssueCodeNTime, \
    IssueLinkTagCode
from src.extraction_tools.client.ssh_client import SSHClient
from src.extraction_tools.infra.orm import ORM
from src.extraction_tools.infra.schema import Issue, IssueTagMatch, TagFull, TagMigration, IssueTagMatchMigration
from src.extraction_tools.util.date_util import DateUtil
from src.extraction_tools.util.directory_util import DirectoryUtil
from src.extraction_tools.util.data_handling_util import DataHandlingUtil

class ExtractionToolApplication:
    def __init__(self,
                 db_client: ORM,
                 ssh_client: SSHClient,
                 ):
        '''
        DBClient: 데이터베이스와 연결하는 클래스,
        SSHClient: 서버와 연결하는 클래스 -> 파일 다운로드 지원,
        DateUtil: 입력한 날짜 사이의 모든 기간을 반환하는 클래스,
        ExtractionUtil: 파일 추출 지원,
        DirectoryUtil: 파일 다운로드, 삭제, 목표 파일 탐색 지원
        '''
        self.download_path = None
        self.upload_path = None
        self.db_client = db_client
        self.ssh_client = ssh_client
        self.date_util = DateUtil()
        self.data_handling_util = DataHandlingUtil()
        self.directory_util = DirectoryUtil()

    async def find_target_tag_issue(self, target_information: dict[str, int]):
        #   데이터 있는지 검증하고 있다면 해당 데이터를 가져옴
        #   다운로드, 업로드를 했다면 count 1 증가
        #   count가 target_count와 같아지면 종료
        coroutines = []
        for tag_type, target_count in target_information.items():
            count = 0
            issues: list[Issue] = self.db_client.get_issue_by_tag_type(tag_type)
            self.directory_util.make_directory_if_not_exists(self.upload_path+"/"+tag_type)
            for issue in issues:
                if count == target_count:
                    break
                for position in "da", "da":
                    remote_path = f"{self.download_path}/{issue.issue_code}/{position}/color.jpg"
                    local_path = f"{self.upload_path}/{tag_type}/{issue.issue_code}_{position}_color.jpg"
                    if self.ssh_client.is_exist(remote_path):
                        coroutines.append(self.ssh_client.download(remote_path, local_path))
                        count += 1
        #   Download And Upload
        result = await asyncio.gather(*coroutines)
        return result

    async def upload_all_sample_images(self):
        target_date = self.date_util.search_all_date(datetime(2023, 1, 1), datetime(2024, 12, 31))
        img_group: dict[date, list[IssueTagResult]] = self._get_image_group_by_date(
            target_date,
            self.db_client.get_sample_data_by_created_at_range
        )
        await self._validate_sample_images(img_group)

    async def _validate_sample_images(self, img_group: dict[date, list[IssueTagResult]]):
        coroutines = []

        for k, v in img_group.items():
            if not v:
                continue
            self.directory_util.make_directory_if_not_exists(self.upload_path)
            for issue_tag_result in v:
                for position in "top", "side":
                    remote_path = f"{self.download_path}/{issue_tag_result.issue_code}/{position}/color.jpg"
                    local_path = (f"{self.upload_path}/{issue_tag_result.tag_code}_color"
                                  f"_{issue_tag_result.rotate}_{position}"
                                  f"_{issue_tag_result.issue_code}.jpg")
                    if self.ssh_client.is_exist(remote_path):
                        coroutines.append(self.ssh_client.download(remote_path, local_path))
        await asyncio.gather(*coroutines)
        return "Done"


    async def upload_all_package_images(self):
        """
        WorkFlow:
        1. 추출을 원하는 날짜 반환
        2. 해당 날짜에 해당하는 데이터베이스 데이터 반환
        3. 데이터베이스 데이터를 이용하여 파일 다운로드
        4. 다운로드 받은 파일을 NAS에 업로드
        """
        target_date = self.date_util.search_all_date(datetime(2023, 1, 1), datetime(2024, 8, 31))
        img_group: dict[date, list[IssueCodeNTime]] = self._get_image_group_by_date(
            target_date,
            self.db_client.get_package_data_by_created_at_range
        )
        await self._validate_package_images(img_group)


    def _get_image_group_by_date(self, target_date: dict[str, list[date]], data_fetch_func: callable) -> dict[date, list[IssueTagResult | IssueCodeNTime | IssueLinkTagCode]]:
        img_group = {}
        for key in target_date:
            for day in target_date[key]:
                issues: list[IssueTagResult | IssueCodeNTime | IssueLinkTagCode] = data_fetch_func(day)
                img_group.setdefault(day, issues)

        return img_group

    async def _validate_package_images(self, img_group: dict[date, list[IssueCodeNTime]]):
        coroutines = []

        for k, v in img_group.items():
            if not v:
                continue
            year, month, day = k.year, k.month, k.day
            self.directory_util.make_directory_if_not_exists(self.upload_path)
            for obj in v:
                for position in "none", "none":
                    coroutines.append(self.ssh_client.download(self.download_path, self.upload_path))

        results = await asyncio.gather(*coroutines)
        for result in results:
            if not result:
                print(f"Failed to download {result}")
                continue

    def find_empty_file(self):
        # 모종의 사고로 유실된 쁘락치 파일 찾기
        resp = []
        self.directory_util.find_target_file(f"input")
        empty_files: set[str] = self.directory_util.target_container
        for empty_file in empty_files:
            target = empty_file.split("\\")[-1].split("_")[0]
            barcode = self.db_client.get_barcode_by_issue_code(target)
            if barcode:
                resp.append(barcode)

        return resp

    def export_missing_sample(self):
        # 유실된 데이터를 찾아서..
        target_date: dict[str, list[date]] = self.date_util.search_all_date(datetime(2023, 10, 1), datetime(2024, 10, 10))
        img_group: dict[date, list[IssueLinkTagCode]] = self._get_image_group_by_date(
            target_date,
            self.db_client.get_all_sample_date_by_issue_tag_match
        )
        merge_img_and_tag_group = self._merge_images_and_tags(img_group)
        merge_rotate_group = self._merge_rotations(merge_img_and_tag_group)
        merge_rotate_group = self.ssh_client.check_files_existence(merge_rotate_group)
        self.data_handling_util.save_to_excel(merge_rotate_group)

    def _merge_images_and_tags(self, img_group):
        # 이슈 와 태그 정보 병합
        merge_img_and_tag_group = {}
        for k, v in img_group.items():
            if not v:
                continue
            for obj in v:
                tag = self.db_client.get_tag_by_tag_code(obj.tag_code)
                tag_info = self._get_tag_info(obj, tag)
                merge_img_and_tag_group.setdefault(k, []).append(tag_info)
        return merge_img_and_tag_group

    def _get_tag_info(self, obj, tag):
        # 태그 조건 확인
        if not tag:
            return [obj.issue_code, obj.issue_created_at, obj.rotate, obj.package_link, "None", "None"]
        if obj.tag_code == tag.tag_code:
            return [obj.issue_code, obj.issue_created_at, obj.rotate, obj.package_link, tag.tag_name, tag.tag_code]
        if obj.tag_code == tag.barcode:
            return [obj.issue_code, obj.issue_created_at, obj.rotate, obj.package_link, tag.tag_name, tag.barcode]
        if obj.tag_code == tag.link_barcode:
            return [obj.issue_code, obj.issue_created_at, obj.rotate, obj.package_link, tag.tag_name, tag.link_barcode]

    def _merge_rotations(self, merge_img_and_tag_group):
        # 이슈와 회전된 이슈 정보 병합
        # [obj.issue_code, obj.issue_created_at, obj.rotate, obj.package_link, tag.tag_name, tag.link_barcode]
        merge_rotate_group = {}
        for k, v in merge_img_and_tag_group.items():
            for obj in v:
                temp = {obj[0]: {0: obj}}
                package_link_sample = self.db_client.get_all_sample_date_by_package_link(obj[0])
                for sample in package_link_sample:
                    if obj[0] == sample.package_link:
                        temp[obj[0]][sample.rotate] = list(sample) + [obj[4], obj[5]]
                merge_rotate_group.setdefault(k, []).append(temp)
        return merge_rotate_group

# TODO: 리팩토링 부터 -> 구조 분해 -> 문제 이미지 추출 -> 문제 이미지 업로드 -> 문제 데이터 업로드

if __name__ == '__main__':
    sys.setrecursionlimit(5000)
    remote_host = HostInformation(
        ip="host_ip",
        name="host_name",
        password="host_password"
    )
    ssh = SSHClient(
        host=remote_host.ip,
        username=remote_host.name,
        password=remote_host.password
    )

    db_information = DatabaseInformation(
        host_ip="ha",
        user="ha",
        password="ha",
        db_name="ha",
        port=0000
    )

    db = ORM(
        host=db_information.host_ip,
        db_user=db_information.user,
        db_password=db_information.password,
        db_name=db_information.db_name,
        port=db_information.port,
    )
    application = ExtractionToolApplication(
        ssh_client=ssh,
        db_client=db
    )





