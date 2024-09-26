import os
import re
import shutil

import pandas as pd


class DataExtractionUtil:
    def extract_date(self, path):
        pattern = re.compile(r"\d{4}/\d{1,2}/\d{1,2}")
        return pattern.search(path).group()

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


