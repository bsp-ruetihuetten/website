#!/usr/bin/env python3
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

import yaml


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
BASE_PATH = ""


class RefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag not in {"a", "img", "link", "script"}:
            return
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.refs.append(value)


def load_yaml(path: Path) -> object:
    with path.open() as handle:
        return yaml.safe_load(handle)


def check_yaml() -> None:
    for path in sorted((ROOT / "data").glob("*.yaml")):
        load_yaml(path)


def check_known_downloads() -> None:
    downloads = load_yaml(ROOT / "data" / "downloads.yaml")["downloads"]
    for item in downloads:
        path = ROOT / "static" / item["pfad"].lstrip("/")
        if item.get("status", "public") == "public" and not path.exists():
            raise SystemExit(f"Download fehlt: {item['pfad']}")

    reports = load_yaml(ROOT / "data" / "jahresberichte.yaml")["jahresberichte"]
    for item in reports:
        path = ROOT / "static" / item["pfad"].lstrip("/")
        if item.get("status", "public") == "public" and not path.exists():
            raise SystemExit(f"Jahresbericht fehlt: {item['pfad']}")

    media = load_yaml(ROOT / "data" / "medien_eintraege.yaml")["medien_eintraege"]
    for item in media:
        local_copy = item.get("lokale_kopie")
        if local_copy:
            path = ROOT / "static" / local_copy.lstrip("/")
            if not path.exists():
                raise SystemExit(f"Medienkopie fehlt: {local_copy}")


def public_target_for(path: str) -> Path | None:
    if path.startswith(("http:", "https:", "mailto:", "#", "data:")):
        return None
    parsed = urlparse(path)
    local_path = unquote(parsed.path)
    if not local_path or local_path.startswith("//"):
        return None
    if BASE_PATH and local_path.startswith(f"{BASE_PATH}/"):
        local_path = local_path[len(BASE_PATH) :]
    elif BASE_PATH and local_path == BASE_PATH:
        local_path = "/"
    target = PUBLIC / local_path.lstrip("/")
    if local_path.endswith("/"):
        return target / "index.html"
    if not target.suffix:
        return target / "index.html"
    return target


def check_internal_links() -> None:
    if not PUBLIC.exists():
        raise SystemExit("public/ fehlt. Zuerst `hugo --minify` ausführen.")

    missing: list[tuple[Path, str]] = []
    for html in PUBLIC.rglob("*.html"):
        parser = RefParser()
        parser.feed(html.read_text(errors="ignore"))
        for ref in parser.refs:
            target = public_target_for(ref)
            if target and not target.exists():
                missing.append((html.relative_to(PUBLIC), ref))

    if missing:
        for html, ref in missing:
            print(f"Fehlender interner Link in {html}: {ref}")
        raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default="",
        help="Base URL used for the Hugo build; path prefix is stripped for local link checks.",
    )
    return parser.parse_args()


def main() -> None:
    global BASE_PATH
    args = parse_args()
    BASE_PATH = urlparse(args.base_url).path.rstrip("/")
    check_yaml()
    check_known_downloads()
    check_internal_links()
    print("Website-Checks OK")


if __name__ == "__main__":
    main()
