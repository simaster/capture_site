import os
from pathlib import Path
from playwright.sync_api import sync_playwright

# 파일에서 웹사이트 목록 읽기
file_path = "web site.txt"
with open(file_path, "r", encoding="utf-8") as f:
    urls = [line.strip() for line in f if line.strip() and line.strip() != "web site"]

# 윈도우 기준 기본 다운로드 폴더 경로 설정 (사용자 환경에 맞게 수정 가능)
download_dir = Path.home() / "Downloads" / "doto_captures"
download_dir.mkdir(parents=True, exist_ok=True)

print(f"총 {len(urls)}개의 웹사이트 캡처를 시작합니다...")
print(f"저장 폴더: {download_dir}")

with sync_playwright() as p:
    # 브라우저 실행 (headless=False 로 설정하면 브라우저 동작 화면을 직접 볼 수 있습니다)
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for idx, url in enumerate(urls, 1):
        try:
            print(f"[{idx}/{len(urls)}] 접속 및 캡처 중: {url}")
            page.goto(url, timeout=30000)
            page.wait_for_load_state("networkidle") # 페이지 로딩 대기

            # URL 경로를 파일명으로 안전하게 변환 (예: https://doto.kr/dashboard -> dashboard.png)
            parsed_name = url.replace("https://doto.kr/", "").replace("/", "_")
            if not parsed_name:
                parsed_name = "main"
            
            save_path = download_dir / f"{parsed_name}.png"
            
            # 스크린샷 저장 (전체 페이지 캡처)
            page.screenshot(path=str(save_path), full_page=True)
            print(f"  └ 성공: {save_path.name}")
        except Exception as e:
            print(f"  └ 실패 ({url}): {e}")

    browser.close()

print("모든 캡처 작업이 완료되었습니다!")