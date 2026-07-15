# pixsort

Take timestamp information from pix(image and video) files, and rename them by using timestamp information.  Timestamp can be extracted from:
 1) file name
 2) exif (if present)
 3) file stat

## Requirements
- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

## Usage

### CLI
```bash
./pixsort run -i <디렉터리> [-r] [-u] [-w N] [-a]
```

옵션:
- `-i, --in`: 대상 디렉터리
- `-r, --recursive`: 서브디렉터리 재귀 탐색
- `-u, --uppercase`: 대문자로 리네이밍
- `-w, --workers`: 워커 스레드 수 (최대 8)
- `-a, --apply`: 실제 적용 (없으면 preview 모드)

`-a` 없이 실행하면 preview 모드로 동작하며, 실제 적용 시 실행 디렉터리에 `history-<타임스탬프>.sh` 이력 스크립트가 생성되어 되돌릴 수 있습니다 (`bash history-*.sh undo`).

### GUI
```bash
./pixsort gui
```
CustomTkinter 기반 창이 열립니다. 대상 디렉터리를 선택하고 옵션(재귀 탐색, 대문자 변환, 워커 수)을 지정한 뒤 "미리보기" 또는 "적용" 버튼을 누르면, CLI와 동일한 처리 결과가 창 안의 콘솔 영역에 표시됩니다.
