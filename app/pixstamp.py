# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from enum import Enum


# ===========================================================
# GLOBAL VARIABLES
# ===========================================================
logger = logging.getLogger(__name__)


# ===========================================================
# DATA TYPES
# ===========================================================
class TSINFO_TYPE(Enum):
    """
    타임스탬프 정보 유형
    """
    UNKNOWN = 0         # 알 수 없음
    STANDARD = 1        # 날짜/시간: (yyyymmdd, HHMMSS, msec)
    TIMESTRUCT = 2      # 날짜/시간: (yyyy, mm, dd, HH, MM, SS)
    EPOCH_SECS = 3      # UNIX epoch 초
    DATETIME_OBJ = 4    # datetime 객체


class STAMP_STYLE(Enum):
    """
    Pix 스탬프 출력 형식
    """
    STANDARD = "%Y%m%d_%H%M%S_%f"
    EPOCH_SECS = "%s_%f"

    def __init__(self, fmt):
        self.fmt = fmt


# ===========================================================
# CLASS IMPLEMENTATIONS
# ===========================================================
class PixStamp:
    """
    pix 파일의 타임스탬프 스탬프
    """
    def __init__(self, fmt, stamp, desc=""):
        self.fmt = fmt
        self.stamp = stamp
        self.desc = desc

    def __str__(self):
        return f"{self.fmt}/{self.stamp}"

    @staticmethod
    def new(style, tsi_type, tsi_data, pix_type, desc="") -> "PixStamp | None":
        """
        타임스탬프 정보로 PixStamp 객체 생성
        """
        dt = None

        try:
            if TSINFO_TYPE.STANDARD == tsi_type:
                date_s, time_s, usec_s = tsi_data
                usec_s = (usec_s + "000")[:3]
                dt = datetime.strptime(f"{date_s}_{time_s}.{usec_s}", "%Y%m%d_%H%M%S.%f")

            elif TSINFO_TYPE.TIMESTRUCT == tsi_type:
                dt = datetime(*list(map(int, tsi_data)))

            elif TSINFO_TYPE.EPOCH_SECS == tsi_type:
                sec_s = tsi_data[0] if isinstance(tsi_data, (list, tuple)) else tsi_data
                dt = datetime.fromtimestamp(int(sec_s))

            elif TSINFO_TYPE.DATETIME_OBJ == tsi_type:
                dt = tsi_data

            else:
                logger.error(f"지원하지 않는 TSI 유형: {tsi_type}")

            if dt is not None:
                stamp_s = "%s_%s" % (pix_type.cls, dt.strftime(style)[:-3])
                return PixStamp(pix_type.fmt, stamp_s, desc)

        except ValueError:
            logger.error(f"유효하지 않은 TSI 데이터: {tsi_data}")

        return None


class PixStampGroup:
    """
    동일 타임스탬프를 가진 pix 파일 그룹
    """
    def __init__(self, fmt, stamp, path=None):
        self.fmt = fmt
        self.stamp = stamp
        self.paths = [path] if path else []

    def key(self):
        return f"{self.fmt}/{self.stamp}"

    def add_path(self, path):
        self.paths.append(path)

    def sort_paths(self):
        self.paths.sort()

    def __str__(self):
        return f"{self.fmt}/{self.stamp}: {self.paths}"
