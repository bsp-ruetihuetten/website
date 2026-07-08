#!/usr/bin/env python3
from __future__ import annotations

import csv
import mimetypes
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlparse, urlsplit, urlunsplit

import yaml


WORKSPACE = Path(__file__).resolve().parents[3]
WEBSITE = WORKSPACE / "Website"
ARCHIVE = WEBSITE / "Archiv" / "2026-07-07-externe-medien"
IMAGE_DIR = ARCHIVE / "images"
METADATA_DIR = ARCHIVE / "metadata"
PARSE_RESULTS = METADATA_DIR / "external-media-parse-results.csv"
DATA_FILES = [
    WEBSITE / "data" / "medien_eintraege.yaml",
    WEBSITE / "bauspielplatz-website" / "data" / "medien_eintraege.yaml",
]

USER_AGENT = "Bauspielplatz-Ruetihuetten-Archive/1.0"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}
EXCLUDED_TERMS = {
    "0.gif",
    "aaa.gif",
    "apple-touch-icon",
    "badge",
    "banner",
    "emilfrey",
    "favicon",
    "gen_dot",
    "hoengger_og-image",
    "icon",
    "krebsliga",
    "logo",
    "mailsignatur",
    "polyrapid",
    "riedhof",
    "silhouette",
    "spacer",
    "tertianum",
    "themen_",
    "toyota",
    "vorlesen",
    "zweifel",
}
RELEVANT_TERMS = {
    "8049_kinder_bauspielplatz",
    "bau",
    "bauspielplatz",
    "boegg",
    "böög",
    "bsp",
    "castagnata",
    "fest",
    "huetten",
    "hütten",
    "marroni",
    "pfahlbauer",
    "ruetihuetten",
    "rütihütten",
    "ruettihuetten",
    "spielplatz",
}


@dataclass(frozen=True)
class Candidate:
    url: str
    quelle: str
    alt: str = ""


class ImageParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.candidates: list[Candidate] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.lower(): value or "" for key, value in attrs}
        if tag == "meta":
            name = (values.get("property") or values.get("name") or "").lower()
            if name in {"og:image", "twitter:image"} and values.get("content"):
                self.add(values["content"], "meta", "")
            return

        if tag != "img":
            style = values.get("style", "")
            for url in style_urls(style):
                self.add(url, "style-background", "")
            return

        alt = values.get("alt") or values.get("title") or ""
        for key in ("src", "data-src", "data-lazy-src", "data-original"):
            if values.get(key):
                self.add(values[key], key, alt)
        if values.get("srcset"):
            srcset_url = largest_srcset_url(values["srcset"])
            if srcset_url:
                self.add(srcset_url, "srcset", alt)

    def add(self, url: str, quelle: str, alt: str) -> None:
        if not url:
            return
        self.candidates.append(Candidate(urljoin(self.base_url, url), quelle, alt.strip()))


def style_urls(style: str) -> list[str]:
    return [match.strip("\"' ") for match in re.findall(r"url\(([^)]+)\)", style)]


def largest_srcset_url(srcset: str) -> str:
    best_url = ""
    best_width = -1
    for part in srcset.split(","):
        tokens = part.strip().split()
        if not tokens:
            continue
        width = 0
        if len(tokens) > 1 and tokens[1].endswith("w"):
            try:
                width = int(tokens[1][:-1])
            except ValueError:
                width = 0
        if width >= best_width:
            best_url = tokens[0]
            best_width = width
    return best_url


def safe_filename(value: str) -> str:
    value = unquote(value)
    value = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value).strip("-")
    return value or "bild"


def image_suffix(url: str, content_type: str = "") -> str:
    suffix = Path(unquote(urlparse(url).path)).suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return ".jpg" if suffix == ".jpeg" else suffix
    guessed = mimetypes.guess_extension(content_type.split(";")[0].strip())
    if guessed in IMAGE_EXTENSIONS or guessed == ".jpe":
        return ".jpg" if guessed in {".jpeg", ".jpe"} else guessed
    return ".jpg"


def is_candidate_image(candidate: Candidate) -> bool:
    parsed = urlparse(candidate.url)
    if parsed.scheme not in {"http", "https"}:
        return False
    lower = unquote(candidate.url).lower()
    if lower.startswith("data:") or any(term in lower for term in EXCLUDED_TERMS):
        return False
    suffix = Path(parsed.path).suffix.lower()
    if suffix and suffix not in IMAGE_EXTENSIONS:
        return False
    if candidate.quelle in {"meta", "style-background"}:
        return True
    haystack = f"{lower} {candidate.alt.lower()}"
    return any(term in haystack for term in RELEVANT_TERMS)


def fetch(url: str) -> tuple[bytes, str, str]:
    request = urllib.request.Request(quote_url(url), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
        content_type = response.headers.get("content-type", "")
        final_url = response.geturl()
    return body, content_type, final_url


def quote_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            quote(unquote(parts.path), safe="/:@"),
            quote(unquote(parts.query), safe="=&?/:@"),
            quote(unquote(parts.fragment), safe="=&?/:@"),
        )
    )


def load_items(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text())
    return data["medien_eintraege"]


def write_items(path: Path, items: list[dict]) -> None:
    path.write_text(yaml.safe_dump({"medien_eintraege": items}, allow_unicode=True, sort_keys=False))


def load_final_urls() -> dict[str, str]:
    if not PARSE_RESULTS.exists():
        return {}
    with PARSE_RESULTS.open() as handle:
        return {row["id"]: row.get("final_url") or row.get("url") or "" for row in csv.DictReader(handle)}


def unique_candidates(candidates: list[Candidate]) -> list[Candidate]:
    seen: set[str] = set()
    unique: list[Candidate] = []
    for candidate in candidates:
        normalized = candidate.url.split("#", 1)[0]
        if normalized in seen:
            continue
        seen.add(normalized)
        unique.append(candidate)
    return unique


def parse_html_images(item: dict, final_urls: dict[str, str]) -> list[Candidate]:
    raw = item.get("archiv_rohdatei")
    if not raw or not raw.endswith(".html"):
        return []
    raw_path = WORKSPACE / raw
    if not raw_path.exists():
        return []
    base_url = final_urls.get(item["id"]) or item.get("externe_url") or ""
    parser = ImageParser(base_url)
    parser.feed(raw_path.read_text(errors="ignore"))
    return [candidate for candidate in unique_candidates(parser.candidates) if is_candidate_image(candidate)]


def archive_item_images(item: dict, final_urls: dict[str, str]) -> tuple[list[str], list[dict]]:
    item_id = item["id"]
    target_dir = IMAGE_DIR / safe_filename(item_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    for old_file in target_dir.iterdir():
        if old_file.is_file():
            old_file.unlink()
    rows: list[dict] = []
    paths: list[str] = []
    candidates = parse_html_images(item, final_urls)
    for index, candidate in enumerate(candidates, start=1):
        row = {
            "id": item_id,
            "status": "failed",
            "source_url": candidate.url,
            "final_url": "",
            "source_type": candidate.quelle,
            "alt": candidate.alt,
            "path": "",
            "content_type": "",
            "bytes": "",
            "error": "",
        }
        try:
            body, content_type, final_url = fetch(candidate.url)
            if not content_type.lower().startswith("image/"):
                raise RuntimeError(f"not an image content type: {content_type}")
            basename = safe_filename(Path(urlparse(final_url).path).stem)
            filename = f"{index:02d}-{basename}{image_suffix(final_url, content_type)}"
            target = target_dir / filename
            target.write_bytes(body)
            path = str(target.relative_to(WORKSPACE))
            paths.append(path)
            row.update(
                {
                    "status": "archived",
                    "final_url": final_url,
                    "path": path,
                    "content_type": content_type,
                    "bytes": str(len(body)),
                }
            )
        except Exception as exc:  # noqa: BLE001 - archive script should keep going through bad image URLs.
            row["error"] = str(exc)
        rows.append(row)
    return paths, rows


def main() -> int:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    final_urls = load_final_urls()
    canonical_items = load_items(DATA_FILES[0])
    all_rows: list[dict] = []
    by_id: dict[str, dict] = {}

    for item in canonical_items:
        paths, rows = archive_item_images(item, final_urls)
        all_rows.extend(rows)
        item["archiv_bilder"] = paths
        item["archiv_bilder_anzahl"] = len(paths)
        item["archiv_bilder_status"] = "archived" if paths else "none"
        by_id[item["id"]] = item

    for path in DATA_FILES:
        items = load_items(path)
        for item in items:
            updated = by_id.get(item["id"])
            if updated:
                item.update(
                    {
                        key: updated[key]
                        for key in ("archiv_bilder", "archiv_bilder_anzahl", "archiv_bilder_status")
                    }
                )
        write_items(path, items)

    output = METADATA_DIR / "external-media-image-results.csv"
    with output.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "status",
                "source_url",
                "final_url",
                "source_type",
                "alt",
                "path",
                "content_type",
                "bytes",
                "error",
            ],
        )
        writer.writeheader()
        writer.writerows(all_rows)

    archived = sum(1 for row in all_rows if row["status"] == "archived")
    failed = sum(1 for row in all_rows if row["status"] == "failed")
    print(f"archived={archived} failed={failed} candidates={len(all_rows)}")
    print(output)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
