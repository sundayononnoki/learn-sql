"""Copy the roadmap homepage links for offline search on chapter pages.

Run from the project root with: python3 scripts/build-search-index.py
"""

import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin


PROJECT = Path(__file__).resolve().parents[1]
VOID = frozenset("area base br col embed hr img input link meta param source track wbr".split())


@dataclass
class Element:
    tag: str
    attrs: dict
    children: list = field(default_factory=list)

    def walk(self):
        for child in self.children:
            if isinstance(child, Element):
                yield child
                yield from child.walk()

    def text(self):
        parts = []
        for child in self.children:
            if isinstance(child, Element):
                if child.tag not in {"script", "style"}:
                    parts.append(child.text())
            else:
                parts.append(child)
        return "".join(parts)

    def first(self, tag):
        return next((node for node in self.walk() if node.tag == tag), None)


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root = Element("document", {})
        self.stack = [self.root]
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        node = Element(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def title(node):
    return " ".join(node.text().split())


def directory_links(path):
    relative = path.relative_to(PROJECT).as_posix()
    document = Document(path.read_text(encoding="utf-8")).root
    directory = next(node for node in document.walk() if "roadmap-directory" in node.attrs.get("class", "").split())
    for stage in directory.walk():
        if "roadmap-stage" not in stage.attrs.get("class", "").split():
            continue
        chapter = re.sub(r"^(\d{2})\s*", r"\1 ", title(stage.first("h2")))
        for topics in stage.walk():
            if "roadmap-topic-list" not in topics.attrs.get("class", "").split():
                continue
            for link in topics.walk():
                if link.tag == "a" and link.attrs.get("href"):
                    yield {"title": title(link), "chapter": chapter, "url": urljoin(relative, link.attrs["href"])}


def main():
    records = list(directory_links(PROJECT / "index.html"))
    contents = ",\n".join(json.dumps(record, ensure_ascii=False, separators=(",", ":")) for record in records)
    destination = PROJECT / "assets/search-index.js"
    destination.write_text(
        "// Generated from index.html by scripts/build-search-index.py.\nwindow.sqlRoadmapDirectoryLinks = [\n"
        + contents + "\n];\n",
        encoding="utf-8",
    )
    print(f"Copied {len(records)} homepage topic links.")


if __name__ == "__main__":
    main()
