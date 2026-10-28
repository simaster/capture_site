# 웹사이트 화면 자동 캡처 프로그램 개발 작업 보고서 (work.md)

## 1. 프로젝트 개요 및 배경

- **프로젝트명**: 웹사이트 화면 자동 캡처 GUI 도구 (Web Capture Tool)
- **작업 일시**: 2026-10-28
- **목적**: 
  - URL 목록 텍스트 파일(예: `web site.txt`)을 읽어 여러 웹페이지를 순차적으로 고화질 `.png` 이미지로 자동 캡처하여 지정 폴더에 저장
  - 기존 CLI 스크립트(`capture_sites.py`)의 한계 극복: 직관적인 GUI 인터페이스, 윈도우 환경 실행 편의성 제공
  - 인트라넷/그룹웨어(`doto.kr`) 등 **로그인 인증이 필수적인 보안 사이트**의 정상 캡처 지원

---

## 2. 개발 아키텍처 및 주요 모듈 구성

단일 책임 원칙(SRP)과 멀티스레드 안전성을 적용하여 3개 핵심 계층으로 모듈화하였습니다.

```
┌────────────────────────────────────────────────────────┐
│             Presentation Layer (gui_app.py)            │
│  - CustomTkinter 기반 다크/라이트 모던 GUI              │
│  - URL 파일 및 저장 폴더 탐색기 다이얼로그             │
│  - [1. 로그인용 크롬 열기] / [2. 캡처 시작] 버튼       │
│  - 실시간 프로그레스 바, 로그 창, 작업 중단 제어       │
└───────────────────────────┬────────────────────────────┘
                            │ Queue & Thread Callback
┌───────────────────────────▼────────────────────────────┐
│               Service Layer (capture_core.py)          │
│  - Chrome Remote Debugging (CDP, 포트 9222) 연동       │
│  - Playwright 헤드리스 엔진 및 세션 관리자             │
│  - 풀페이지 스크롤 캡처 및 추가 렌더링 대기 처리       │
│  - 로그인 리다이렉트 자동 감지 및 경고 로깅            │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│                Utility Layer (utils.py)                │
│  - URL 목록 정제 (빈 줄, 주석, 헤더 필터링)            │
│  - Windows 파일시스템 금지 특수문자 안전 치환          │
│  - 동일 파일명 충돌 방지 인덱싱 (_1, _2 ...)           │
└────────────────────────────────────────────────────────┘
```

---

## 3. 주요 구현 파일 목록

| 파일명 | 파일 설명 |
|---|---|
| [`gui_app.py`](file:///c:/CODE/execise/capture_site/gui_app.py) | CustomTkinter 기반 메인 GUI 프로그램 (멀티스레드 UI 무응답 방지, 실시간 로그) |
| [`capture_core.py`](file:///c:/CODE/execise/capture_site/capture_core.py) | Playwright 캡처 엔진 및 Google Chrome CDP 원격 디버깅(포트 9222) 연동 로직 |
| [`utils.py`](file:///c:/CODE/execise/capture_site/utils.py) | URL 파싱, 필터링 및 Windows 파일시스템 안전 파일명 생성기 |
| [`run.py`](file:///c:/CODE/execise/capture_site/run.py) | 파이썬 메인 런처 스크립트 |
| [`run.bat`](file:///c:/CODE/execise/capture_site/run.bat) | 윈도우 원클릭 실행 배치 파일 (CP949 인코딩 충돌 방지 및 경로 자동 이동) |
| [`requirements.txt`](file:///c:/CODE/execise/capture_site/requirements.txt) | 의존성 패키지 명세 (`customtkinter`, `playwright`, `pytest`) |
| [`tests/`](file:///c:/CODE/execise/capture_site/tests/) | 단위 및 실제 브라우저 통합 테스트 스위트 (총 7개 테스트 100% 통과) |
| [`docs/superpowers/`](file:///c:/CODE/execise/capture_site/docs/superpowers/) | 세부 설계 사양서(Spec) 및 단계별 구현 계획서(Implementation Plan) |

---

## 4. 핵심 트러블슈팅 및 문제 해결 내역

### 4.1 로그인 화면(`/login`)만 반복 캡처되던 현상 해결
- **문제 현상**: 모든 URL 캡처 결과물이 동일한 로그인 페이지(약 25KB)로 저장됨.
- **원인 규명**: 
  - `doto.kr`의 내부 페이지들은 인증이 없으면 서버에서 자동으로 `https://doto.kr/login`으로 302 리다이렉트함.
  - Playwright는 일반 브라우저와 분리된 시크릿 모드로 실행되므로, 기존 크롬에 로그인되어 있어도 쿠키가 공유되지 않음.
- **해결 조치**: 
  - **방법 1 (Chrome CDP 원격 디버깅 연동)** 적용: 사용자의 실제 Google Chrome을 디버깅 포트(9222)로 띄워, 사용자가 이미 로그인한 크롬의 탭과 세션을 Playwright가 그대로 공유받아 캡처하도록 구현.

### 4.2 `run.bat` 더블 클릭 시 실행 실패(창 꺼짐) 문제 해결
- **문제 현상**: `run.bat` 실행 시 `'Capture' is not recognized...`, `'vel' is not recognized...` 에러 발생 후 즉시 종료.
- **원인 규명**: 윈도우 `cmd.exe`가 기본 CP949 인코딩으로 배치 파일을 읽을 때, UTF-8 한글 텍스트 및 괄호 `()` 구문을 명령어로 오인함.
- **해결 조치**: 배치 파일 내부의 텍스트를 영문 ASCII로 표준화하고, `cd /d "%~dp0"` 및 파이썬 절대 경로 탐색기를 추가하여 더블 클릭 시 즉각 실행되도록 수정.

### 4.3 URL 파일 고정 여부 질의 대응
- `web site.txt`는 프로그램 최초 구동 시 편의를 위한 기본값이며, 상단 `[파일 찾기]` 버튼으로 어떤 파일이든 선택 가능하도록 설계되었음을 확인 및 안내.

---

## 5. 품질 검증 및 테스트 결과

`pytest tests/ -v` 실행 결과, **7개 테스트 전원 통과 (100% Pass)**:
- `test_capture_options_defaults`: 캡처 옵션 기본값 검증 PASS
- `test_find_chrome_path`: Chrome 실행 파일 경로 검색 PASS
- `test_is_chrome_debug_running_not_running`: 디버그 포트 상태 감지 PASS
- `test_single_url_capture`: 실제 Playwright 브라우저 캡처 동작 PASS
- `test_clean_url_list`: 유효 URL 필터링/정제 PASS
- `test_sanitize_filename_from_url`: URL -> 안전 파일명 치환 PASS
- `test_sanitize_filename_duplicate_handling`: 중복 파일명 인덱싱 PASS
