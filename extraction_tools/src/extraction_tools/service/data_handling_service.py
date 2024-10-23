import os
import re
import shutil

import pandas as pd

from src.extraction_tools.infra.orm import ORM
from src.extraction_tools.infra.schema import TagFull, TagMigration
from src.extraction_tools.util.directory_util import DirectoryUtil


class DataHandlingService:
    def __init__(self, directory_util: DirectoryUtil, db_client: ORM):
        self.directory_util = directory_util
        self.db_client = db_client

    def find_empty_file(self):
        # 모종의 사고로 유실된 쁘락치 파일 찾기
        # 사이즈가 0인 파일을 찾아서 해당 파일의 이름을 바코드로 변환하여 반환
        resp = []
        self.directory_util.find_target_file(f"input")
        empty_files: set[str] = self.directory_util.target_container
        for empty_file in empty_files:
            target = empty_file.split("\\")[-1].split("_")[0]
            barcode = self.db_client.get_barcode_by_issue_code(target)
            if barcode:
                resp.append(barcode)

        return resp

    def extract_date(self, path: str):
        pattern = re.compile(r"\d{4}/\d{1,2}/\d{1,2}")
        return pattern.search(path).group()


    def extract_file(self, target: str, destination: str, new_name: str, position: str):
        shutil.move(f"{target}/color.jpg", f"{destination}/{new_name}_{position}_color.jpg")

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

    def find_missing_sample(self, target_date):
        # 샘플 데이터 누락 확인
        img_group = self.db_client.get_image_group_by_date(
            target_date,
            self.db_client.get_sample_data_by_created_at_range
        )
        merge_img_and_tag_group = self._merge_images_and_tags(img_group)
        merge_rotate_group = self._merge_rotations(merge_img_and_tag_group)
        self._save_to_excel(merge_rotate_group)


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

