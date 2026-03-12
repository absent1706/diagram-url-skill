#!/usr/bin/env python3
"""
diagram_url.py — Convert between diagram source and shareable URLs.

Supports two engines:
  - mermaid.live (default for Mermaid diagrams) — interactive editor
  - kroki.io (default for everything else) — universal renderer

No dependencies, pure Python 3 stdlib.

Usage as CLI:
    python diagram_url.py to-url diagram.mmd
    python diagram_url.py to-url -t plantuml diagram.puml
    python diagram_url.py to-url --engine kroki diagram.mmd
    python diagram_url.py to-diagram 'https://mermaid.live/edit#pako:...'
    python diagram_url.py to-diagram 'https://kroki.io/mermaid/svg/eNp...'
"""

import argparse
import base64
import json
import re
import sys
import zlib


# ---------------------------------------------------------------------------
# mermaid.live engine
# ---------------------------------------------------------------------------

def _mermaid_encode(diagram: str) -> str:
    state = json.dumps(
        {
            "code": diagram,
            "mermaid": json.dumps({"theme": "default"}),
            "autoSync": True,
            "updateDiagram": True,
            "updateEditor": True,
        },
        separators=(",", ":"),
    )
    compress_obj = zlib.compressobj(9, zlib.DEFLATED, 15)
    compressed = compress_obj.compress(state.encode("utf-8")) + compress_obj.flush()
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii").rstrip("=")
    return f"https://mermaid.live/edit#pako:{encoded}"


def _mermaid_decode(url: str) -> str:
    encoded = url.split("#pako:")[1]
    encoded += "=" * (-len(encoded) % 4)
    compressed = base64.urlsafe_b64decode(encoded)
    # Try zlib-wrapped first, fall back to raw deflate (legacy)
    try:
        state = json.loads(zlib.decompress(compressed))
    except zlib.error:
        state = json.loads(zlib.decompress(compressed, -15))
    return state["code"]


# ---------------------------------------------------------------------------
# kroki.io engine
# ---------------------------------------------------------------------------

def _kroki_encode(diagram: str, diagram_type: str, output_format: str) -> str:
    compressed = zlib.compress(diagram.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode("ascii")
    return f"https://kroki.io/{diagram_type}/{output_format}/{encoded}"


def _kroki_decode(url: str) -> tuple[str, str, str]:
    m = re.match(r"https?://kroki\.io/([^/]+)/([^/]+)/(.+)", url)
    if not m:
        raise ValueError("Not a valid kroki.io URL")
    diagram_type, output_format, encoded = m.groups()
    encoded += "=" * (-len(encoded) % 4)
    compressed = base64.urlsafe_b64decode(encoded)
    return zlib.decompress(compressed).decode("utf-8"), diagram_type, output_format


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def to_url(
    diagram: str,
    diagram_type: str = "mermaid",
    output_format: str = "svg",
    engine: str | None = None,
) -> str:
    """Encode a diagram into a shareable URL.

    engine: "mermaid" | "kroki" | None (auto — mermaid.live for mermaid, kroki for others)
    """
    if engine is None:
        engine = "mermaid" if diagram_type == "mermaid" else "kroki"

    if engine == "mermaid":
        if diagram_type != "mermaid":
            raise ValueError("mermaid.live engine only supports mermaid diagrams")
        return _mermaid_encode(diagram)
    else:
        return _kroki_encode(diagram, diagram_type, output_format)


def to_diagram(url: str) -> tuple[str, str]:
    """Decode a URL back into diagram text.

    Returns (diagram_text, diagram_type).
    Auto-detects engine from URL.
    """
    if "#pako:" in url:
        return _mermaid_decode(url), "mermaid"
    elif "kroki.io/" in url:
        text, dtype, _ = _kroki_decode(url)
        return text, dtype
    else:
        raise ValueError(
            "Unrecognized URL. Expected mermaid.live (#pako:...) or kroki.io URL."
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert between diagram source and shareable URLs (mermaid.live / kroki.io)."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_encode = sub.add_parser("to-url", help="Diagram → URL")
    p_encode.add_argument(
        "file",
        help='Path to diagram file, or "-" to read from stdin',
    )
    p_encode.add_argument(
        "-t", "--type",
        default="mermaid",
        help="Diagram type (mermaid, plantuml, graphviz, etc.). Default: mermaid",
    )
    p_encode.add_argument(
        "-f", "--format",
        default="svg",
        help="Output format for kroki (svg, png, pdf). Default: svg",
    )
    p_encode.add_argument(
        "-e", "--engine",
        choices=["mermaid", "kroki"],
        default=None,
        help="Engine: mermaid (mermaid.live) or kroki (kroki.io). Default: auto",
    )

    p_decode = sub.add_parser("to-diagram", help="URL → diagram source")
    p_decode.add_argument("url", help="mermaid.live or kroki.io URL to decode")

    args = parser.parse_args()

    if args.command == "to-url":
        if args.file == "-":
            diagram = sys.stdin.read()
        else:
            with open(args.file) as f:
                diagram = f.read()
        print(to_url(diagram, diagram_type=args.type, output_format=args.format, engine=args.engine))

    elif args.command == "to-diagram":
        text, dtype = to_diagram(args.url)
        print(text)


if __name__ == "__main__":
    main()
