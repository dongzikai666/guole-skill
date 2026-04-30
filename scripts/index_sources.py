#!/usr/bin/env python3
"""Build a lightweight source index for a study subject."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


SOURCE_META = {
    "syllabus": ("official scope", "high", "scope and grading rules"),
    "teacher-focus": ("teacher focus", "highest", "priority and likely emphasis"),
    "past-exams": ("past exam", "high", "question style and private practice"),
    "past-exam-answers": ("past answer", "high", "private answer checking"),
    "slides": ("slides", "medium", "coverage and examples"),
    "notes": ("notes", "medium", "learner summary and gaps"),
    "textbook-excerpts": ("textbook excerpt", "medium", "concept repair"),
    "homework": ("homework", "medium", "practice style"),
    "user-mistakes": ("mistake record", "high", "weak-point targeting"),
    "public-links": ("public link", "variable", "public explanation and resources"),
}


def iter_material_files(materials: Path) -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    if not materials.exists():
        return files
    for folder in sorted(p for p in materials.iterdir() if p.is_dir()):
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                files.append((folder.name, path))
    return files


def relative(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def build_index(subject: Path) -> str:
    materials = subject / "materials"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    files = iter_material_files(materials)
    lines = [
        "# Source Index",
        "",
        f"Generated: {now}",
        f"Subject: `{subject.name}`",
        "",
        "| Path | Type | Reliability | Use | Size |",
        "| --- | --- | --- | --- | ---: |",
    ]
    if not files:
        lines.append("| - | none | - | Add files under `materials/` first. | 0 |")
    for folder, path in files:
        source_type, reliability, use = SOURCE_META.get(folder, ("material", "unknown", "supporting context"))
        lines.append(
            f"| `{relative(path, subject)}` | {source_type} | {reliability} | {use} | {path.stat().st_size} |"
        )
    lines.extend(
        [
            "",
            "## Source Weighting",
            "",
            "- `teacher-focus/` has the highest priority for emphasis.",
            "- `past-exams/` informs question style and difficulty, but should not be publicly redistributed.",
            "- `slides/` and `notes/` fill concept coverage.",
            "- `homework/` helps infer practice style.",
            "- `public-links/` and web search are supplemental explanations only.",
            "",
            "## Safety",
            "",
            "Keep teacher materials, past exams, answer keys, and student records private. Generate original similar questions when possible.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index source files for an exam coach subject.")
    parser.add_argument("--subject", required=True, help="Subject directory under exam-coach-workspace/subjects.")
    parser.add_argument("--output", default="", help="Output Markdown path. Defaults to subject/generated/source-index.md.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    subject = Path(args.subject).resolve()
    output = Path(args.output).resolve() if args.output else subject / "generated" / "source-index.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(build_index(subject) + "\n", encoding="utf-8")
    print(f"Wrote source index to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
