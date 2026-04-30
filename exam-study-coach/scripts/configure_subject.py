#!/usr/bin/env python3
"""Update subject config for a live tutor session."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


FIELDS = [
    "fast_mode",
    "response_style",
    "target_user",
    "study_goal",
    "rank_style",
    "reward_mode",
    "study_mode",
    "score_goal",
    "pass_score",
    "assessment_mode",
    "question_type",
    "difficulty",
    "scope",
    "source_mode",
    "past_exam_mode",
    "answer_mode",
    "feedback",
    "web_search",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update exam-study-coach subject config.")
    parser.add_argument("--subject", required=True, help="Subject directory under exam-coach-workspace/subjects.")
    parser.add_argument("--setup-complete", action="store_true", help="Mark question-session setup complete.")
    parser.add_argument("--reset-setup", action="store_true", help="Force question-session setup prompts again.")
    parser.add_argument("--slow-mode", action="store_true", help="Set fast_mode to false for more detailed replies.")
    for field in FIELDS:
        parser.add_argument(f"--{field.replace('_', '-')}", default="", help=f"Set {field}.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.subject).resolve() / "config.json"
    if not config_path.exists():
        raise SystemExit(f"Config not found: {config_path}")
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    for field in FIELDS:
        value = getattr(args, field)
        if value:
            if field == "fast_mode":
                config[field] = value.strip().lower() not in {"0", "false", "no", "off"}
            elif field == "pass_score":
                config[field] = int(value)
            else:
                config[field] = value
    if args.slow_mode:
        config["fast_mode"] = False
        config["response_style"] = "detailed"
    if args.setup_complete:
        config["setup_complete"] = True
        config["configured_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    if args.reset_setup:
        config["setup_complete"] = False
        config["configured_at"] = ""
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {config_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
