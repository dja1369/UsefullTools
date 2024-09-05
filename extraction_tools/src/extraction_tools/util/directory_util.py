import os
import shutil
from collections.abc import Callable


class DirectoryUtil:
    def __init__(self):
        self.target_container = set()

    def make_directory_if_not_exists(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def end_file(self, path):
        filename = path + "/end"
        with open (filename, "a") as f:
            f.write("end")

    def _move_folder(self, target: str, destination: str):
        # remove end file and move folder
        os.remove(f"{target}/end")
        shutil.move(target, destination)

    def remove_folder(self, path):
        try:
            shutil.rmtree(path)
        except Exception:
            print(f"Failed to remove {path}")

    def _traverse_directory(self, in_path: str, condition_func: Callable):
        if os.path.exists(in_path):
            target_list = os.listdir(in_path)
            for target in target_list:
                full_path = os.path.join(in_path, target)
                if full_path.__contains__(".DS_Store"):
                    continue
                if condition_func(full_path):
                    self.target_container.add(full_path)
                else:
                    if os.path.isfile(full_path):  # not target file
                        continue
                    self._traverse_directory(full_path, condition_func)

    def find_empty_file(self, in_path: str):
        def condition_func(full_path):
            return os.path.isfile(full_path) and os.path.getsize(full_path) == 0
        self._traverse_directory(in_path, condition_func)

    def find_target_file(self, in_path: str):
        def condition_func(full_path):
            return os.path.isfile(full_path)
        self._traverse_directory(in_path, condition_func)

    def find_download_ended_dir(self, in_path: str):
        def condition_func(full_path):
            return os.path.isdir(full_path) and "end" in os.listdir(full_path)
        self._traverse_directory(in_path, condition_func)



