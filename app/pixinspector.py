# -*- coding: utf-8 -*-
import os
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed


# ===========================================================
# GLOBAL VARIABLES
# ===========================================================
logger = logging.getLogger(__name__)


# ===========================================================
# CLASS IMPLEMENTATIONS
# ===========================================================
class PixInspector:
    """
    pix 파일 타임스탬프 병렬 검사기
    """
    def __init__(self, num_workers):
        self.num_workers = num_workers

    def run(self, pix_files, inspect_fn) -> list[tuple]:
        """
        pix_files를 병렬로 검사해서 (stamp, path) 쌍 목록 반환
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            future_to_path = {executor.submit(inspect_fn, p): p for p in pix_files}
            for future in as_completed(future_to_path):
                path = future_to_path[future]
                stamp = future.result()
                if stamp is not None:
                    logger.info(f" * {stamp} ({stamp.desc}) <-- {os.path.split(path)[-1]}")
                    results.append((stamp, path))

        return results
