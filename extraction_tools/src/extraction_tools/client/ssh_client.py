import paramiko


class SSHClient:
    def __init__(self, host: str, username: str, password: str):
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self._connect(host, username, password)
        self._sftp = self._client.open_sftp()

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
