from __future__ import annotations

import argparse

from qrtools.generator import (
    QRConfig,
    filename_from_text,
    make_qr,
    normalize_input,
    save_qr,
)


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
