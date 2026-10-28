import pytest
from pathlib import Path
from capture_core import CaptureOptions, find_chrome_path, is_chrome_debug_running

def test_capture_options_defaults():
    opts = CaptureOptions()
    assert opts.full_page is True
    assert opts.delay_seconds == 1.0
    assert opts.viewport_width == 1920
    assert opts.viewport_height == 1080
    assert opts.timeout_ms == 30000
    assert opts.use_cdp is False
    assert opts.cdp_port == 9222

def test_find_chrome_path():
    chrome = find_chrome_path()
    assert chrome is not None
    assert chrome.exists()
    assert chrome.name.lower() == "chrome.exe"

def test_is_chrome_debug_running_not_running():
    # 임의의 안 쓰는 포트에서 False 리턴 확인
    assert is_chrome_debug_running(port=59123) is False
