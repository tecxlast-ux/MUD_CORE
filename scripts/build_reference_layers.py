#!/usr/bin/env python3
"""Build public-safe PUNNARAJ reference layers from reviewed markdown."""

from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT_ROOT = ROOT / "content"

REQUIRED_FRONTMATTER = [
    "title",
    "layer",
    "status",
    "visibility",
    "source_layer",
    "confidence",
    "last_reviewed",
    "owner",
    "tags",
]

ALLOWED_STATUS = {"beta", "reviewed", "canonical", "public"}
ALLOWED_SOURCE_LAYERS = {"reviewed_derived", "compressed", "manual"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
SUSPICIOUS_STRINGS = [
    "API token",
    "client secret",
    "private key",
    "password",
    "bearer token",
    "CLOUDFLARE_API_TOKEN",
    "GITHUB_TOKEN",
    "GOOGLE_CLIENT_SECRET",
    ".dev.vars",
    "BEGIN PRIVATE KEY",
    "sk-",
    "ghp_",
    "gho_",
    "eyJ",
]

LAYER_CONFIG = {
    "beta": {
        "content_dir": CONTENT_ROOT / "beta",
        "output_dir": ROOT / "beta",
        "output_root": "beta",
        "label": "Beta Reference Layer",
        "home_body": (
            "# Beta Reference Layer\n\n"
            "The Beta Reference Layer is reviewed working context for humans and agents. "
            "It is public-readable, marked beta, and generated from reviewed markdown.\n\n"
            "It is not the Zero Vault and it is not final canon."
        ),
    },
    "public": {
        "content_dir": CONTENT_ROOT / "public",
        "output_dir": ROOT / "atlas",
        "output_root": "atlas",
        "label": "Project Atlas",
        "home_body": "",
    },
}


class BuildError(Exception):
    """Raised when publication validation fails."""


@dataclass(frozen=True)
class Document:
    source_path: Path
    relative_path: Path
    meta: dict[str, object]
    body: str
    output_root: str
    output_path: Path
    url: str

    @property
    def title(self) -> str:
        return str(self.meta["title"])

    @property
    def layer(self) -> str:
        return str(self.meta["layer"])


def parse_frontmatter(path: Path, text: str) -> tuple[dict[str, object], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise BuildError(f"{path}: missing opening frontmatter delimiter")

    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break

    if closing_index is None:
        raise BuildError(f"{path}: missing closing frontmatter delimiter")

    frontmatter_lines = lines[1:closing_index]
    body = "\n".join(lines[closing_index + 1 :]).strip() + "\n"
    data: dict[str, object] = {}
    current_key: str | None = None

    for line in frontmatter_lines:
        if not line.strip():
            continue
        if line.startswith("  - "):
            if current_key is None:
                raise BuildError(f"{path}: list item without frontmatter key")
            data.setdefault(current_key, [])
            value = data[current_key]
            if not isinstance(value, list):
                raise BuildError(f"{path}: mixed scalar/list frontmatter for {current_key}")
            value.append(line[4:].strip())
            continue
        if ":" not in line:
            raise BuildError(f"{path}: invalid frontmatter line: {line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise BuildError(f"{path}: empty frontmatter key")
        if value:
            data[key] = value
            current_key = key
        else:
            data[key] = []
            current_key = key

    return data, body


def validate_no_suspicious_strings(path: Path, text: str) -> None:
    lower_text = text.lower()
    for term in SUSPICIOUS_STRINGS:
        if term.lower() in lower_text:
            raise BuildError(f"{path}: blocked suspicious publication string: {term}")


def validate_frontmatter(path: Path, meta: dict[str, object], expected_layer: str) -> None:
    for key in REQUIRED_FRONTMATTER:
        if key not in meta:
            raise BuildError(f"{path}: missing required frontmatter key: {key}")

    for key in REQUIRED_FRONTMATTER:
        value = meta[key]
        if key == "tags":
            if not isinstance(value, list) or not value:
                raise BuildError(f"{path}: tags must be a non-empty list")
            continue
        if not isinstance(value, str) or not value.strip():
            raise BuildError(f"{path}: frontmatter key {key} must be non-empty")

    if meta["layer"] != expected_layer:
        raise BuildError(f"{path}: layer must be {expected_layer}")
    if meta["status"] not in ALLOWED_STATUS:
        raise BuildError(f"{path}: unsupported status {meta['status']}")
    if meta["visibility"] != "public":
        raise BuildError(f"{path}: visibility must be public")
    if meta["source_layer"] not in ALLOWED_SOURCE_LAYERS:
        raise BuildError(f"{path}: unsupported source_layer {meta['source_layer']}")
    if meta["confidence"] not in ALLOWED_CONFIDENCE:
        raise BuildError(f"{path}: unsupported confidence {meta['confidence']}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(meta["last_reviewed"])):
        raise BuildError(f"{path}: last_reviewed must use YYYY-MM-DD")
    if "punnaraj" not in [str(tag).lower() for tag in meta["tags"]]:
        raise BuildError(f"{path}: tags must include punnaraj")


def output_relative_path(relative_path: Path) -> Path:
    if relative_path.name == "index.md":
        return relative_path.with_suffix(".html")
    return relative_path.with_suffix("") / "index.html"


def url_for(output_root: str, output_path: Path) -> str:
    if output_path == Path("index.html"):
        return f"/{output_root}/"
    return f"/{output_root}/{output_path.parent.as_posix().strip('/')}/"


def load_documents(layer: str) -> list[Document]:
    config = LAYER_CONFIG[layer]
    content_dir = config["content_dir"]
    if not content_dir.exists():
        raise BuildError(f"missing content directory: {content_dir}")

    documents: list[Document] = []
    for path in sorted(content_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        validate_no_suspicious_strings(path, text)
        meta, body = parse_frontmatter(path, text)
        validate_frontmatter(path, meta, layer)
        relative_path = path.relative_to(content_dir)
        output_path = output_relative_path(relative_path)
        documents.append(
            Document(
                source_path=path,
                relative_path=relative_path,
                meta=meta,
                body=body,
                output_root=str(config["output_root"]),
                output_path=output_path,
                url=url_for(str(config["output_root"]), output_path),
            )
        )

    if not documents:
        raise BuildError(f"no markdown documents found in {content_dir}")

    return sorted(documents, key=document_sort_key)


def document_sort_key(document: Document) -> tuple[int, str]:
    if document.relative_path == Path("index.md"):
        return (0, "")
    if document.relative_path.name == "index.md":
        return (1, document.relative_path.as_posix())
    return (2, document.relative_path.as_posix())


def make_beta_home(documents: list[Document]) -> Document:
    config = LAYER_CONFIG["beta"]
    return Document(
        source_path=Path("content/beta"),
        relative_path=Path("index.md"),
        meta={
            "title": "Beta Reference Layer",
            "layer": "beta",
            "status": "beta",
            "visibility": "public",
            "source_layer": "manual",
            "confidence": "medium",
            "last_reviewed": "2026-05-17",
            "owner": "Wisut Punnaraj",
            "tags": ["punnaraj"],
        },
        body=str(config["home_body"]),
        output_root="beta",
        output_path=Path("index.html"),
        url="/beta/",
    )


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug or "section"


def render_inline(text: str) -> str:
    pattern = re.compile(r"(`[^`]+`)|(\[([^\]]+)\]\(([^)]+)\))")
    result: list[str] = []
    cursor = 0

    for match in pattern.finditer(text):
        result.append(html.escape(text[cursor : match.start()]))
        if match.group(1):
            code = match.group(1)[1:-1]
            result.append(f"<code>{html.escape(code)}</code>")
        else:
            label = match.group(3)
            href = match.group(4)
            result.append(
                f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
            )
        cursor = match.end()

    result.append(html.escape(text[cursor:]))
    return "".join(result)


def markdown_to_html(markdown: str) -> str:
    parts: list[str] = []
    paragraph: list[str] = []
    list_kind: str | None = None
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            parts.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            parts.append(f"</{list_kind}>")
            list_kind = None

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code:
                parts.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
                code_lines = []
                in_code = False
            else:
                flush_paragraph()
                close_list()
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not stripped:
            flush_paragraph()
            close_list()
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            parts.append(
                f'<h{level} id="{slugify(title)}">{render_inline(title)}</h{level}>'
            )
            continue

        unordered = re.match(r"^-\s+(.+)$", stripped)
        ordered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if unordered or ordered:
            flush_paragraph()
            desired_kind = "ul" if unordered else "ol"
            if list_kind != desired_kind:
                close_list()
                parts.append(f"<{desired_kind}>")
                list_kind = desired_kind
            item_text = (unordered or ordered).group(1)
            parts.append(f"<li>{render_inline(item_text)}</li>")
            continue

        close_list()
        paragraph.append(stripped)

    if in_code:
        parts.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
    flush_paragraph()
    close_list()
    return "\n".join(parts)


def render_status_badges(meta: dict[str, object]) -> str:
    badges = [
        ("layer", meta["layer"]),
        ("status", meta["status"]),
        ("confidence", meta["confidence"]),
    ]
    return "\n".join(
        f'<span class="badge badge-{html.escape(str(value))}">'
        f"{html.escape(label)}: {html.escape(str(value))}</span>"
        for label, value in badges
    )


def render_nav(documents: list[Document], active_url: str, output_root: str) -> str:
    items = []
    for document in documents:
        active = " active" if document.url == active_url else ""
        items.append(
            f'<li><a class="nav-link{active}" href="{document.url}">'
            f"{html.escape(document.title)}</a></li>"
        )

    peer_url = "/atlas/" if output_root == "beta" else "/beta/"
    peer_label = "Project Atlas" if output_root == "beta" else "Beta Reference"

    return (
        '<nav class="site-nav" aria-label="Reference navigation">\n'
        '<div class="nav-tools">\n'
        '<a href="/">Legacy Home</a>\n'
        f'<a href="{peer_url}">{peer_label}</a>\n'
        '<a href="/api/health">Health</a>\n'
        '<a href="/api/system">System</a>\n'
        "</div>\n"
        '<ul class="nav-list">\n'
        + "\n".join(items)
        + "\n</ul>\n"
        "</nav>"
    )


def render_sitemap(documents: list[Document], current: Document) -> str:
    cards = []
    for document in documents:
        if document.url == current.url:
            continue
        group = document.relative_path.parts[0] if len(document.relative_path.parts) > 1 else "root"
        cards.append(
            '<a class="page-card" href="{url}">'
            '<span class="page-card-group">{group}</span>'
            '<strong>{title}</strong>'
            '<span>{status} / {confidence}</span>'
            "</a>".format(
                url=document.url,
                group=html.escape(group),
                title=html.escape(document.title),
                status=html.escape(str(document.meta["status"])),
                confidence=html.escape(str(document.meta["confidence"])),
            )
        )
    return (
        '<section class="sitemap" aria-labelledby="reference-index">\n'
        '<h2 id="reference-index">Reference Index</h2>\n'
        '<div class="page-grid">\n'
        + "\n".join(cards)
        + "\n</div>\n"
        "</section>"
    )


def render_footer(meta: dict[str, object]) -> str:
    fields = [
        "layer",
        "status",
        "source_layer",
        "confidence",
        "last_reviewed",
        "owner",
    ]
    rows = "\n".join(
        f"<dt>{html.escape(field)}</dt><dd>{html.escape(str(meta[field]))}</dd>"
        for field in fields
    )
    return (
        '<footer class="metadata" aria-label="Reference metadata">\n'
        "<h2>Metadata</h2>\n"
        f"<dl>{rows}</dl>\n"
        "</footer>"
    )


def render_shell(document: Document, documents: list[Document], layer_label: str) -> str:
    body_html = markdown_to_html(document.body)
    if document.output_path == Path("index.html"):
        body_html = body_html + "\n" + render_sitemap(documents, document)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(document.title)} | PUNNARAJ</title>
  <link rel="stylesheet" href="/{document.output_root}/assets/style.css" />
</head>
<body>
  <div class="layout">
    <aside class="sidebar">
      <a class="brand" href="/{document.output_root}/">
        <span>PUNNARAJ</span>
        <strong>{html.escape(layer_label)}</strong>
      </a>
      {render_nav(documents, document.url, document.output_root)}
    </aside>
    <main class="content">
      <header class="page-header">
        <p class="layer-label">{html.escape(layer_label)}</p>
        <h1>{html.escape(document.title)}</h1>
        <div class="badges" aria-label="Status badges">
          {render_status_badges(document.meta)}
        </div>
      </header>
      <article class="document">
        {body_html}
      </article>
      {render_footer(document.meta)}
    </main>
  </div>
</body>
</html>
"""


def write_documents(layer: str, documents: list[Document]) -> int:
    config = LAYER_CONFIG[layer]
    output_dir = config["output_dir"]
    page_documents = documents
    if layer == "beta" and not any(doc.output_path == Path("index.html") for doc in documents):
        page_documents = [make_beta_home(documents)] + documents

    for document in page_documents:
        destination = output_dir / document.output_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        html_text = render_shell(document, page_documents, str(config["label"]))
        destination.write_text(html_text, encoding="utf-8")

    return len(page_documents)


def selected_layers(layer: str) -> list[str]:
    if layer == "all":
        return ["beta", "public"]
    return [layer]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--layer",
        choices=["all", "beta", "public"],
        default="all",
        help="Reference layer to build. Public content is emitted under atlas/.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate markdown frontmatter and publication safety without writing HTML.",
    )
    args = parser.parse_args(argv)

    try:
        counts: dict[str, int] = {}
        loaded: dict[str, list[Document]] = {}
        for layer in selected_layers(args.layer):
            documents = load_documents(layer)
            loaded[layer] = documents
            counts[layer] = len(documents)

        if args.validate_only:
            for layer, count in counts.items():
                print(f"{layer}: validated {count} source documents")
            return 0

        written = {
            layer: write_documents(layer, documents) for layer, documents in loaded.items()
        }
        for layer, count in written.items():
            output_root = LAYER_CONFIG[layer]["output_root"]
            print(f"{output_root}: wrote {count} HTML pages")
        return 0
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
