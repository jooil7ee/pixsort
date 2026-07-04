# -*- coding: utf-8 -*-
import logging
from enum import Enum
from dataclasses import dataclass
from PIL import Image, UnidentifiedImageError


# ===========================================================
# GLOBAL VARIABLES
# ===========================================================
logger = logging.getLogger(__name__)


# ==========================================================
# DATA TYPES
# ==========================================================
@dataclass
class PX_CLS:
    """
    pix 파일 분류
    """
    IMAGE: str = "img"
    VIDEO: str = "mov"


class PX_TYPE(Enum):
    """
    pix 파일 형식
    """
    UNKNOWN = (None, None)
    JPG = ("jpg", PX_CLS.IMAGE)
    TIF = ("tif", PX_CLS.IMAGE)
    PNG = ("png", PX_CLS.IMAGE)
    MP4 = ("mp4", PX_CLS.VIDEO)
    MOV = ("mov", PX_CLS.VIDEO)

    def __init__(self, fmt, cls):
        self.fmt = fmt
        self.cls = cls


# ==========================================================
# CLASS IMPLEMENTATIONS
# ==========================================================
class PixTypeMapper:
    """
    파일 확장자 → 미디어 타입 매핑
    """
    type_map = {
        "jpg": PX_TYPE.JPG,
        "jpeg": PX_TYPE.JPG,
        "mpo": PX_TYPE.JPG,
        "tif": PX_TYPE.TIF,
        "tiff": PX_TYPE.TIF,
        "png": PX_TYPE.PNG,
        "mp4": PX_TYPE.MP4,
        "mov": PX_TYPE.MOV,
    }

    def __new__(cls, *args, **kwargs):
        raise RuntimeError('%s should not be instantiated' % cls)

    @classmethod
    def map(cls, pix_path) -> PX_TYPE:
        try:
            fmt = Image.open(pix_path).format.lower()
        except UnidentifiedImageError:
            *_, fmt = pix_path.lower().split(".")
        except FileNotFoundError:
            logger.error(f"파일을 찾을 수 없습니다: {pix_path}")
            return PX_TYPE.UNKNOWN

        return cls.type_map.get(fmt, PX_TYPE.UNKNOWN)
