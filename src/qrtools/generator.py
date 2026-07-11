from __future__ import annotations

import argparse
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import qrcode
from PIL import Image

# ----------------------------
# Config
# ----------------------------


@dataclass(frozen=True, slots=True)
class QRConfig:
    box_size: int = 10
    border: int = 4
    size: int = 512


# ----------------------------
# Normalization helpers
# ----------------------------


_URL_FIX_RE = re.compile(r"^(https?):/(?!/)")


def normalize_input(text: str) -> str:
    text = text.strip()
    if not text:
        raise ValueError("Empty input")

    # fix broken scheme like https:/example.com
    text = _URL_FIX_RE.sub(r"\1://", text)

    # if it looks like a bare domain, optionally upgrade to URL
    if "://" not in text and "." in text and " " not in text:
        text = "https://" + text

    return text


def filename_from_text(text: str) -> str:
    # try URL-based name first
    p = urlparse(text)
    host = (p.netloc or "").split(":")[0]

    if host:
        return f"{host}.png"

    # fallback: hash for arbitrary text
    h = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f"qr_{h}.png"


# ----------------------------
# QR core
# ----------------------------


def make_qr(text: str, cfg: QRConfig) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # type: ignore
        box_size=cfg.box_size,
        border=cfg.border,
    )

    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")  # type: ignore

    # optional upscale (safe integer scaling only)
    if cfg.size:
        scale = cfg.size // img.size[0]
        if scale > 1:
            img = img.resize(
                (img.size[0] * scale, img.size[1] * scale),
                Image.Resampling.NEAREST,
            )

    return img


def save_qr(img: Image.Image, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG", optimize=True)


# ----------------------------
# CLI
# ----------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="qr",
        description="Generate QR codes from arbitrary text (URL, JSON, ID, etc.)",
    )

    p.add_argument(
        "text",
        help="Payload (URL, text, JSON, device ID, etc.)",
    )

    p.add_argument(
        "-o",
        "--out",
        type=str,
        default=None,
        help="Output file path (default: auto-generated)",
    )

    p.add_argument(
        "--size",
        type=int,
        default=512,
        help="Output image size in pixels",
    )

    p.add_argument(
        "--border",
        type=int,
        default=1,
        help="QR border size (quiet zone)",
    )

    p.add_argument(
        "--box-size",
        type=int,
        default=10,
        help="QR module pixel size",
    )

    return p


def main() -> None:
    args = build_parser().parse_args()

    payload = normalize_input(args.text)

    out = args.out or filename_from_text(payload)

    cfg = QRConfig(
        size=args.size,
        border=args.border,
        box_size=args.box_size,
    )
    print(
        f"Generating QR code for payload: {payload} -> {out} (size={cfg.size}px, border={cfg.border}, box_size={cfg.box_size})"
    )
    img = make_qr(payload, cfg)
    save_qr(img, out)

    print(out)


if __name__ == "__main__":
    main()
