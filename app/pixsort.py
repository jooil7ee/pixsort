# -*- coding: utf-8 -*-
import re
import logging
import os.path
import exifread
from datetime import datetime

from app.pixfinder import PixFinder
from app.pixinspector import PixInspector
from app.pixtype import PX_TYPE, PixTypeMapper
from app.pixrenamer import PixRenamer
from app.pixstamp import STAMP_STYLE, TSINFO_TYPE, PixStamp


# ===========================================================
# GLOBAL VARIABLES
# ===========================================================
logger = logging.getLogger(__name__)


# ===========================================================
# SYMBOLIC CONSTANTS
# ===========================================================
# 파일 이름 패턴 (정규식)
NAME_PATTERNS = (
    # 표준 스탬프 형식
    (re.compile(r"^(?:img|mov)_(\d{8})_(\d{6})_(\d{3,6})\.\w+", re.IGNORECASE),
     TSINFO_TYPE.STANDARD),

    # 날짜/시간 기반 파일명 (마이크로초 포함)
    (re.compile(r"[a-z_]*(\d{8})[-_]?(\d{6})[-_]?(\d{0,3})\w*\.\w+", re.IGNORECASE),
     TSINFO_TYPE.STANDARD),

    (re.compile(r"[a-z_]*(\d{8})[-_]?(\d{6})[-_]?(\d{0,3})\W+.*\.\w+", re.IGNORECASE),
     TSINFO_TYPE.STANDARD),

    # 날짜/시간 구조체 형식 (macOS 스크린샷 등)
    (re.compile(r"[a-z_]*(\d{4})-?(\d{2})-?(\d{2})[ \w]*(\d{1,2})\.(\d{2})\.(\d{2}).*\.\w+",
                re.IGNORECASE),
     TSINFO_TYPE.TIMESTRUCT),

    # UNIX epoch 초
    (re.compile(r"(\d{10})\w*\.\w+", re.IGNORECASE), TSINFO_TYPE.EPOCH_SECS),
)


# ===========================================================
# CLASS IMPLEMENTATIONS
# ===========================================================
class PixSorter:
    """
    타임스탬프 기반 미디어 파일 소터
    """
    def __init__(self):
        self.opts = {
            'style': STAMP_STYLE.STANDARD,
            'num_workers': 1,
            'recursive': False,
            'uppercase': False,
            'apply': False,
            'suffix': '',
        }

    def set_options(self, **kwargs):
        for (k, v) in kwargs.items():
            self.opts[k] = v

    def run(self, in_dir):
        """
        주어진 디렉터리의 pix 파일 리네이밍
        """
        if not os.path.exists(in_dir):
            logger.error(f"입력 디렉터리가 존재하지 않습니다: {in_dir}")
            return

        num_workers = self.opts['num_workers']

        # 1단계: 파일 탐색 (단일 쓰레드)
        pix_files = PixFinder().find(in_dir, self.opts['recursive'])
        logger.info(f"{in_dir}: {len(pix_files)}개 파일 검사 중 (workers={num_workers})")

        # 2단계: 타임스탬프 검사 (병렬)
        results = PixInspector(num_workers).run(pix_files, self.__inspect)

        # 3단계: 리네이밍 (병렬)
        workers = PixRenamer(num_workers)
        for stamp, path in results:
            workers.add_work(stamp, path)
        workers.start(self.opts['uppercase'], self.opts['apply'], self.opts['suffix'])
        workers.close()

        logger.info("완료")

    def __inspect(self, pix_path) -> "PixStamp | None":
        """
        파일에서 타임스탬프 정보를 추출한다.
         - R1: 파일명 패턴 매칭
         - R2: EXIF 정보 (JPEG, TIFF)
         - R3: 파일 수정 시간 (st_mtime)
        """
        pix_type = PixTypeMapper.map(pix_path)
        *_, pix_name = os.path.split(pix_path)

        if pix_type is not PX_TYPE.UNKNOWN:
            style = self.opts['style'].fmt

            # R1: 파일명 패턴
            for p, tsi_type in NAME_PATTERNS:
                m = p.match(pix_name)
                if m:
                    return PixStamp.new(style, tsi_type, m.groups(), pix_type, "R1")

            # R2: EXIF 정보
            if pix_type in [PX_TYPE.JPG, PX_TYPE.TIF]:
                with open(pix_path, "rb") as f:
                    exif = exifread.process_file(f)
                if "EXIF DateTimeOriginal" in exif:
                    dt_obj = datetime.strptime(
                        exif["EXIF DateTimeOriginal"].values, "%Y:%m:%d %H:%M:%S")
                    return PixStamp.new(style, TSINFO_TYPE.DATETIME_OBJ, dt_obj, pix_type, "R2")

            # R3: 파일 수정 시간
            stat = os.stat(pix_path)
            if stat.st_mtime > 0:
                return PixStamp.new(style, TSINFO_TYPE.EPOCH_SECS, int(stat.st_mtime), pix_type, "R3")

        logger.error(f"타임스탬프 추출 실패: {pix_name}")
        return None
