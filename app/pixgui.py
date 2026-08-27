# -*- coding: utf-8 -*-
"""PixSort GUI (CustomTkinter)"""
import sys
import queue
import logging
import threading
from tkinter import filedialog

import customtkinter as ctk

from app.pixsort import PixSorter


# ===========================================================
# GLOBAL VARIABLES
# ===========================================================
logger = logging.getLogger(__name__)

_DONE = object()


# ===========================================================
# CLASS IMPLEMENTATIONS
# ===========================================================
class _QueueLogHandler(logging.Handler):
    """로그 레코드를 큐에 전달하는 핸들러"""

    def __init__(self, out_queue):
        super().__init__()
        self.out_queue = out_queue

    def emit(self, record):
        self.out_queue.put(self.format(record) + "\n")


class _QueueStdout:
    """print() 출력을 큐로 전달하는 stdout 대체 객체 (preview 모드가 print를 사용하기 때문)"""

    def __init__(self, out_queue):
        self.out_queue = out_queue

    def write(self, text):
        if text:
            self.out_queue.put(text)

    def flush(self):
        pass


class PixGuiApp(ctk.CTk):
    """PixSort GUI 메인 윈도우"""

    def __init__(self):
        super().__init__()

        self.title("pixsort")
        self.geometry("720x560")

        self.out_queue = queue.Queue()
        self.worker = None

        self._build_widgets()
        self._poll_queue()

    def _build_widgets(self):
        # 디렉터리 선택
        dir_frame = ctk.CTkFrame(self)
        dir_frame.pack(fill="x", padx=12, pady=(12, 6))

        self.dir_entry = ctk.CTkEntry(dir_frame, placeholder_text="대상 디렉터리")
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(dir_frame, text="찾아보기", width=90, command=self._browse_dir).pack(side="left")

        # 옵션
        opt_frame = ctk.CTkFrame(self)
        opt_frame.pack(fill="x", padx=12, pady=6)

        self.recursive_var = ctk.BooleanVar(value=False)
        self.uppercase_var = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(
            opt_frame, text="재귀 탐색", variable=self.recursive_var
        ).pack(side="left", padx=(0, 12))
        ctk.CTkCheckBox(
            opt_frame, text="대문자로 리네이밍", variable=self.uppercase_var
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(opt_frame, text="워커 수").pack(side="left", padx=(12, 4))
        self.workers_var = ctk.StringVar(value="4")
        ctk.CTkEntry(opt_frame, textvariable=self.workers_var, width=50).pack(side="left")

        ctk.CTkLabel(opt_frame, text="접미사").pack(side="left", padx=(12, 4))
        self.suffix_var = ctk.StringVar(value="")
        ctk.CTkEntry(opt_frame, textvariable=self.suffix_var, width=100).pack(side="left")

        # 실행 버튼
        run_frame = ctk.CTkFrame(self)
        run_frame.pack(fill="x", padx=12, pady=6)

        self.preview_btn = ctk.CTkButton(
            run_frame, text="미리보기", command=lambda: self._run(apply=False)
        )
        self.preview_btn.pack(side="left", padx=(0, 6))

        self.apply_btn = ctk.CTkButton(
            run_frame, text="적용", fg_color="#b03a2e", hover_color="#902d23",
            command=lambda: self._run(apply=True),
        )
        self.apply_btn.pack(side="left")

        # 콘솔 출력
        self.console = ctk.CTkTextbox(self, wrap="none", font=("Menlo", 12))
        self.console.pack(fill="both", expand=True, padx=12, pady=(6, 12))
        self.console.configure(state="disabled")

    def _browse_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, path)

    def _run(self, apply):
        if self.worker and self.worker.is_alive():
            return

        in_dir = self.dir_entry.get().strip()
        if not in_dir:
            self._append_console("대상 디렉터리를 선택하세요.\n")
            return

        try:
            num_workers = int(self.workers_var.get())
        except ValueError:
            num_workers = 1

        self._set_running(True)
        self._clear_console()

        self.worker = threading.Thread(
            target=self._run_sorter,
            args=(
                in_dir, self.recursive_var.get(), self.uppercase_var.get(),
                num_workers, apply, self.suffix_var.get(),
            ),
            daemon=True,
        )
        self.worker.start()

    def _run_sorter(self, in_dir, recursive, uppercase, num_workers, apply, suffix):
        """백그라운드 스레드에서 PixSorter 실행. 로그/print를 큐로 리다이렉트."""
        handler = _QueueLogHandler(self.out_queue)
        handler.setFormatter(logging.Formatter("%(message)s"))
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)

        stdout_backup = sys.stdout
        sys.stdout = _QueueStdout(self.out_queue)

        try:
            sorter = PixSorter()
            sorter.set_options(
                recursive=recursive,
                uppercase=uppercase,
                num_workers=num_workers,
                apply=apply,
                suffix=suffix,
            )
            sorter.run(in_dir)
        except Exception as e:
            self.out_queue.put(f"오류 발생: {e}\n")
        finally:
            sys.stdout = stdout_backup
            root_logger.removeHandler(handler)
            self.out_queue.put(_DONE)

    def _poll_queue(self):
        try:
            while True:
                item = self.out_queue.get_nowait()
                if item is _DONE:
                    self._set_running(False)
                else:
                    self._append_console(item)
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)

    def _append_console(self, text):
        self.console.configure(state="normal")
        self.console.insert("end", text)
        self.console.see("end")
        self.console.configure(state="disabled")

    def _clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    def _set_running(self, running):
        state = "disabled" if running else "normal"
        self.preview_btn.configure(state=state)
        self.apply_btn.configure(state=state)


def launch():
    """GUI 실행 진입점"""
    ctk.set_appearance_mode("system")
    app = PixGuiApp()
    app.mainloop()
