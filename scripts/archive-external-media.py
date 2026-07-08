#!/usr/bin/env python3
from __future__ import annotations

import csv
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import yaml


WORKSPACE = Path(__file__).resolve().parents[3]
WEBSITE = WORKSPACE / "Website"
ARCHIVE = WEBSITE / "Archiv" / "2026-07-07-externe-medien"
MARKDOWN_DIR = ARCHIVE / "markdown"
RAW_HTML_DIR = ARCHIVE / "raw_html"
RAW_DOWNLOADS_DIR = ARCHIVE / "raw_downloads"
METADATA_DIR = ARCHIVE / "metadata"
DATA_FILES = [
    WEBSITE / "data" / "medien_eintraege.yaml",
    WEBSITE / "bauspielplatz-website" / "data" / "medien_eintraege.yaml",
]

USER_AGENT = "Bauspielplatz-Ruetihuetten-Archive/1.0"


def slug_filename(item_id: str, suffix: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "-", item_id).strip("-")
    return f"{safe}{suffix}"


def fetch(url: str) -> tuple[bytes, str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read()
        content_type = response.headers.get("content-type", "")
        final_url = response.geturl()
    return body, content_type, final_url


def run_command(args: list[str], input_path: Path | None = None) -> str:
    if input_path:
        args = [*args, str(input_path)]
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"command failed: {' '.join(args)}")
    return result.stdout


def html_to_markdown(raw_path: Path) -> str:
    return run_command(["pandoc", "--from", "html", "--to", "gfm-raw_html", "--wrap=none"], raw_path)


def pdf_to_text(raw_path: Path) -> str:
    with tempfile.NamedTemporaryFile(suffix=".txt") as output:
        result = subprocess.run(
            ["pdftotext", "-layout", str(raw_path), output.name],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "pdftotext failed")
        return Path(output.name).read_text(errors="replace")


def yaml_frontmatter(item: dict, status: str, raw_path: Path | None, content_type: str, final_url: str) -> str:
    frontmatter = {
        "id": item.get("id", ""),
        "titel": item.get("titel", ""),
        "typ": item.get("typ", ""),
        "datum": item.get("datum", ""),
        "quelle": item.get("quelle", ""),
        "externe_url": item.get("externe_url", ""),
        "finale_url": final_url,
        "abgerufen_am": str(date.today()),
        "archiv_status": status,
        "content_type": content_type,
    }
    if raw_path:
        frontmatter["archiv_rohdatei"] = str(raw_path.relative_to(WORKSPACE))
    return "---\n" + yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=False) + "---\n\n"


def build_markdown(item: dict, parsed_text: str, status: str, raw_path: Path | None, content_type: str, final_url: str) -> str:
    title = item.get("titel") or item.get("id")
    note = (
        "Interner Arbeitsauszug aus einer externen Quelle. "
        "Für die öffentliche Website nur kuratierte Zusammenfassung und Link verwenden."
    )
    body = [
        yaml_frontmatter(item, status, raw_path, content_type, final_url),
        f"# {title}\n",
        f"- Quelle: {item.get('quelle', '')}",
        f"- Original: {item.get('externe_url', '')}",
        f"- Finale URL beim Abruf: {final_url}",
        "",
        f"> {note}",
        "",
        "## Geparster Text",
        "",
        parsed_text.strip(),
        "",
    ]
    return "\n".join(body)


def load_items(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text())
    return data["medien_eintraege"]


def write_items(path: Path, items: list[dict]) -> None:
    path.write_text(
        yaml.safe_dump({"medien_eintraege": items}, allow_unicode=True, sort_keys=False),
    )


def parse_item(item: dict) -> dict:
    item_id = item["id"]
    url = item.get("externe_url")
    result = {
        "id": item_id,
        "url": url,
        "status": "skipped",
        "content_type": "",
        "final_url": "",
        "markdown": "",
        "raw": "",
        "error": "",
    }
    markdown_path = MARKDOWN_DIR / slug_filename(item_id, ".md")
    try:
        if url:
            body, content_type, final_url = fetch(url)
            lower_url = urlparse(final_url).path.lower()
            is_pdf = "pdf" in content_type.lower() or lower_url.endswith(".pdf")

            if is_pdf:
                raw_path = RAW_DOWNLOADS_DIR / slug_filename(item_id, ".pdf")
                raw_path.write_bytes(body)
                parsed = pdf_to_text(raw_path)
            else:
                raw_path = RAW_HTML_DIR / slug_filename(item_id, ".html")
                raw_path.write_bytes(body)
                parsed = html_to_markdown(raw_path)
        else:
            final_url = ""
            source = item.get("archiv_quelle")
            if source:
                raw_path = WORKSPACE / source
            elif item.get("lokale_kopie"):
                raw_path = WEBSITE / "bauspielplatz-website" / "static" / item["lokale_kopie"].lstrip("/")
            else:
                return result

            if not raw_path.exists():
                raise FileNotFoundError(raw_path)

            content_type = "application/pdf" if raw_path.suffix.lower() == ".pdf" else "text/html"
            parsed = pdf_to_text(raw_path) if raw_path.suffix.lower() == ".pdf" else html_to_markdown(raw_path)

        markdown_path.write_text(build_markdown(item, parsed, "parsed", raw_path, content_type, final_url))
        result.update(
            {
                "status": "parsed",
                "content_type": content_type,
                "final_url": final_url,
                "markdown": str(markdown_path.relative_to(WORKSPACE)),
                "raw": str(raw_path.relative_to(WORKSPACE)),
            }
        )
    except Exception as exc:  # noqa: BLE001 - archive script should continue through bad external links.
        markdown_path.write_text(build_markdown(item, str(exc), "failed", None, "", url))
        result.update(
            {
                "status": "failed",
                "final_url": url,
                "markdown": str(markdown_path.relative_to(WORKSPACE)),
                "error": str(exc),
            }
        )
    return result


def main() -> int:
    for directory in (MARKDOWN_DIR, RAW_HTML_DIR, RAW_DOWNLOADS_DIR, METADATA_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    canonical_items = load_items(DATA_FILES[0])
    results = []
    by_id = {}
    for item in canonical_items:
        result = parse_item(item)
        results.append(result)
        if result["markdown"]:
            item["archiv_markdown"] = result["markdown"]
        if result["raw"]:
            item["archiv_rohdatei"] = result["raw"]
        if result["status"]:
            item["archiv_parse_status"] = result["status"]
        by_id[item["id"]] = item

    for path in DATA_FILES:
        items = load_items(path)
        for item in items:
            updated = by_id.get(item["id"])
            if updated:
                item.update(
                    {
                        key: updated[key]
                        for key in ("archiv_markdown", "archiv_rohdatei", "archiv_parse_status")
                        if key in updated
                    }
                )
        write_items(path, items)

    with (METADATA_DIR / "external-media-parse-results.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "url", "status", "content_type", "final_url", "markdown", "raw", "error"],
        )
        writer.writeheader()
        writer.writerows(results)

    parsed = sum(1 for result in results if result["status"] == "parsed")
    failed = sum(1 for result in results if result["status"] == "failed")
    skipped = sum(1 for result in results if result["status"] == "skipped")
    print(f"parsed={parsed} failed={failed} skipped={skipped}")
    print(METADATA_DIR / "external-media-parse-results.csv")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
