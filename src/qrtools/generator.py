from __future__ import annotations

import argparse
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import qrcode
from PIL import Image


@dataclass(frozen=True, slots=True)
class QRConfig:
    box_size: int = 10
    border: int = 4
    size: int = 512

    def __post_init__(self) -> None:
        if self.box_size <= 0:
            raise ValueError("box_size must be > 0")
        if self.border < 0:
            raise ValueError("border must be >= 0")
        if self.size <= 0:
            raise ValueError("size must be > 0")


_URL_FIX_RE = re.compile(r"^(https?):/(?!/)")


def normalize_input(text: str) -> str:
    text = text.strip()

    if not text:
        raise ValueError("Empty input")

    text = _URL_FIX_RE.sub(r"\1://", text)

    if "://" not in text and "." in text and " " not in text:
        text = "https://" + text

    return text


def filename_from_text(text: str) -> str:
    parsed = urlparse(text)
    host = parsed.netloc.split(":")[0]

    if host:
        return f"{host}.png"

    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f"qr_{digest}.png"


def make_qr(text: str, cfg: QRConfig) -> Image.Image:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=cfg.box_size,
        border=cfg.border,
    )

    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    # qrcode returns mode "1"; expose stable RGB API
    img = img.convert("RGB")

    if img.size != (cfg.size, cfg.size):
        img = img.resize(
            (cfg.size, cfg.size),
            Image.Resampling.NEAREST,
        )

    return img


def save_qr(img: Image.Image, path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    img.save(output, format="PNG", optimize=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qr",
        description="Generate QR codes from arbitrary text",
    )

    parser.add_argument(
        "text",
        help="Payload (URL, text, JSON, device ID, etc.)",
    )

    parser.add_argument(
        "-o",
        "--out",
        default=None,
        help="Output PNG path",
    )

    parser.add_argument(
        "--size",
        type=int,
        default=512,
        help="Output image size",
    )

    parser.add_argument(
        "--border",
        type=int,
        default=1,
        help="QR quiet zone size",
    )

    parser.add_argument(
        "--box-size",
        type=int,
        default=10,
        help="QR module size",
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    payload = normalize_input(args.text)

    output = args.out or filename_from_text(payload)

    cfg = QRConfig(
        size=args.size,
        border=args.border,
        box_size=args.box_size,
    )

    img = make_qr(payload, cfg)
    save_qr(img, output)

    print(output)


if __name__ == "__main__":
    main()
