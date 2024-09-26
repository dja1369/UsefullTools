import asyncio
from datetime import datetime

import pandas as pd

from src.extraction_tools.dto.Vo import HostInformation, DatabaseInformation
from src.extraction_tools.client.ssh_client import SSHClient
from src.extraction_tools.infra.orm import ORM
from src.extraction_tools.util.date_util import DateUtil
from src.extraction_tools.util.directory_util import DirectoryUtil
from src.extraction_tools.util.extraction_util import DataExtractionUtil

class ExtractionToolApplication:
    def __init__(self,
                 host_information: HostInformation,
                 db_information: DatabaseInformation
                 ):
        '''
        DBClient: 데이터베이스와 연결하는 클래스,
        SSHClient: 서버와 연결하는 클래스 -> 파일 다운로드 지원,
        DateUtil: 입력한 날짜 사이의 모든 기간을 반환하는 클래스,
        ExtractionUtil: 파일 추출 지원,
        DirectoryUtil: 파일 다운로드, 삭제, 목표 파일 탐색 지원
        '''

        self.db_client = ORM(
            host=host_information.host_ip,
            db_user=db_information.db_user,
            db_password=db_information.db_password,
            port=db_information.db_port,
            db_name=db_information.db_name
        )
        self.ssh_client = SSHClient(
            host=host_information.host_ip,
            username=host_information.host_name,
            password=host_information.host_password
        )
        self.date_util = DateUtil()
        self.extraction_util = DataExtractionUtil()
        self.directory_util = DirectoryUtil()


    async def download_and_upload_images(self):
        """
        WorkFlow:
        1. 추출을 원하는 날짜 반환
        2. 해당 날짜에 해당하는 데이터베이스 데이터 반환
        3. 데이터베이스 데이터를 이용하여 파일 다운로드
        4. 다운로드 받은 파일을 원하는 위치로 이동
        5. 필요에 따라 파일 추출
        6. 데이터 업로드
        """
        target_date = self.date_util.search_all_date(datetime(2023, 1, 1), datetime(2024, 8, 31))

        await asyncio.gather(
            self._download_images(
                target_date,
                self.db_client.get_package_data_by_created_at_range
            ),
            self._download_images(
                target_date,
                self.db_client.get_sample_data_by_created_at_range
                )
        )

    async def _download_images(self, target_date: dict, target_image_fetch_func: callable):
        img_group = self._get_image_group_by_date(target_date, target_image_fetch_func)
        await self._validate_images(img_group)


    def _get_image_group_by_date(self, target_date: dict, data_fetch_func: callable):
        img_group = {}
        for key in target_date:
            for day in target_date[key]:
                issue = data_fetch_func(day)
                img_group.setdefault(day, issue)

        return img_group

    async def _validate_images(self, img_group: dict):
        coroutines = []

        for k, v in img_group.items():
            if v:
                local_path = f"input"
                self.directory_util.make_directory_if_not_exists(local_path)
                for issue_code, created_at in v:
                    for position in "condition", "condition":
                        remote_path = f"input"
                        download_path = f"input"
                        coroutines.append(self.ssh_client.download(remote_path, download_path))

        results = await asyncio.gather(*coroutines)
        for result in results:
            if not result:
                print(f"Failed to download {result}")
                continue

    def find_empty_file(self):
        resp = []
        self.directory_util.find_target_file(f"input")
        empty_files: set[str] = self.directory_util.target_container
        for empty_file in empty_files:
            target = empty_file.split("\\")[-1].split("_")[0]
            barcode = self.db_client.get_barcode_by_issue_code(target)
            if barcode:
                resp.append(barcode)

        return resp

    def find_missing_sample(self):
        target_date = self.date_util.search_all_date(datetime(2024, 1, 1), datetime(2024, 9, 10))
        img_group = self._get_image_group_by_date(target_date, self.db_client.get_all_sample_date_by_issue_tag_match)
        merge_img_and_tag_group = self._merge_images_and_tags(img_group)
        merge_rotate_group = self._merge_rotations(merge_img_and_tag_group)
        self._check_files_existence(merge_rotate_group)
        self._save_to_excel(merge_rotate_group)

    def _merge_images_and_tags(self, img_group):
        # 이슈 와 태그 정보 병합
        merge_img_and_tag_group = {}
        for k, v in img_group.items():
            if v:
                for obj in v:
                    tag = self.db_client.get_tag_by_tag_code(obj.tag_code)
                    tag_info = self.get_tag_info(obj, tag)
                    merge_img_and_tag_group.setdefault(k, []).append(tag_info)
        return merge_img_and_tag_group

    def get_tag_info(self, obj, tag):
        if not tag:
            return [obj.issue_code, obj.created_at, obj.rotate, obj.package_link, "None", "None"]
        if obj.tag_code == tag.tag_code:
            return [obj.issue_code, obj.created_at, obj.rotate, obj.package_link, tag.tag_name, tag.tag_code]
        if obj.tag_code == tag.barcode:
            return [obj.issue_code, obj.created_at, obj.rotate, obj.package_link, tag.tag_name, tag.barcode]
        if obj.tag_code == tag.link_barcode:
            return [obj.issue_code, obj.created_at, obj.rotate, obj.package_link, tag.tag_name, tag.link_barcode]

    def _merge_rotations(self, merge_img_and_tag_group):
        # 이슈와 회전된 이슈 정보 병합
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

    def _check_files_existence(self, merge_rotate_group):
        # 파일 존재 여부 확인
        remote_path = f"input"
        for day, issue_arr in merge_rotate_group.items():
            for issue in issue_arr:
                for k, v in issue.items():
                    for rotate in [0,0,0]:
                        if rotate not in v:
                            v[rotate] = [False] * 8
                            continue
                        check_file = v[rotate][0]
                        for position in ["condition", "condition"]:
                            v[rotate].append(self.ssh_client.is_exist(f"input"))

    def _save_to_excel(self, merge_rotate_group):
        # 엑셀로 저장
        result_group = {}
        count = 0
        for day, issue_arr in merge_rotate_group.items():
            for issue in issue_arr:
                for k, v in issue.items():
                    result_group[count] = {
                        "img_name": v[0][0],
                        "barcode_name": v[0][5],
                        "0_top": v[0][6],
                        "0_side": v[0][7],
                        "45_top": v[45][6],
                        "45_side": v[45][7],
                        "90_top": v[90][6],
                        "90_side": v[90][7],
                        "created_date": str(v[0][1]).split(" ")[0],
                        "created_time": str(v[0][1]).split(" ")[1]
                    }
                    count += 1
        df = pd.DataFrame.from_dict(result_group, orient="index")
        df.to_excel(f"input")


if __name__ == '__main__':
    host = HostInformation("host_ip", "host_name", "host_password")
    db = DatabaseInformation("db_user", "db_password", "db_name", 0000)
    service = ExtractionToolApplication(
        host_information=host,
        db_information=db
    )
    # find_missing_sample()
    # print(find_empty_file())
    # asyncio.run(download_and_upload_images())

