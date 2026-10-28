import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Set
from playwright.sync_api import sync_playwright
from utils import sanitize_filename_from_url

@dataclass
class CaptureOptions:
    full_page: bool = True
    delay_seconds: float = 1.0
    viewport_width: int = 1920
    viewport_height: int = 1080
    timeout_ms: int = 30000

def save_browser_session(
    start_url: str,
    session_file: Path,
    on_log: Optional[Callable[[str], None]] = None
) -> bool:
    """헤드풀 브라우저를 열어 사용자가 로그인하도록 유도한 후 실시간으로 storage_state.json 저장"""
    session_file.parent.mkdir(parents=True, exist_ok=True)
    logged_in = False

    def log(msg: str):
        if on_log:
            on_log(msg)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        log(f"브라우저를 열어 접속합니다: {start_url}")
        page.goto(start_url)
        log("열린 브라우저 창에서 아이디와 비밀번호를 입력하여 로그인해 주세요.")

        # 브라우저 창이 열려 있는 동안 페이지 상태 및 URL을 실시간 감시하며 세션 저장
        while True:
            try:
                if page.is_closed():
                    break
                current_url = page.url
                context.storage_state(path=str(session_file))

                # /login 페이지를 벗어나서 로그인 성공 페이지로 이동한 경우 감지
                if "/login" not in current_url and not logged_in:
                    logged_in = True
                    log(f"✅ 로그인 성공이 감지되었습니다! (현재 주소: {current_url})")
                    log("로그인 세션이 안전하게 저장되었습니다. 이제 브라우저 창을 닫으셔도 됩니다.")

                page.wait_for_timeout(500)
            except Exception:
                break

        try:
            context.close()
            browser.close()
        except Exception:
            pass

    return session_file.exists()

def capture_urls(
    urls: list[str],
    output_dir: Path,
    options: CaptureOptions,
    session_file: Optional[Path] = None,
    on_progress: Optional[Callable[[int, int, str], None]] = None,
    on_log: Optional[Callable[[str], None]] = None,
    is_stopped: Optional[Callable[[], bool]] = None
) -> dict:
    """지정된 URL 목록을 순회하며 스크린샷 캡처 수행"""
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {"total": len(urls), "success": 0, "failed": 0, "skipped": 0}
    existing_files: Set[str] = set()

    def log(msg: str):
        if on_log:
            on_log(msg)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context_kwargs = {
            "viewport": {"width": options.viewport_width, "height": options.viewport_height}
        }
        if session_file and session_file.exists():
            context_kwargs["storage_state"] = str(session_file)
            log(f"저장된 세션 파일({session_file.name})을 적용하여 브라우저를 구동합니다.")
        else:
            log("⚠️ 적용할 로그인 세션 파일이 없습니다. (공개 페이지만 정상 접근 가능)")

        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        for idx, url in enumerate(urls, 1):
            if is_stopped and is_stopped():
                log("사용자에 의해 작업이 중단되었습니다.")
                results["skipped"] = len(urls) - idx + 1
                break

            if on_progress:
                on_progress(idx, len(urls), url)

            log(f"[{idx}/{len(urls)}] 접속 시도: {url}")
            try:
                page.goto(url, timeout=options.timeout_ms)
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    # networkidle 타임아웃 시에도 domcontentloaded 기반으로 계속 진행
                    pass

                if options.delay_seconds > 0:
                    time.sleep(options.delay_seconds)

                current_url = page.url
                if "/login" in current_url and "/login" not in url:
                    log(f"  ⚠️ [로그인 필요 안내] '{url}' 접속 시 로그인 페이지({current_url})로 리다이렉트되었습니다.")
                    log("     → 먼저 상단의 [브라우저 로그인 및 세션 저장] 버튼을 눌러 로그인해 주세요.")

                filename = sanitize_filename_from_url(url, existing_names=existing_files)
                save_path = output_dir / filename

                page.screenshot(path=str(save_path), full_page=options.full_page)
                log(f"  └ 캡처 저장: {save_path.name}")
                results["success"] += 1
            except Exception as e:
                log(f"  └ 캡처 실패 ({url}): {e}")
                results["failed"] += 1

        context.close()
        browser.close()

    return results
