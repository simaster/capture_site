import re
from urllib.parse import urlparse

def clean_url_list(raw_lines: list[str]) -> list[str]:
    """텍스트 파일 라인 목록에서 유효한 HTTP/HTTPS URL만 필터링 및 정제"""
    valid_urls = []
    for line in raw_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.lower() in ("web site", "website", "url", "urls"):
            continue
        if stripped.startswith("http://") or stripped.startswith("https://"):
            valid_urls.append(stripped)
    return valid_urls

def sanitize_filename_from_url(url: str, existing_names: set[str] | None = None) -> str:
    """URL을 Windows에서 사용 가능한 안전한 .png 파일명으로 변환"""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    query = parsed.query.strip()

    parts = []
    if path:
        parts.append(path)
    if query:
        parts.append(query)

    base = "_".join(parts)
    if not base:
        base = "main"

    # 파일시스템 예약 및 특수문자 치환: \ / : * ? " < > | = &
    safe_base = re.sub(r'[\\/*?:"<>|=&]', '_', base)
    # 연속된 언더스코어 정리
    safe_base = re.sub(r'_+', '_', safe_base).strip('_.')

    if not safe_base:
        safe_base = "site"

    filename = f"{safe_base}.png"
    
    if existing_names is not None:
        counter = 1
        original_base = safe_base
        while filename in existing_names:
            filename = f"{original_base}_{counter}.png"
            counter += 1
        existing_names.add(filename)

    return filename
