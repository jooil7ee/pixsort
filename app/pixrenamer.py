# -*- coding: utf-8 -*-
import os.path
import logging
from threading import Thread
from collections import deque

from app.pixstamp import PixStampGroup
from app.pixhistory import PixHistory


# ===========================================================
# GLOBAL VARIABLES
# ===========================================================
logger = logging.getLogger(__name__)


# ===========================================================
# CLASS IMPLEMENTATIONS
# ===========================================================
class PixRenameQueue:
    """
    인덱스를 가진 단순 큐
    """
    def __init__(self, index=None):
        self.queue = deque()
        self.count = 0
        self.index = index if index is not None else {}

    def __del__(self):
        self.queue.clear()

    def empty(self):
        return not self.queue

    def push(self, elem):
        self.queue.append(elem)
        self.count += 1
        self.index[elem.key()] = elem

    def pop(self):
        if not self.queue:
            return None
        elem = self.queue.popleft()
        self.index.pop(elem.key())
        return elem


class PixRenamer:
    """
    병렬 리네이밍 실행기
    """
    worker_count_max = 8

    def __init__(self, num_workers=1):
        self.index = {}
        self.workq = []
        self.count = 0
        self.history = None

        self.num_workers = num_workers if 0 < num_workers <= self.worker_count_max else 1

        for _ in range(self.num_workers):
            self.workq.append(PixRenameQueue(index=self.index))

    def add_work(self, pixstamp, path):
        """
        리네이밍 작업 추가. 동일 타임스탬프이면 그룹에 병합.
        """
        key = f"{pixstamp.fmt}/{pixstamp.stamp}"

        if key not in self.index:
            next_queue = self.workq[self.count % self.num_workers]
            next_queue.push(PixStampGroup(pixstamp.fmt, pixstamp.stamp))
            self.count += 1

        psg = self.index[key]
        psg.add_path(path)
        return psg

    def start(self, uppercase, apply=False):
        """
        워커 스레드 시작
        """
        if apply:
            logger.info(f"{self.num_workers}개 워커 시작 (apply 모드, 히스토리 기록)")
            target = PixRenamer.__process
            self.history = PixHistory(".")
        else:
            logger.info(f"{self.num_workers}개 워커 시작 (preview 모드)")
            target = PixRenamer.__preview

        workers = []
        for i in range(self.num_workers):
            worker = Thread(target=target, args=(i, self.workq[i], self.history, uppercase))
            workers.append(worker)
            worker.start()

        for worker in workers:
            worker.join()

    def close(self):
        if self.history:
            self.history.close()

    @staticmethod
    def __process(tid, queue, history, uppercase):
        """
        실제 리네이밍 수행
        """
        while not queue.empty():
            psg = queue.pop()
            psg.sort_paths()

            for seq, from_path in enumerate(psg.paths):
                base, x = os.path.split(from_path)
                y = "%s%03d.%s" % (psg.stamp, seq, psg.fmt)

                if uppercase:
                    y = y.upper()

                if x == y:
                    logger.info(" [X] %-30s <-- %s (@%s)" % ("---", x, base))
                else:
                    logger.info(f" [A] {y} <-- {x} (@{base})")
                    to_path = os.path.join(base, y)
                    os.rename(from_path, to_path)
                    history.writeline(from_path, to_path)

    @staticmethod
    def __preview(tid, queue, history, uppercase):
        """
        리네이밍 미리보기 (실제 적용 없음)
        """
        while not queue.empty():
            psg = queue.pop()
            psg.sort_paths()

            for seq, from_path in enumerate(psg.paths):
                base, x = os.path.split(from_path)
                y = "%s%03d.%s" % (psg.stamp, seq, psg.fmt)

                if uppercase:
                    y = y.upper()

                if x == y:
                    print(" [X] %-30s <-- %s (@%s)" % ("---", x, base))
                else:
                    print(f" [P] {y} <-- {x} (@{base})")
