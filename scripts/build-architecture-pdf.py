# /// script
# requires-python = ">=3.12"
# dependencies = ["markdown==3.8"]
# ///
"""Build the Part 2 PDF, architecture-trade-offs.pdf at the root.

Its one source is docs/explanation/architecture-trade-offs.md. This script
checks each Mermaid diagram there against the size limits and accessibility
fields the diagrams rule declares for that document, renders it to SVG with
the Mermaid CLI, converts the page to HTML, and prints it to PDF with headless
Chrome. It then counts the pages and fails unless there are two to four, the
brief's bound.

Run from the repository root:

    uv run scripts/build-architecture-pdf.py

Needs Google Chrome, and npx able to run @mermaid-js/mermaid-cli (fetched on
first use). Set CHROME to use another Chrome or Chromium binary.
"""

import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import NoReturn

import markdown

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs" / "explanation" / "architecture-trade-offs.md"
# At the root with the other deliverables, outside the trees whose READMEs map every file.
TARGET = ROOT / "architecture-trade-offs.pdf"
REPOSITORY_URL = "https://github.com/wahidyankf/proto-account-ledger-py/blob/main"
MERMAID_CLI = "@mermaid-js/mermaid-cli@11.14.0"
CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
)

# The limits the diagrams rule declares for this document's rendered diagrams.
MAX_NODES_PER_LEVEL = 6
MAX_LABEL_LINE = 30
MIN_PAGES, MAX_PAGES = 2, 4
# Seconds a render or the print may take before the build gives up rather than hangs.
STEP_TIMEOUT = 180

ACC_DESCR_BLOCK = re.compile(r"^\s*accDescr\s*\{.*?\}", re.MULTILINE | re.DOTALL)
MERMAID_BLOCK = re.compile(r"^```mermaid\n(.*?)^```\n", re.MULTILINE | re.DOTALL)
FLOW_NODE = re.compile(r"([A-Za-z]\w*)\s*(\[\(|\[\[|\(\(|\[|\(|\{)(.*?)(\)\]|\]\]|\)\)|\]|\)|\})")
FLOW_EDGE = re.compile(r"([A-Za-z]\w*)[^\n]*?(?:-->|-\.->|==>|---)(?:\|([^|]*)\|)?\s*([A-Za-z]\w*)")
FLOW_EDGE_TEXT = re.compile(r"--\s+([^->][^-]*?)\s+-->")
STATE_EDGE = re.compile(r"^\s*(\[\*\]|\w+)\s*-->\s*(\[\*\]|\w+)\s*(?::\s*(.*))?$")
STATE_ALIAS = re.compile(r'^\s*state\s+"([^"]*)"\s+as\s+\w+\s*$')
STATE_NOTE = re.compile(r"^\s*note (?:left|right) of \w+\s*:\s*(.*)$")
RELATIVE_LINK = re.compile(r'href="(?!https?:|#|mailto:)([^"#]+)(#[^"]*)?"')

STYLE = """
@page { size: A4; margin: 15mm 16mm; }
body { font-family: -apple-system, "Helvetica Neue", Arial, sans-serif; font-size: 9.6pt;
       line-height: 1.38; color: #111; }
h1 { font-size: 17pt; margin: 0 0 4pt; }
h2 { font-size: 12.5pt; margin: 12pt 0 4pt; border-bottom: 1px solid #999; padding-bottom: 2pt;
     break-after: avoid; }
p, ul { margin: 3pt 0 5pt; }
li { margin: 1pt 0; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 6pt; font-size: 8.8pt; }
th, td { border: 1px solid #999; padding: 2pt 5pt; text-align: left; vertical-align: top; }
th { background: #eee; }
code { font-family: Menlo, Consolas, monospace; font-size: 8.6pt; }
a { color: #0645ad; text-decoration: none; }
figure { margin: 5pt 0 7pt; text-align: center; break-inside: avoid; }
figure svg { max-width: 100%; max-height: 62mm; height: auto; }
figcaption { font-size: 8.4pt; color: #444; margin-top: 2pt; }
"""


def fail(message: str) -> NoReturn:
    """Report a failure on standard error and stop with status 1."""

    print(f"error: {message}", file=sys.stderr)

    raise SystemExit(1)


def find_chrome() -> str:
    """Return the Chrome binary, from CHROME or the first candidate found."""

    for candidate in (os.environ.get("CHROME", ""), *CHROME_CANDIDATES):
        if candidate and (Path(candidate).is_file() or shutil.which(candidate)):
            return candidate

    fail("no Chrome or Chromium found; set CHROME to its path")


def run(command: list[str], step: str) -> subprocess.CompletedProcess[str]:
    """Run one build step, failing if it outlasts the step timeout."""

    try:
        return subprocess.run(command, capture_output=True, text=True, check=False, timeout=STEP_TIMEOUT)

    except subprocess.TimeoutExpired:
        fail(f"{step} did not finish within {STEP_TIMEOUT} s")


def list_labels(diagram: str) -> tuple[str, list[str], dict[str, set[str]]]:
    """Return a diagram's type, every label line, and its edges by source."""

    diagram = ACC_DESCR_BLOCK.sub("", diagram)
    lines = [line for line in diagram.splitlines() if line.strip()]
    kind = lines[0].split()[0]

    labels: list[str] = []
    edges: dict[str, set[str]] = {}

    for line in lines[1:]:
        if line.strip().startswith(("accTitle", "accDescr", "%%")):
            continue

        if kind == "flowchart":
            labels += [text for _, _, text, _ in FLOW_NODE.findall(line)]
            labels += FLOW_EDGE_TEXT.findall(line)

            for source, text, target in FLOW_EDGE.findall(line):
                labels += [text] if text else []
                edges.setdefault(source, set()).add(target)
                edges.setdefault(target, set())

        elif kind == "stateDiagram-v2":
            if named := STATE_ALIAS.match(line) or STATE_NOTE.match(line):
                labels.append(named.group(1))

            elif edge := STATE_EDGE.match(line):
                source = "start" if edge.group(1) == "[*]" else edge.group(1)
                target = "end" if edge.group(2) == "[*]" else edge.group(2)
                labels += [edge.group(3)] if edge.group(3) else []
                edges.setdefault(source, set()).add(target)
                edges.setdefault(target, set())

        else:
            fail(f"diagram type {kind!r} has no size check; use flowchart or stateDiagram-v2")

    split = [part.strip(' "') for label in labels for part in re.split(r"<br\s*/?>", label)]

    return kind, split, edges


def count_nodes_per_level(edges: dict[str, set[str]]) -> int:
    """Return the most nodes on one level, a node's level its shortest distance from a root."""

    targets = {target for sources in edges.values() for target in sources}
    frontier = [node for node in edges if node not in targets] or list(edges)[:1]
    level = dict.fromkeys(frontier, 0)

    while frontier:
        reached: list[str] = []

        for node in frontier:
            for target in sorted(edges[node] - level.keys()):
                level[target] = level[node] + 1
                reached.append(target)

        frontier = reached

    depths = list(level.values())

    return max((depths.count(depth) for depth in set(depths)), default=0)


def check_diagram(number: int, diagram: str) -> str:
    """Refuse a diagram missing its accessible title or description, or over a limit; return its title."""

    title = re.search(r"^\s*accTitle:\s*(.+)$", diagram, re.MULTILINE)

    if not title or not re.search(r"^\s*accDescr(?::\s*\S|\s*\{\s*[^\s}])", diagram, re.MULTILINE):
        fail(f"diagram {number} needs both accTitle and accDescr")

    kind, labels, edges = list_labels(diagram)

    for label in labels:
        if len(label) > MAX_LABEL_LINE:
            fail(f"diagram {number}: label line {label!r} is over {MAX_LABEL_LINE} characters")

    widest = count_nodes_per_level(edges)

    if widest > MAX_NODES_PER_LEVEL:
        fail(f"diagram {number} ({kind}): {widest} nodes on one level, over {MAX_NODES_PER_LEVEL}")

    return title.group(1).strip()


def render_diagram(number: int, diagram: str, work: Path, chrome: str) -> str:
    """Render one diagram to SVG with the Mermaid CLI and return the SVG markup."""

    source, target, config = work / f"d{number}.mmd", work / f"d{number}.svg", work / "puppeteer.json"
    source.write_text(diagram, encoding="utf-8")
    config.write_text(json.dumps({"executablePath": chrome, "args": ["--no-sandbox"]}), encoding="utf-8")

    command = ["npx", "--yes", MERMAID_CLI, "--quiet", "-p", str(config), "-t", "neutral", "-b", "white"]
    command += ["-I", f"diagram-{number}", "-i", str(source), "-o", str(target)]
    done = run(command, f"diagram {number}")

    if done.returncode != 0 or not target.is_file():
        fail(f"diagram {number} did not render:\n{done.stderr.strip()}")

    return target.read_text(encoding="utf-8")


def replace_diagrams(text: str, work: Path, chrome: str) -> str:
    """Swap every Mermaid block for a figure holding its SVG, after checking it."""

    parts: list[str] = []
    position = 0

    for number, block in enumerate(MERMAID_BLOCK.finditer(text), start=1):
        diagram = block.group(1)
        title = check_diagram(number, diagram)
        svg = base64.b64encode(render_diagram(number, diagram, work, chrome).encode()).decode()
        figure = f'<figure><div data-svg="{svg}"></div><figcaption>Figure {number}. {title}</figcaption></figure>'

        parts += [text[position : block.start()], f"\n{figure}\n\n"]
        position = block.end()

    return "".join([*parts, text[position:]])


def link_to_repository(html: str) -> str:
    """Point each relative link at the file on GitHub, since a PDF has no repository beside it."""

    def absolute(match: re.Match[str]) -> str:
        path = (SOURCE.parent / match.group(1)).resolve().relative_to(ROOT).as_posix()

        return f'href="{REPOSITORY_URL}/{path}{match.group(2) or ""}"'

    return RELATIVE_LINK.sub(absolute, html)


def inline_svgs(html: str) -> str:
    """Put each rendered SVG back in place of its placeholder, after the Markdown pass."""

    return re.sub(r'<div data-svg="([^"]+)"></div>', lambda match: base64.b64decode(match.group(1)).decode(), html)


def count_pages(pdf: bytes) -> int:
    """Return the number of page objects in a PDF."""

    return len(re.findall(rb"/Type\s*/Page(?!s)", pdf))


def print_pdf(chrome: str, html: Path, output: Path, profile: Path) -> None:
    """Print the page to PDF with headless Chrome, stopping Chrome once the file is complete.

    Chrome can stay running after it writes the PDF, held open by its updater, so the build waits for the file's
    end-of-file marker instead of for Chrome to exit. A profile of its own keeps an open Chrome from being reused.
    """

    command = [chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={profile}"]
    command += [f"--print-to-pdf={output}", html.as_uri()]
    deadline = time.monotonic() + STEP_TIMEOUT

    with subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) as chrome_process:
        while not (output.is_file() and output.read_bytes().rstrip().endswith(b"%%EOF")):
            if chrome_process.poll() is not None and not output.is_file():
                fail("Chrome exited without printing the PDF")

            if time.monotonic() > deadline:
                chrome_process.kill()
                fail(f"the print did not finish within {STEP_TIMEOUT} s")

            time.sleep(0.2)

        chrome_process.terminate()


def main() -> None:
    """Build the PDF, then check its page count."""

    chrome = find_chrome()

    with tempfile.TemporaryDirectory() as scratch:
        work = Path(scratch)
        text = replace_diagrams(SOURCE.read_text(encoding="utf-8"), work, chrome)
        body = markdown.markdown(text, extensions=["tables", "fenced_code"])
        body = inline_svgs(link_to_repository(body))

        page = '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Architecture Trade-Offs</title>'
        page += f"<style>{STYLE}</style></head><body>{body}</body></html>"
        html = work / "page.html"
        html.write_text(page, encoding="utf-8")

        output = work / "page.pdf"
        print_pdf(chrome, html, output, work / "chrome")
        pages = count_pages(output.read_bytes())
        shutil.copyfile(output, TARGET)

    print(f"{TARGET.relative_to(ROOT)}: {pages} pages")

    if not MIN_PAGES <= pages <= MAX_PAGES:
        fail(f"the brief bounds the PDF to {MIN_PAGES} to {MAX_PAGES} pages; it has {pages}")


if __name__ == "__main__":
    main()
