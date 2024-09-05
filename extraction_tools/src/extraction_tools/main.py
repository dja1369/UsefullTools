import asyncio
from datetime import datetime

from src.extraction_tools.client.ssh_client import SSHClient
from src.extraction_tools.infra.orm import ORM
from src.extraction_tools.util.date_util import DateUtil
from src.extraction_tools.util.directory_util import DirectoryUtil
from src.extraction_tools.util.extraction_util import DataExtractionUtil


def constructor():
    '''
    @return: DateUtil, ORM, SSHClient, DataExtractionUtil, DirectoryUtil
    DateUtil: 입력한 날짜 사이의 모든 기간을 반환하는 클래스
    ORM: 데이터베이스와 연결하는 클래스
    SSHClient: 서버와 연결하는 클래스 -> 파일 다운로드 지원
    DataExtractionUtil: 파일 추출 지원,
    DirectoryUtil: 파일 다운로드, 삭제, 목표 파일 탐색 지원
    '''
    host_ip, host_name, host_password = "101.202.34.105", "deep", "9011plum!#"
    db_user, db_password, db_name, db_port = "root", "deepnoid", "deepshot20240218", 8888

    date_util = DateUtil()

    orm = ORM(
        host=host_ip, db_user=db_user, db_password=db_password, port=db_port, db_name=db_name
    )

    client = SSHClient(host_ip, host_name, host_password)

    data_util = DataExtractionUtil()
    directory_util = DirectoryUtil()
    return date_util, orm, client, data_util, directory_util

date_util, orm, client, data_util ,directory_util = constructor()

async def download_and_upload_images():
    """
    WorkFlow:
    1. 추출을 원하는 날짜 반환
    2. 해당 날짜에 해당하는 데이터베이스 데이터 반환
    3. 데이터베이스 데이터를 이용하여 파일 다운로드
    4. 다운로드 받은 파일을 원하는 위치로 이동
    5. 필요에 따라 파일 추출
    6. 데이터 업로드
    """
    target_date = date_util.search_all_date(datetime(2023, 1, 1), datetime(2024, 8, 31))
    await asyncio.gather(
        package_images(target_date), sample_images(target_date)
    )

async def package_images(target_date: dict):
    img_group = {}
    for key in target_date:
        for day in target_date[key]:
            issue = orm.get_package_data_by_created_ay_range(day)
            img_group.setdefault(day, issue)

    coroutine_arr = []
    for k, v in img_group.items():
        if v:
            local_path = f"input"
            directory_util.make_directory_if_not_exists(local_path)
            for issue_code, created_at in v:
                for position in "condition", "condition":
                    remote_path = f"input"
                    download_path = f"input"
                    coroutine_arr.append(client.download(remote_path, download_path))

    results = await asyncio.gather(*coroutine_arr)
    for result in results:
        if not result:
            print(f"Package Failed to download {result}")
            continue


async def sample_images(target_date: dict):
    img_group = {}
    for key in target_date:
        for day in target_date[key]:
            issue = orm.get_all_sample_data(day)
            img_group.setdefault(day, issue)

    coroutine_arr = []
    for k, v in img_group.items():
        if v:
            local_path = f"input"
            directory_util.make_directory_if_not_exists(local_path)
            for issue_code, created_at in v:
                for position in "condition", "condition":
                    remote_path = f"input"
                    download_path = f"input"
                    coroutine_arr.append(client.download(remote_path, download_path))

    results = await asyncio.gather(*coroutine_arr)
    for result in results:
        if not result:
            print(f"Package Failed to download {result}")
            continue

def find_empty_file():
    resp = []
    directory_util.find_target_file(f"input")
    empty_files: set[str] = directory_util.target_container
    for empty_file in empty_files:
        target = empty_file.split("\\")[-1].split("_")[0]
        barcode = orm.get_barcode_by_issue_code(target)
        if barcode:
            resp.append(barcode)

    return resp



if __name__ == '__main__':
    print(find_empty_file())
    # asyncio.run(download_and_upload_images())

