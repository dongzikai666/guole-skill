#!/usr/bin/env python3
"""Initialize an exam-study-coach workspace and subject."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


MATERIAL_DIRS = [
    "syllabus",
    "slides",
    "notes",
    "teacher-focus",
    "textbook-excerpts",
    "homework",
    "past-exams",
    "past-exam-answers",
    "user-mistakes",
    "public-links",
]

DEFAULT_CONFIG = {
    "setup_complete": False,
    "configured_at": "",
    "fast_mode": True,
    "response_style": "compact",
    "target_user": "undergraduate_or_graduate",
    "study_goal": "rapid_pass_or_short_term_mastery",
    "rank_style": "competitive",
    "reward_mode": "correct_answer_blind_box",
    "study_mode": "quiz",
    "score_goal": "pass_first",
    "pass_score": 60,
    "assessment_mode": "readiness_estimate",
    "source_priority": [
        "teacher_focus",
        "syllabus",
        "past_exams",
        "user_mistakes",
        "slides",
        "notes",
        "homework",
        "public_links",
    ],
    "mode": "live_tutor",
    "question_type": "mixed",
    "difficulty": "final_regular",
    "scope": "teacher_focus_then_core",
    "source_mode": "local_only",
    "past_exam_mode": "inspired_similar",
    "answer_mode": "one_by_one",
    "feedback": "grade_explain_then_ask",
    "web_search": "ask_each_time",
}


def slugify(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^\w]+", "-", text, flags=re.UNICODE)
    text = text.strip("-_")
    return text or "subject"


def write_once(path: Path, text: str, overwrite: bool = False) -> bool:
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def build_profile(title: str, subject_id: str, now: str) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            f"Subject id: `{subject_id}`",
            f"Created: {now}",
            "",
            "## Exam Context",
            "",
            "- Exam date: unknown",
            "- Target: pass-oriented",
            "- Question types: mixed",
            "- Current level: unknown",
            "",
            "## Material Placement",
            "",
            "- Put official scope in `materials/syllabus/`.",
            "- Put teacher-marked focus in `materials/teacher-focus/`.",
            "- Put past exams in `materials/past-exams/` for private study analysis.",
            "- Put your own wrong-answer notes in `materials/user-mistakes/`.",
            "",
        ]
    )


def initial_progress(title: str, subject_id: str, now: str) -> dict[str, object]:
    return {
        "title": title,
        "subject_id": subject_id,
        "total_xp": 0,
        "level": 1,
        "level_percent": 0,
        "title_label": "Bronze",
        "rank_name": "Bronze",
        "rank_short": "Brz",
        "attempt_count": 0,
        "answered_count": 0,
        "correct_count": 0,
        "partial_count": 0,
        "incorrect_count": 0,
        "reward_count": 0,
        "reward_counts": {},
        "reward_bonus_xp": 0,
        "box_points": 0,
        "latest_reward": None,
        "unlocked_modes": ["live_tutor", "memory"],
        "latest_unlocks": [],
        "latest_motivation": "",
        "exam_readiness": {
            "estimated_score_range": [0, 55],
            "pass_score": 60,
            "pass_risk": "unknown",
            "readiness": "not_enough_evidence",
            "basis": "no scored attempts yet",
            "most_likely_loss_points": [],
            "priority_review_order": [],
            "disclaimer": "Decision aid only; not an exact score prediction or pass guarantee.",
        },
        "knowledge_point_assessments": [],
        "pet_name": "Astra",
        "pet_stage": "Ember",
        "badges": [],
        "pet_mood": "Standby",
        "pet_energy": 0,
        "pet_focus": 0,
        "pet_bond": 0,
        "weak_points": [],
        "updated_at": now,
    }


def init_subject(args: argparse.Namespace) -> list[Path]:
    workspace = Path(args.workspace).resolve()
    subject_id = args.subject_id or slugify(args.title)
    subject = workspace / "subjects" / subject_id
    materials = subject / "materials"
    generated = subject / "generated"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    written: list[Path] = []
    for path in [workspace, workspace / "subjects", subject, materials, generated]:
        path.mkdir(parents=True, exist_ok=True)
    for dirname in MATERIAL_DIRS:
        (materials / dirname).mkdir(parents=True, exist_ok=True)

    files = {
        subject / "course-profile.md": build_profile(args.title, subject_id, now),
        subject / "config.json": json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2) + "\n",
        generated / "source-index.md": "# Source Index\n\nNo materials indexed yet.\n",
        generated / "focus-checklist.md": "# Focus Checklist\n\nNo focus checklist generated yet.\n",
        generated / "focus-checklist.json": "[]\n",
        generated / "knowledge-map.md": "# Knowledge Map\n\nNo knowledge units indexed yet.\n",
        generated / "question-bank.jsonl": "",
        generated / "session-log.jsonl": "",
        generated / "mastery-report.md": "# Mastery Report\n\nNo attempts yet.\n",
        generated / "exam-readiness.md": "# Exam Readiness\n\nNo attempts yet.\n",
        generated / "wrong-questions.md": "# Wrong Questions\n\nNo wrong questions exported yet.\n",
        generated / "progress-state.json": json.dumps(initial_progress(args.title, subject_id, now), ensure_ascii=False, indent=2) + "\n",
        workspace / "current-subject.txt": subject_id + "\n",
    }

    for path, text in files.items():
        if write_once(path, text, overwrite=args.overwrite or path.name == "current-subject.txt"):
            written.append(path)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize an exam coach subject workspace.")
    parser.add_argument("--title", required=True, help="Course or exam title.")
    parser.add_argument("--subject-id", default="", help="Stable subject id. Defaults to a slug from title.")
    parser.add_argument("--workspace", default="exam-coach-workspace", help="Workspace directory.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing subject metadata files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    written = init_subject(args)
    print("Initialized subject workspace.")
    for path in written:
        print(f"- {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
