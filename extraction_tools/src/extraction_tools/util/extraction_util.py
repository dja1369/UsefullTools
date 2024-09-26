import os
import re
import shutil



class DataExtractionUtil:
    def extract_date(self, path):
        pattern = re.compile(r"\d{4}/\d{1,2}/\d{1,2}")
        return pattern.search(path).group()

    def extract_file(self, target: str, destination: str, new_name: str, position: str):
        shutil.move(f"{target}/color.jpg", f"{destination}/{new_name}_{position}_color.jpg")

    def


