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

    def is_exist(self, path: str):
        try:
            self._sftp.stat(path)
            return True
        except FileNotFoundError:
            return False
        except Exception as e:
            return False
