import pytest
from pathlib import Path
from capture_core import CaptureOptions

def test_capture_options_defaults():
    opts = CaptureOptions()
    assert opts.full_page is True
    assert opts.delay_seconds == 1.0
    assert opts.viewport_width == 1920
    assert opts.viewport_height == 1080
    assert opts.timeout_ms == 30000
