"""Dropbox api 사용법.

저용량, 대용량 파일 업/다운로드 방법과 파일 목록 출력 방법 등 dropbox api 사용법을 소개하는 모듈.

필수 패키지: https://pypi.org/project/dropbox/
공식 가이드: https://dropbox-sdk-python.readthedocs.io

테스트 앱 위치: dropbox_api_tutorial_keys.csv 참조
FORUS_AI_RESOURCES_APP_ACCESS_TOKEN 값: dropbox_api_tutorial_keys.csv 참조

작성자: 손동우
작성일: 2020. 6. 2.
"""
import logging
import dropbox.files

# TODO: 코드 실행 전 dropbox_api_tutorial_keys.csv에 적힌 값으로 바꿀 것
FORUS_AI_RESOURCES_APP_ACCESS_TOKEN = 'NULL'

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)
dbx = dropbox.Dropbox(FORUS_AI_RESOURCES_APP_ACCESS_TOKEN)

# 저용량 파일 저장 예시(150MB 이하 전용)
# https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html?highlight=files_upload()#dropbox.dropbox.Dropbox.files_upload 참조
small_data = 'example_data'
binary_data = small_data.encode('ascii')
small_file_path = '/small_file_testing/file.txt'
metadata = dbx.files_upload(binary_data, small_file_path)
logger.warning('저용량 파일 업로드 완료')

# 액세스 토큰 폴더 내 존재하는 폴더/파일 출력
logger.warning('저용량 파일 저장 후 폴더/파일 목록:')
for entry in dbx.files_list_folder('').entries:
    logger.warning("\t" + entry.name)

# 대용량 파일 업로드 테스트용 200MB 파일 생성
logger.warning('대용량 파일(200MB) 생성')
with open("200MB_file", "wb") as out:
    out.truncate(1024 * 1024 * 200)

# 대용량 파일 저장 예시(최대 48시간 내 350GB 까지 업로드 가능) - 150MB 초과 파일을 150MB 청크들로 분할하여 업로드
# https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html#dropbox.dropbox.Dropbox.files_upload_session_start 참조
logger.warning('대용량 파일(200MB) 업로드 시작')
CHUNK_SIZE = 1024 * 1024 * 150  # 150MB

large_file = open('200MB_file', 'rb')
large_file_path = '/large_file_testing/200MB_file'

chunk = large_file.read(CHUNK_SIZE)
session_info = dbx.files_upload_session_start(chunk)
cursor = dropbox.files.UploadSessionCursor(
    session_id=session_info.session_id,
    offset=large_file.tell(),
)
# 남은 청크들 업로드용 loop
while True:
    chunk = large_file.read(CHUNK_SIZE)

    if not chunk:
        dbx.files_upload_session_finish(
            b'',
            dropbox.files.UploadSessionCursor(
                session_id=session_info.session_id,
                offset=large_file.tell(),
            ),
            dropbox.files.CommitInfo(
                large_file_path,
                dropbox.files.WriteMode('add'),
            ),
        )
        break
    else:
        # 청크 분할 후 남은 데이터 appending
        dbx.files_upload_session_append_v2(chunk, cursor)
        cursor.offset = large_file.tell()
logger.warning('대용량 파일(200MB) 업로드 완료')

# 액세스 토큰 폴더 내 존재하는 폴더/파일 출력
logger.warning('대용량 파일 업로드 후 폴더/파일 목록:')
for entry in dbx.files_list_folder('').entries:
    logger.warning("\t" + entry.name)

# 파일(폴더) 삭제 예시
# https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html?highlight=files_delete#dropbox.dropbox.Dropbox.files_delete
dbx.files_delete('/small_file_testing')
dbx.files_delete('/large_file_testing')
logger.warning('폴더 삭제 완료')

# 액세스 토큰 폴더 내 존재하는 폴더/파일 출력
logger.warning('테스트 폴더들 삭제 후 폴더/파일 목록:')
for entry in dbx.files_list_folder('').entries:
    logger.warning("\t" + entry.name)
