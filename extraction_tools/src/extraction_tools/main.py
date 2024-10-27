from datetime import datetime

from src.extraction_tools.client.ssh_client import SSHClient
from src.extraction_tools.dto.Vo import HostInformation, DatabaseInformation
from src.extraction_tools.infra.orm import ORM
from src.extraction_tools.service.data_handling_service import DataHandlingService
from src.extraction_tools.service.exam_build_service import ExamBuildService
from src.extraction_tools.service.image_extract_service import ImageExtractService
from src.extraction_tools.service.image_upload_service import ImageUploadService
from src.extraction_tools.util.date_util import DateUtil
from src.extraction_tools.util.directory_util import DirectoryUtil


class ExtractionToolApplication:
    def __init__(self,
                 date_module: DateUtil,
                 data_handling_module: DataHandlingService,
                 img_upload_module: ImageUploadService,
                 img_extract_module: ImageExtractService,
                 exam_build_module: ExamBuildService
                 ):
        '''
        DBClient: 데이터베이스와 연결하는 클래스,
        SSHClient: 서버와 연결하는 클래스 -> 파일 다운로드 지원,
        DateUtil: 입력한 날짜 사이의 모든 기간을 반환하는 클래스,
        ExtractionUtil: 파일 추출 지원,
        DirectoryUtil: 파일 다운로드, 삭제, 목표 파일 탐색 지원
        '''
        self.download_path = None
        self.upload_path = None
        self.data_handling_util = data_handling_module
        self.img_upload_service = img_upload_module
        self.img_extract_service = img_extract_module
        self.date_util = date_module
        self.exam_build_service = exam_build_module

    async def process_upload_all_sample_images(self):
        # 기간내의 모든 샘플 이미지를 업로드
        target_date = self.date_util.search_all_date(datetime(2023, 1, 1), datetime(2024, 12, 31))
        await self.img_upload_service.upload_all_sample_images(
            target_date,
            self.download_path,
            self.upload_path
        )

    async def upload_all_package_images(self):
        # 기간내의 모든 패키지 이미지를 업로드
        target_date = self.date_util.search_all_date(datetime(2023, 1, 1), datetime(2024, 8, 31))
        await self.img_upload_service.upload_all_package_images(
            target_date,
            self.download_path,
            self.upload_path
        )

    def process_find_empty_file(self):
        # 빈 파일 찾아서 바코드로 변환하여 반환
        return self.data_handling_util.find_empty_file()

    def process_export_missing_sample(self):
        # 누락된 샘플데이터 리스트를 엑셀로 추출
        target_date = self.date_util.search_all_date(datetime(2023, 1, 1), datetime(2024, 8, 31))
        self.data_handling_util.find_missing_sample(target_date)

    def process_extract_exam_image(self):
        target_question_seq: list[int] = []
        self.img_extract_service.extract_target_questions_and_option_images(
            target_question_seq,
            self.download_path,
            self.upload_path
        )

    def extract_exam_data(self):
        """
        시험 데이터 추출
        문제, 문제 데이터, 옵션, 옵션 데이터 (시퀀스 빼고 모두 추출)
        @return: None
        """
        self.exam_build_service.extract_exam_data()

    def process_make_exam(self):
        pass


if __name__ == '__main__':
    date_util = DateUtil()
    directory_util = DirectoryUtil()
    remote_host = HostInformation(
        ip="host_ip",
        name="host_name",
        password="host_password"
    )
    ssh = SSHClient(
        host=remote_host.ip,
        username=remote_host.name,
        password=remote_host.password
    )

    db_information = DatabaseInformation(
        host_ip="ha",
        user="ha",
        password="ha",
        db_name="ha",
        port=0000
    )

    db = ORM(
        host=db_information.host_ip,
        db_user=db_information.user,
        db_password=db_information.password,
        db_name=db_information.db_name,
        port=db_information.port,
    )

    image_upload_service = ImageUploadService(
        ssh_client=ssh,
        directory_util=directory_util,
        db_client=db
    )

    exam_db_information = DatabaseInformation(
        host_ip="ha",
        user="ha",
        password="ha",
        db_name="ha",
        port=0000
    )
    exam_db = ORM(
        host=exam_db_information.host_ip,
        db_user=exam_db_information.user,
        db_password=exam_db_information.password,
        db_name=exam_db_information.db_name,
        port=exam_db_information.port,
    )

    image_extract_service = ImageExtractService(
        db_client=exam_db,
        directory_util=directory_util,
        ssh_client=ssh
    )

    data_handling_service = DataHandlingService(
        directory_util=directory_util,
        db_client=db
    )
    exam_build_service = ExamBuildService(
        db_client=exam_db
    )

    application = ExtractionToolApplication(
        data_handling_module=data_handling_service,
        img_upload_module=image_upload_service,
        date_module=date_util,
    )
