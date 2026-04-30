#!/usr/bin/env python3
"""Claude Code status line helper for GL Study Coach.

Modes:
- label: JSON output for claude-hud --extra-cmd.
- statusline: standalone multi-line study HUD.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path
from typing import Any

import quiz_session


QUOTES = [
    "One repaired mistake is real progress.",
    "Active recall beats passive rereading.",
    "Small drills compound before the exam.",
    "Weak points are maps, not verdicts.",
    "Review less, retrieve more.",
    "A short quiz today saves panic later.",
    "Turn mistakes into next quests.",
]


def find_attempts(explicit: str = "") -> Path | None:
    if explicit:
        path = Path(explicit).expanduser()
        return path if path.exists() else None

    env_path = os.environ.get("EXAM_STUDY_ATTEMPTS", "")
    if env_path:
        path = Path(env_path).expanduser()
        return path if path.exists() else None

    current = Path.cwd().resolve()
    for base in [current, *current.parents]:
        candidate = base / "study-pack" / "quizzes" / "attempts.jsonl"
        if candidate.exists():
            return candidate
    return None


def find_progress_state(explicit: str = "") -> Path | None:
    if explicit:
        path = Path(explicit).expanduser()
        return path if path.exists() else None

    env_path = os.environ.get("EXAM_STUDY_PROGRESS_STATE", "")
    if env_path:
        path = Path(env_path).expanduser()
        return path if path.exists() else None

    current = Path.cwd().resolve()
    for base in [current, *current.parents]:
        workspace = base / "exam-coach-workspace"
        current_subject = workspace / "current-subject.txt"
        if current_subject.exists():
            subject_id = current_subject.read_text(encoding="utf-8-sig").strip()
            candidate = workspace / "subjects" / subject_id / "generated" / "progress-state.json"
            if candidate.exists():
                return candidate
        candidate = base / "generated" / "progress-state.json"
        if candidate.exists():
            return candidate
    return None


def load_progress_state(path: Path | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_state(path: Path | None) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    if not path:
        return [], {}
    records = quiz_session.load_attempts(path)
    grouped = quiz_session.summarize(records)
    return records, grouped


def quote_for(level: int) -> str:
    index = (date.today().toordinal() + level) % len(QUOTES)
    return QUOTES[index]


def weak_count(grouped: dict[str, dict[str, Any]]) -> int:
    return sum(1 for item in grouped.values() if quiz_session.status_for(item) == "weak")


def label_text(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]]) -> str:
    if not records:
        return "GL Lv.1 0% | Pet Standby | First quiz"
    total_xp, level, _next_target, current_percent = quiz_session.progress_numbers(records)
    pet = quiz_session.pet_metrics(records, grouped)
    return f"GL Lv.{level} {current_percent}% | Pet {pet['mood']} | Weak {weak_count(grouped)}"


def label_from_state(state: dict[str, Any]) -> str:
    level = int(state.get("level") or 1)
    percent = int(state.get("level_percent") or 0)
    answered = int(state.get("answered_count") or 0)
    correct = int(state.get("correct_count") or 0)
    partial = int(state.get("partial_count") or 0)
    rank = "".join(str(state.get("rank_short") or state.get("title_label") or "Brz").split())[:4]
    pet = "".join(str(state.get("pet_stage") or state.get("pet_mood") or "Ember").split())[:7]
    weak = len(state.get("weak_points") or [])
    return f"EC {rank}{level} {percent}XP {percent}% A{answered} C{correct}/P{partial} W{weak} {pet}"


def statusline_text(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]]) -> str:
    total_xp, level, next_target, current_percent = quiz_session.progress_numbers(records)
    pet = quiz_session.pet_metrics(records, grouped)
    bar = quiz_session.progress_bar(current_percent, width=12)
    quest = quiz_session.next_quest(grouped)
    quote = quote_for(level)

    if not records:
        total_xp = 0
        level = 1
        next_target = 100
        current_percent = 0
        bar = "-" * 12
        pet = {
            "stage": "Spark",
            "mood": "Waiting",
            "energy": 0,
            "focus": 0,
            "bond": 0,
        }
        quest = "first diagnostic quiz"
        quote = quote_for(level)

    return "\n".join(
        [
            f"GL Lv.{level} {quiz_session.title_for(level)} | XP {total_xp}/{next_target} | [{bar}] {current_percent}%",
            f"Pet {pet['stage']}/{pet['mood']} | Energy {pet['energy']} | Focus {pet['focus']} | Bond {pet['bond']} | Weak {weak_count(grouped)}",
            f"Next: {quest} | {quote}",
        ]
    )


def statusline_from_state(state: dict[str, Any]) -> str:
    level = int(state.get("level") or 1)
    total_xp = int(state.get("total_xp") or 0)
    next_target = max(100, level * 100)
    percent = int(state.get("level_percent") or 0)
    title = str(state.get("title_label") or quiz_session.title_for(level))
    stage = str(state.get("pet_stage") or "Spark")
    mood = str(state.get("pet_mood") or "Waiting")
    energy = int(state.get("pet_energy") or 0)
    focus = int(state.get("pet_focus") or 0)
    bond = int(state.get("pet_bond") or 0)
    weak = len(state.get("weak_points") or [])
    answered = int(state.get("answered_count") or 0)
    correct = int(state.get("correct_count") or 0)
    partial = int(state.get("partial_count") or 0)
    incorrect = int(state.get("incorrect_count") or 0)
    quest = str(state.get("next_quest") or "first diagnostic quiz")
    quote = quote_for(level)
    return "\n".join(
        [
            f"GL {title} Lv.{level} | XP {total_xp}/{next_target} | [{quiz_session.progress_bar(percent, width=12)}] {percent}% | A{answered} C{correct}/P{partial}/I{incorrect}",
            f"Pet {stage}/{mood} | Energy {energy} | Focus {focus} | Bond {bond} | Weak {weak}",
            f"Next: {quest} | {quote}",
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render GL Study Coach status line output.")
    parser.add_argument("mode", choices=["label", "statusline"], help="Output mode.")
    parser.add_argument("--attempts", default="", help="Path to study-pack/quizzes/attempts.jsonl.")
    parser.add_argument("--state", default="", help="Path to generated/progress-state.json.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state = load_progress_state(find_progress_state(args.state))
    if state:
        if args.mode == "label":
            print(json.dumps({"label": label_from_state(state)}, ensure_ascii=False))
        else:
            print(statusline_from_state(state))
        return 0

    attempts = find_attempts(args.attempts)
    records, grouped = load_state(attempts)
    if args.mode == "label":
        print(json.dumps({"label": label_text(records, grouped)}, ensure_ascii=False))
    else:
        print(statusline_text(records, grouped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
