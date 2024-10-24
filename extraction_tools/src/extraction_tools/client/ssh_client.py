import asyncio
import os

import paramiko
from stat import S_ISDIR

class SSHClient:
    def __init__(self, host: str, username: str, password: str):
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self._connect(host, username, password)
        try:
            self._sftp = self._client.open_sftp()
        except Exception as e:
            print(f"Failed to open sftp")
            print(f"reason {e}")

    def _connect(self, host_ip: str, host_name: str, password: str):
        try:
            self._client.connect(hostname=host_ip, username=host_name, password=password)
            print(f"Connected to {host_ip} as {host_name}")
        except Exception as e:
            print(f"Failed to connect to {host_ip} as {host_name}")
            print(f"reason {e}")

    async def download(self, remote_path: str, local_path: str):
        try:
            self._sftp.get(remote_path, local_path)
            return True
        except Exception as e:
            return False

    async def folder_download(self, remote_path: str, local_path: str, img_id: str = ""):
        """
        원격지에 다운로드 오브젝트를 확인한다
            폴더인지 검증한다
            폴더라면 재귀적으로 재탐색 한다
                폴더가 아니라면 다운로드를 진행한다
                이때 로컬에 폴더가 없다면 생성한다
        """
        try:
            remote_path = f"{remote_path}{img_id}"
            local_path = f"{local_path}{img_id}"
            files = self._sftp.listdir_attr(remote_path)
            for file in files:
                if S_ISDIR(file.st_mode):
                    await self.folder_download(f"{remote_path}/{file.filename}", f"{local_path}/{file.filename}")
                else:
                    if not os.path.exists(local_path):
                        os.makedirs(local_path, exist_ok=True)
                    if not self.is_exist(f"{remote_path}/{file.filename}"):
                        continue
                    await self.download(f"{remote_path}/{file.filename}", f"{local_path}/{file.filename}")
        except Exception as e:
            print(f"Failed to download {remote_path}")
            print(f"reason {e}")
            return



    async def upload(self, local_path: str, remote_path: str):
        try:
            self._sftp.put(local_path, remote_path)
            return True
        except Exception as e:
            return False

    def check_files_existence(self, merge_rotate_group):
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
                            v[rotate].append(self.is_exist(f"input"))
        return merge_rotate_group

    def is_exist(self, path: str):
        try:
            self._sftp.stat(path)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            return False
