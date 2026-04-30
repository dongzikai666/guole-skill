#!/usr/bin/env python3
"""Create a reusable exam study-pack scaffold."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def render_template(name: str, values: dict[str, str]) -> str:
    template_path = skill_dir() / "assets" / "templates" / name
    text = template_path.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def write_once(path: Path, content: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def material_list(paths: list[str]) -> str:
    if not paths:
        return "- No source files listed yet.\n"
    lines = []
    for raw in paths:
        path = Path(raw)
        status = "exists" if path.exists() else "missing"
        lines.append(f"- `{raw}` ({status})")
    return "\n".join(lines) + "\n"


def build(args: argparse.Namespace) -> list[Path]:
    output = Path(args.output).resolve()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    values = {
        "title": args.title,
        "exam_date": args.exam_date or "unknown",
        "days": str(args.days),
        "generated_at": now,
    }

    files = {
        output / "source-summary.md": (
            f"# Source Summary: {args.title}\n\n"
            f"Generated: {now}\n\n"
            "## Materials\n\n"
            f"{material_list(args.materials)}\n"
            "## Short Summaries\n\n"
            "- Add one short paraphrased summary per source.\n"
        ),
        output / "knowledge-map.md": (
            f"# Knowledge Map: {args.title}\n\n"
            "| Unit | Priority | Evidence | Prerequisites | Must Know | Common Traps | Practice Style |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
            "| TBD | core | TBD | TBD | TBD | TBD | TBD |\n"
        ),
        output / "study-plan.md": render_template("study-plan.md", values),
        output / "mastery-report.md": render_template("mastery-report.md", values),
        output / "progress-card.md": render_template("progress-card.md", values),
        output / "pet-status.md": render_template("pet-status.md", values),
        output / "progress-state.json": json.dumps(
            {
                "title": args.title,
                "total_xp": 0,
                "level": 1,
                "title_label": "Starter",
                "pet_name": "Study Buddy",
                "pet_stage": "Spark",
                "badges": [],
                "pet_mood": "Waiting",
                "pet_energy": 0,
                "pet_focus": 0,
                "pet_bond": 0,
                "updated_at": now,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        output / "mistake-log.md": (
            f"# Mistake Log: {args.title}\n\n"
            "| Date | Question | Knowledge Point | Mistake Type | Cause | Fix | Follow-up Drill |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n"
        ),
        output / "quizzes" / "quiz-001.md": render_template("quiz.md", values),
        output / "quizzes" / "attempts.jsonl": "",
    }

    written = []
    for path, content in files.items():
        if write_once(path, content, args.overwrite):
            written.append(path)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create an exam study-pack scaffold.")
    parser.add_argument("--title", required=True, help="Course or exam title.")
    parser.add_argument("--days", type=int, default=14, help="Review window in days.")
    parser.add_argument("--exam-date", default="", help="Exam date if known.")
    parser.add_argument("--output", default="study-pack", help="Output directory.")
    parser.add_argument("--materials", nargs="*", default=[], help="Source file paths to list.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    written = build(args)
    if written:
        print("Created or updated:")
        for path in written:
            print(f"- {path}")
    else:
        print("No files changed. Use --overwrite to replace existing files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
