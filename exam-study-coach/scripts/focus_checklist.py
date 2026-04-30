#!/usr/bin/env python3
"""Build a focus checklist from subject materials and progress state."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


SOURCE_WEIGHTS = {
    "teacher-focus": 100,
    "syllabus": 90,
    "past-exams": 82,
    "past-exam-answers": 78,
    "user-mistakes": 76,
    "homework": 64,
    "slides": 58,
    "notes": 54,
    "textbook-excerpts": 48,
    "public-links": 28,
}

QUESTION_HINTS = {
    "teacher-focus": "short_answer",
    "syllabus": "mixed",
    "past-exams": "past_exam_inspired",
    "past-exam-answers": "calculation_or_short_answer",
    "user-mistakes": "reinforcement",
    "homework": "calculation_or_application",
    "slides": "concept_check",
    "notes": "blank_or_short_answer",
    "textbook-excerpts": "concept_explanation",
    "public-links": "concept_check",
}


def normalize_topic(text: str) -> str:
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or "core topic"


def iter_material_files(subject: Path) -> list[tuple[str, Path]]:
    materials = subject / "materials"
    if not materials.exists():
        return []
    files: list[tuple[str, Path]] = []
    for folder in sorted(path for path in materials.iterdir() if path.is_dir()):
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                files.append((folder.name, path))
    return files


def load_progress(subject: Path) -> dict[str, Any]:
    path = subject / "generated" / "progress-state.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def topic_rows(subject: Path) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for folder, path in iter_material_files(subject):
        topic = normalize_topic(path.stem)
        row = grouped.setdefault(
            topic.lower(),
            {
                "topic": topic,
                "score": 0,
                "sources": [],
                "basis": set(),
                "question_types": set(),
            },
        )
        row["score"] += SOURCE_WEIGHTS.get(folder, 30)
        row["sources"].append((folder, path))
        row["basis"].add(folder)
        row["question_types"].add(QUESTION_HINTS.get(folder, "mixed"))

    progress = load_progress(subject)
    for index, item in enumerate(progress.get("weak_point_details") or [], start=1):
        topic = normalize_topic(str(item.get("knowledge_point") or f"weak point {index}"))
        row = grouped.setdefault(
            topic.lower(),
            {
                "topic": topic,
                "score": 0,
                "sources": [],
                "basis": set(),
                "question_types": set(),
            },
        )
        row["score"] += 95
        row["basis"].add("weak-point")
        row["question_types"].add("reinforcement")

    rows = list(grouped.values())
    if not rows:
        rows.append(
            {
                "topic": "First diagnostic topic",
                "score": 10,
                "sources": [],
                "basis": {"manual"},
                "question_types": {"mixed"},
            }
        )
    rows.sort(key=lambda item: (-int(item["score"]), str(item["topic"]).lower()))
    return rows


def priority_for(score: int) -> str:
    if score >= 150:
        return "S"
    if score >= 90:
        return "A"
    if score >= 55:
        return "B"
    return "C"


def mastery_for(topic: str, progress: dict[str, Any]) -> str:
    for item in progress.get("weak_point_details") or []:
        if str(item.get("knowledge_point") or "").lower() == topic.lower():
            return "weak"
    return "untested"


def serializable(rows: list[dict[str, Any]], progress: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    output = []
    for index, row in enumerate(rows[:limit], start=1):
        score = int(row["score"])
        basis = sorted(str(item) for item in row["basis"])
        output.append(
            {
                "id": f"KP{index:03d}",
                "topic": row["topic"],
                "priority": priority_for(score),
                "score": score,
                "source_basis": basis,
                "suggested_question_type": sorted(str(item) for item in row["question_types"])[0],
                "mastery": mastery_for(str(row["topic"]), progress),
            }
        )
    return output


def markdown(items: list[dict[str, Any]], subject: Path) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Focus Checklist",
        "",
        f"Generated: {now}",
        f"Subject: `{subject.name}`",
        "",
        "| ID | Priority | Topic | Basis | Suggested Type | Mastery |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        basis = ", ".join(item["source_basis"])
        lines.append(
            f"| {item['id']} | {item['priority']} | {item['topic']} | {basis} | "
            f"{item['suggested_question_type']} | {item['mastery']} |"
        )
    lines.extend(
        [
            "",
            "Use: choose a focus ID such as `KP001`, then ask one live tutor question for that topic.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an exam focus checklist for a subject.")
    parser.add_argument("--subject", required=True, help="Subject directory under exam-coach-workspace/subjects.")
    parser.add_argument("--limit", type=int, default=12, help="Maximum checklist items.")
    parser.add_argument("--output", default="", help="Markdown output path.")
    parser.add_argument("--json-output", default="", help="JSON output path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    subject = Path(args.subject).resolve()
    progress = load_progress(subject)
    items = serializable(topic_rows(subject), progress, max(1, args.limit))

    md_output = Path(args.output).resolve() if args.output else subject / "generated" / "focus-checklist.md"
    json_output = (
        Path(args.json_output).resolve() if args.json_output else subject / "generated" / "focus-checklist.json"
    )
    md_output.parent.mkdir(parents=True, exist_ok=True)
    md_output.write_text(markdown(items, subject) + "\n", encoding="utf-8")
    json_output.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote focus checklist to {md_output}")
    print(f"Wrote focus checklist JSON to {json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
