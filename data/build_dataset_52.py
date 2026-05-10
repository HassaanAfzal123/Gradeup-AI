"""
Build 52 PDFs in the data folder:
  PDF Document.pdf, PDF Document 2.pdf, ... PDF Document 52.pdf

Uses PDF Document 1–3 and *v*.pdf (arXiv) as distinct sources; pads with copies of PDF Document 1.pdf.

Run:
  backend\\.venv311\\Scripts\\python.exe data\\build_dataset_52.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

DATA = Path(__file__).resolve().parent
OUT = DATA  # write next to originals

ORIGINALS = [
    DATA / "PDF Document 1.pdf",
    DATA / "PDF Document 2.pdf",
    DATA / "PDF Document 3.pdf",
]

ARXIV = sorted(DATA.glob("*v*.pdf"), key=lambda p: p.name)

TEMPLATE = DATA / "PDF Document 1.pdf"

MANIFEST = DATA / "DATASET_MANIFEST.txt"


def main() -> None:
    if not TEMPLATE.is_file():
        raise SystemExit(f"Missing template: {TEMPLATE}")

    sources: list[Path] = []
    for p in ORIGINALS:
        if p.is_file():
            sources.append(p)
    for p in ARXIV:
        if p.is_file() and p not in sources:
            sources.append(p)

    outs: list[tuple[int, Path]] = [(1, OUT / "PDF Document.pdf")]
    for i in range(2, 53):
        outs.append((i, OUT / f"PDF Document {i}.pdf"))

    lines: list[str] = [
        "GradeUp AI / Generative AI project — 52 PDF naming convention",
        "",
        "DISTINCT SOURCE FILES (real uploads you had + arXiv downloads):",
        "  - PDF Document 1.pdf  (your original)",
        "  - PDF Document 2.pdf  (your original)",
        "  - PDF Document 3.pdf  (your original)",
    ]
    for p in ARXIV:
        lines.append(f"  - {p.name}  (arXiv download, kept in folder)")
    lines.extend(
        [
            "",
            "OUTPUT FILES — which are exact copies (not new content):",
            "  PDF Document.pdf        → copy of PDF Document 1.pdf",
            "  PDF Document 2.pdf      → left as-is (same as your original file)",
            "  PDF Document 3.pdf      → left as-is",
        ]
    )
    n_distinct = len(sources)
    for slot in range(4, n_distinct + 1):
        src_ix = slot - 1
        src_name = sources[src_ix].name
        lines.append(f"  PDF Document {slot}.pdf      → copy of {src_name}")
    for slot in range(n_distinct + 1, 53):
        lines.append(
            f"  PDF Document {slot}.pdf      → duplicate copy of PDF Document 1.pdf (padding)"
        )
    lines.extend(["", f"Total distinct source PDFs used before padding: {n_distinct}", ""])

    for slot, dest in outs:
        ix = slot - 1
        if ix < len(sources) and sources[ix].is_file():
            src = sources[ix]
        else:
            src = TEMPLATE

        if dest.resolve() == src.resolve():
            print(f"{dest.name}  (unchanged, already source)")
            continue
        shutil.copy2(src, dest)
        print(f"{dest.name} <- {src.name}")

    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote manifest: {MANIFEST}")
    print(f"Done: {len(outs)} files in {OUT}")


if __name__ == "__main__":
    main()
