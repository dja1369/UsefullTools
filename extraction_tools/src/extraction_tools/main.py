from extraction_tools.src.extraction_tools.client.ssh_client import SSHClient
from extraction_tools.src.extraction_tools.infra.orm import ORM
from extraction_tools.src.extraction_tools.util.date_util import DateUtil
from extraction_tools.src.extraction_tools.util.directory_util import DirectoryUtil
from extraction_tools.src.extraction_tools.util.extraction_util import DataExtractionUtil


def constructor():
    '''
    @return: DateUtil, ORM, SSHClient, DataExtractionUtil, DirectoryUtil
    DateUtil: 입력한 날짜 사이의 모든 기간을 반환하는 클래스
    ORM: 데이터베이스와 연결하는 클래스
    SSHClient: 서버와 연결하는 클래스 -> 파일 다운로드 지원
    DataExtractionUtil: 파일 추출 지원,
    DirectoryUtil: 파일 다운로드, 삭제, 목표 파일 탐색 지원
    '''
    host_ip, host_name, host_password = None, None, None
    db_user, db_password, db_name, db_port = None, None, None, None

    date_util = DateUtil()

    orm = ORM(
        host=host_ip, db_user=db_user, db_password=db_password, port=db_port,db_name=db_name
    )

    client = SSHClient(host_ip, host_name, host_password)

    data_util = DataExtractionUtil()
    directory_util = DirectoryUtil()
    return date_util, orm, client, data_util, directory_util

date_util, orm, client, data_util ,directory_util = constructor()
def main():
    """
    WorkFlow:
    1. 추출을 원하는 날짜 반환
    2. 해당 날짜에 해당하는 데이터베이스 데이터 반환
    3. 데이터베이스 데이터를 이용하여 파일 다운로드
    4. 다운로드 받은 파일을 원하는 위치로 이동
    5. 필요에 따라 파일 추출
    6. 데이터 업로드
    """

