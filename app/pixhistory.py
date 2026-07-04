# -*- coding: utf-8 -*-
import time
import logging
import os.path
from threading import Lock as WriteLock


# ===========================================================
# GLOBAL VARIABLES
# ===========================================================
logger = logging.getLogger(__name__)


# ===========================================================
# SYMBOLIC CONSTANTS
# ===========================================================
HEADER = """#!/bin/bash

if [[ "$#" == 1 && "$1" == "do" ]]; then
  pixwork() { mv -fv "$1" "$2"; }
elif [[ "$#" == 1 && "$1" == "undo" ]]; then
  pixwork() { mv -fv "$2" "$1"; }
else
  echo "Usage: $0 {do|undo}"; exit 0
fi

"""


# ===========================================================
# CLASS IMPLEMENTATIONS
# ===========================================================
class PixHistory:
    """
    리네이밍 이력 기록기 (do/undo 가능한 shell 스크립트 생성)
    """

    def __init__(self, history_dir="."):
        if not os.path.exists(history_dir):
            os.mkdir(history_dir)

        history_file = "history-%s.sh" % time.strftime("%Y%m%d-%H%M%S", time.localtime())

        try:
            self.history = open(os.path.join(history_dir, history_file), "w")
        except Exception:
            logger.error(f"히스토리 파일 생성 실패: {history_dir}")
            self.history = open(history_file, "w")

        self.history.write(HEADER)
        self.lock = WriteLock()

        logger.info(f"히스토리 기록 시작: {history_file}")

    def close(self):
        with self.lock:
            if self.history:
                self.history.close()
                self.history = None

    def writeline(self, from_path, to_path):
        with self.lock:
            if not self.history:
                return
            try:
                self.history.write(f"pixwork '{from_path}' '{to_path}'\n")
            except Exception:
                logger.error("히스토리 라인 기록 실패")
