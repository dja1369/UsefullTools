import os
import shutil

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

    def remove_folder(self, path):
        try:
            shutil.rmtree(path)
        except Exception:
            print(f"Failed to remove {path}")

    def find_target_file(self, in_path):
        target_path = in_path
        if os.path.exists(target_path):
            target_list = os.listdir(target_path)
            for target in target_list:
                target = target_path + "/" + target
                if os.path.isdir(target):
                    self.find_target_file(target)
                elif target.__contains__(".DS_Store"):
                    continue
                else:
                    self.target_container.add(target_path)

    def find_target_dir(self, in_path):
        target_path = in_path
        print(target_path)
        if os.path.exists(target_path):
            target_list = os.listdir(target_path)
            if not "end" in target_list: # end file is Download complete flag
                for dir in target_list:
                    self.find_target_dir(target_path+'/'+dir)
            else:
                self.target_container.add(target_path)

    def find_remove_target_folder(self, in_path):
        target_path = in_path
        if os.path.exists(target_path):
            target_list = os.listdir(target_path)
            for target in target_list:
                if len(target) >= 5: # UUID length
                    target = target_path + "/" + target
                    if os.path.isdir(target):
                        self.target_container.add(target)
                        continue
                    else: continue
                target = target_path + "/" + target
                if os.path.isdir(target):
                    self.find_remove_target_folder(target)
                elif target.__contains__(".DS_Store"):
                    continue


    def _move_folder(self, target: str, destination: str):
        os.remove(f"{target}/end")
        shutil.move(target, destination)

    def _remove_folder(self, target: str):
        if os.path.isdir(target):
            print(f"Remove {target}")
            shutil.rmtree(target)