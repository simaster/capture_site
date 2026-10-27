import sys
from pathlib import Path

# 프로젝트 루트 경로를 sys.path에 추가하여 모듈 임포트 보장
root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
