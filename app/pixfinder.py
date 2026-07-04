# -*- coding: utf-8 -*-
import os


# ==========================================================
# CLASS IMPLEMENTATIONS
# ==========================================================
class PixFinder:
    """
    디렉터리에서 pix 파일 경로를 수집
    """
    def find(self, path, recursive=False) -> list[str]:
        files = []
        self._scan(path, recursive, files)
        return files

    def _scan(self, path, recursive, files):
        # DirEntry는 is_dir() 결과를 캐싱해서 stat() 재호출 없음
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    if recursive:
                        self._scan(entry.path, recursive, files)
                else:
                    files.append(entry.path)
