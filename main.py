#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging
import logging.config
from typing import Annotated

import yaml
import typer

from app.pixsort import PixSorter


logger = logging.getLogger(__name__)

app = typer.Typer(
    help="이미지/동영상 파일을 타임스탬프 기반으로 리네이밍하는 도구",
    add_completion=False,
)


def _setup_logging():
    if os.path.exists("resources/logging.conf"):
        with open("resources/logging.conf", "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        log_dir = os.path.split(config["handlers"]["logfile"]["filename"])[0]
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)


@app.command("run")
def run_cmd(
    in_dir: Annotated[str, typer.Option("--in", "-i", help="이미지/동영상 파일이 있는 디렉터리")],
    recursive: Annotated[bool, typer.Option("--recursive", "-r", help="서브디렉터리 재귀 탐색")] = False,
    uppercase: Annotated[bool, typer.Option("--uppercase", "-u", help="대문자로 리네이밍")] = False,
    num_workers: Annotated[int, typer.Option("--workers", "-w", help="워커 스레드 수 (최대 8)")] = 1,
    apply: Annotated[bool, typer.Option("--apply", "-a", help="실제 적용 (없으면 preview 모드)")] = False,
    suffix: Annotated[str, typer.Option("--suffix", "-s", help="파일명 끝(확장자 앞)에 추가할 접미사")] = "",
):
    """이미지/동영상 파일을 타임스탬프 기반으로 리네이밍"""
    _setup_logging()
    logger.info(
        f"in_dir={in_dir}, recursive={recursive}, uppercase={uppercase}, "
        f"workers={num_workers}, apply={apply}, suffix={suffix}"
    )
    logger.info("<< Start Pixsort >>")

    sorter = PixSorter()
    sorter.set_options(
        recursive=recursive,
        uppercase=uppercase,
        num_workers=num_workers,
        apply=apply,
        suffix=suffix,
    )
    sorter.run(in_dir)


@app.command("gui")
def gui_cmd():
    """GUI 모드 실행"""
    from app.pixgui import launch

    launch()


if __name__ == "__main__":
    app()
