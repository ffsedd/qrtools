import pytest

from qrtools.generator import (
    normalize_input,
    filename_from_text,
    make_qr,
    QRConfig,
)


def test_normalize_empty():
    with pytest.raises(ValueError):
        normalize_input("   ")


def test_normalize_url_fix():
    assert normalize_input("https:/web.com") == "https://web.com"
    assert normalize_input("http:/web.com") == "http://web.com"


def test_normalize_add_scheme():
    assert normalize_input("example.com") == "https://example.com"


def test_filename_url():
    name = filename_from_text("https://web.com/path")
    assert name == "web.com.png"


def test_filename_fallback_hash():
    name = filename_from_text("some random payload")
    assert name.startswith("qr_")
    assert name.endswith(".png")


def test_make_qr_returns_image():
    img = make_qr("hello world", QRConfig())
    assert img is not None
    assert img.mode == "RGB"
    assert img.size[0] > 0 and img.size[1] > 0


def test_make_qr_deterministic_size():
    img = make_qr("hello world", QRConfig(size=512))
    assert img.size[0] == img.size[1]
