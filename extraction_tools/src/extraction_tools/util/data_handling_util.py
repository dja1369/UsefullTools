import os
import re
import shutil

import pandas as pd

from src.extraction_tools.infra.schema import TagFull, TagMigration


class DataHandlingUtil:
    def extract_date(self, path: str):
        pattern = re.compile(r"\d{4}/\d{1,2}/\d{1,2}")
        return pattern.search(path).group()

    def migration_tag_entity(self, tag: TagFull):
        # A-Z까지1,2개 - 숫자 2개 - 숫자 4개 형식 찾는 정규 표현식
        pattern = re.compile(r"^[A-Z]{1,4}-\d{2}-\d{4}$")
        # for attr, value in tag.__dict__.items():
        for attr, value in tag:
            if isinstance(value, str) and pattern.match(value):
               return TagMigration(
                   tag_code=value,
                   tag_name=tag.tag_name,
                   description=tag.description,
                   barcode=value,
                   link_barcode=None,
                   tag_type=value.split("-")[0],
                   obj_type=tag.obj_type,
                   battery_code=tag.battery_code,
                   created_at=tag.created_at,
                   updated_at=tag.updated_at
               )

    def extract_file(self, target: str, destination: str, new_name: str, position: str):
        shutil.move(f"{target}/color.jpg", f"{destination}/{new_name}_{position}_color.jpg")

    def save_to_excel(self, merge_rotate_group):
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



