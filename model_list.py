#!/usr/bin/env python3
"""Extract model ids from OpenRouter-style models.json ({"data": [{ "id": ... }, ...]})."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_ids(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        payload = json.load(f)

    items = payload.get("data")
    if not isinstance(items, list):
        raise ValueError("expected top-level key 'data' with a list")

    ids: list[str] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict) or "id" not in item:
            raise ValueError(f"data[{i}] missing 'id'")
        ids.append(str(item["id"]))
    return ids


def filter_by_provider(ids: list[str], provider: str) -> list[str]:
    """Keep ids whose vendor prefix matches (e.g. openai -> openai/gpt-5-mini)."""
    prefix = f"{provider.strip()}/"
    return [i for i in ids if i.startswith(prefix)]


def vendor_prefix(model_id: str) -> str:
    return model_id.split("/", 1)[0] if "/" in model_id else model_id


def sort_by_prefix(ids: list[str]) -> list[str]:
    return sorted(ids, key=lambda x: (vendor_prefix(x).lower(), x.lower()))


def lines_grouped_by_prefix(ids: list[str]) -> list[str]:
    """Sorted ids with a blank line between each vendor prefix block."""
    ordered = sort_by_prefix(ids)
    lines: list[str] = []
    prev_prefix: str | None = None
    for mid in ordered:
        p = vendor_prefix(mid)
        if prev_prefix is not None and p != prev_prefix:
            lines.append("")
        lines.append(mid)
        prev_prefix = p
    return lines


def parse_args(argv: list[str] | None) -> tuple[argparse.Namespace, str | None]:
    ap = argparse.ArgumentParser(
        description="List model ids from models.json. "
        "Without -p/--vendor: sorted and grouped by vendor prefix (blank line between groups). "
        "Optional: filter by vendor (e.g. --openai or -p openai)."
    )
    ap.add_argument(
        "json_path",
        nargs="?",
        default=Path(__file__).resolve().parent / "models.json",
        type=Path,
        help="Path to models.json (default: ./models.json next to this script)",
    )
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Write ids here (default: stdout)",
    )
    ap.add_argument(
        "--as-json",
        action="store_true",
        help='Output as JSON array: ["id1", "id2", ...]',
    )
    ap.add_argument(
        "-p",
        "--provider",
        metavar="NAME",
        default=None,
        help="Only list models for this vendor (id prefix before the first /), e.g. openai, anthropic, x-ai",
    )
    args, rest = ap.parse_known_args(argv)

    provider: str | None = args.provider
    for raw in rest:
        if not raw.startswith("--"):
            ap.error(f"unexpected argument: {raw!r}")
        name = raw[2:]
        if not name:
            ap.error("empty flag after --")
        if provider is not None:
            ap.error("only one provider filter allowed (use -p NAME or a single --vendor flag)")
        provider = name

    return args, provider


def main() -> int:
    args, provider = parse_args(None)

    path: Path = args.json_path
    if not path.is_file():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        ids = load_ids(path)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if provider:
        ids = filter_by_provider(ids, provider)

    if args.as_json:
        out = json.dumps(sort_by_prefix(ids), indent=2) + "\n"
    else:
        if provider:
            out = "\n".join(sort_by_prefix(ids)) + "\n"
        else:
            out = "\n".join(lines_grouped_by_prefix(ids)) + "\n"

    if args.output:
        args.output.write_text(out, encoding="utf-8")
    else:
        sys.stdout.write(out)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
