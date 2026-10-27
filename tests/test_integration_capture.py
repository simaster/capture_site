import pytest
from pathlib import Path
from capture_core import CaptureOptions, capture_urls

def test_single_url_capture(tmp_path):
    output_dir = tmp_path / "captures"
    options = CaptureOptions(
        full_page=False,
        delay_seconds=0.5,
        viewport_width=1280,
        viewport_height=720,
        timeout_ms=15000
    )
    urls = ["https://example.com"]
    logs = []
    progress_calls = []

    results = capture_urls(
        urls=urls,
        output_dir=output_dir,
        options=options,
        on_progress=lambda idx, total, url: progress_calls.append((idx, total, url)),
        on_log=lambda msg: logs.append(msg)
    )

    assert results["total"] == 1
    assert results["success"] == 1
    assert results["failed"] == 0
    assert len(progress_calls) == 1

    # 생성된 파일 확인
    png_files = list(output_dir.glob("*.png"))
    assert len(png_files) == 1
    assert png_files[0].stat().st_size > 0
