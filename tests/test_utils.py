import pytest
from utils import clean_url_list, sanitize_filename_from_url

def test_clean_url_list():
    raw_lines = [
        "web site",
        "",
        "   ",
        "# 주석 라인",
        "https://doto.kr/dashboard",
        "http://example.com/test   ",
        "invalid-url-string"
    ]
    cleaned = clean_url_list(raw_lines)
    assert cleaned == [
        "https://doto.kr/dashboard",
        "http://example.com/test"
    ]

def test_sanitize_filename_from_url():
    # 기본 경로 변환
    assert sanitize_filename_from_url("https://doto.kr/dashboard") == "dashboard.png"
    # 하위 경로 및 특수문자 변환
    assert sanitize_filename_from_url("https://doto.kr/crm/contacts") == "crm_contacts.png"
    # 메인/루트 도메인 처리
    assert sanitize_filename_from_url("https://doto.kr/") == "main.png"
    assert sanitize_filename_from_url("https://doto.kr") == "main.png"
    # 윈도우 금지 특수문자 치환 (: ? * 등)
    assert sanitize_filename_from_url("https://doto.kr/search?q=test*value") == "search_q_test_value.png"

def test_sanitize_filename_duplicate_handling():
    existing = {"dashboard.png"}
    # 중복 시 _1 접미사 추가 확인
    assert sanitize_filename_from_url("https://doto.kr/dashboard", existing_names=existing) == "dashboard_1.png"
