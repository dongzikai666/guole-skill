#!/usr/bin/env python3
"""Create quiz attempt skeletons and summarize mastery from JSONL attempts."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


QUESTION_HEADING = re.compile(r"^##\s+(Q[\w.-]+)\s*$", re.IGNORECASE)
FIELD = re.compile(r"^-\s*([a-zA-Z_]+)\s*:\s*(.*)\s*$")

DIFFICULTY_XP = {
    "easy": 10,
    "basic": 10,
    "medium": 20,
    "final_regular": 20,
    "hard": 35,
    "advanced": 35,
    "challenge": 50,
    "sprint": 50,
}

RANKS = [
    (30, "Legend", "Leg"),
    (25, "King", "King"),
    (20, "Master", "Mst"),
    (15, "Diamond", "Dia"),
    (10, "Platinum", "Plat"),
    (6, "Gold", "Gold"),
    (3, "Silver", "Sil"),
    (1, "Bronze", "Brz"),
]

REWARD_BOXES = [
    ("common", "Recall Coin", 1, 1, "Retry one old question."),
    ("common", "Focus Shard", 1, 1, "Mark one concept for retest."),
    ("common", "Formula Spark", 1, 1, "Do one formula recall."),
    ("rare", "Error Scanner", 3, 2, "Review one past mistake."),
    ("rare", "Sprint Token", 3, 2, "Unlock one timed mini-drill."),
    ("epic", "Diamond Key", 6, 4, "Promote one weak point into priority drill."),
    ("legendary", "King Star", 10, 8, "Take one boss-level mixed question when ready."),
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

MOTIVATION_LINES = {
    "correct": [
        "这题拿下了，说明这个考点已经开始站稳。",
        "答对不是运气，是你刚刚把一个得分点握住了。",
        "很好，继续把这种确定感搬到下一个考点。",
    ],
    "partial": [
        "半对也算推进，差的那一步就是下一次提分点。",
        "方向已经有了，现在把条件和步骤补齐就能拿分。",
        "这类题最怕模糊，你已经把模糊处照出来了。",
    ],
    "incorrect": [
        "错题不是退步，是定位雷区；现在修，考场就少丢分。",
        "先别急，这题暴露的问题很值钱，修掉就是净赚。",
        "今天错在练习里，比考场上错要划算得多。",
    ],
    "unscored": [
        "先把状态记下来，下一题继续校准。",
    ],
}

MICRO_STORIES = [
    "短故事：华罗庚早年靠自学和反复演算补基础，难题是一点点磨开的。",
    "短故事：爱迪生做过大量实验，把失败当作排除错误路径的证据。",
    "短故事：很多数学家证明定理前都要先撞上大量反例，反例会把思路磨尖。",
]


def parse_quiz(path: Path) -> list[dict[str, str]]:
    questions: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = QUESTION_HEADING.match(line.strip())
        if heading:
            if current:
                questions.append(current)
            current = {"question_id": heading.group(1)}
            continue
        if current:
            field = FIELD.match(line.strip())
            if field:
                current[field.group(1)] = field.group(2)
    if current:
        questions.append(current)
    return questions


def load_config(path: str = "") -> dict[str, Any]:
    if not path:
        return dict(DEFAULT_CONFIG)
    config_path = Path(path)
    if not config_path.exists():
        raise SystemExit(f"Config file not found: {config_path}")
    data = json.loads(config_path.read_text(encoding="utf-8-sig"))
    config = dict(DEFAULT_CONFIG)
    if isinstance(data, dict):
        config.update(data)
    return config


def config_value(config: dict[str, Any], key: str) -> str:
    return str(config.get(key) or DEFAULT_CONFIG.get(key) or "")


def init_attempts(args: argparse.Namespace) -> int:
    quiz_path = Path(args.quiz)
    questions = parse_quiz(quiz_path)
    config = load_config(args.config)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for question in questions:
            record = {
                "question_id": question.get("question_id", ""),
                "knowledge_point": question.get("knowledge_point", ""),
                "study_mode": question.get("study_mode", config_value(config, "study_mode")),
                "question_type": question.get("question_type", config_value(config, "question_type")),
                "difficulty": question.get("difficulty", config_value(config, "difficulty")),
                "scope": question.get("scope", config_value(config, "scope")),
                "source_mode": question.get("source_mode", config_value(config, "source_mode")),
                "past_exam_mode": question.get("past_exam_mode", config_value(config, "past_exam_mode")),
                "result": "unscored",
                "mistake_type": "",
                "notes": "",
            }
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Wrote {len(questions)} attempt record(s) to {output}")
    return 0


def load_attempts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for index, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON on line {index}: {exc}") from exc
    return records


def append_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def normalize_result(value: Any) -> str:
    text = str(value or "").strip().lower()
    if text in {"correct", "right", "yes", "true", "1", "remembered", "remember"}:
        return "correct"
    if text in {"partial", "hinted", "fuzzy"}:
        return "partial"
    if text in {"incorrect", "wrong", "no", "false", "0", "forgotten", "forget"}:
        return "incorrect"
    return "unscored"


def summarize(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"attempts": 0, "correct": 0, "partial": 0, "incorrect": 0, "mistakes": defaultdict(int)}
    )
    for record in records:
        point = str(record.get("knowledge_point") or "unspecified")
        result = normalize_result(record.get("result"))
        item = grouped[point]
        item["attempts"] += 1
        if result == "correct":
            item["correct"] += 1
        elif result == "partial":
            item["partial"] += 1
        elif result == "incorrect":
            item["incorrect"] += 1
            mistake = str(record.get("mistake_type") or "unspecified")
            item["mistakes"][mistake] += 1
    return grouped


def xp_for(record: dict[str, Any]) -> int:
    difficulty = str(record.get("difficulty") or "easy").strip().lower()
    base = DIFFICULTY_XP.get(difficulty, 10)
    result = normalize_result(record.get("result"))
    if result == "correct":
        return base
    if result == "partial":
        return max(1, round(base * 0.4))
    if result == "incorrect" and (record.get("mistake_type") or record.get("notes")):
        return 5
    return 0


def status_for(item: dict[str, Any]) -> str:
    attempts = item["attempts"]
    if attempts == 0:
        return "untested"
    score = item["correct"] + 0.5 * item["partial"]
    ratio = score / attempts
    if item["incorrect"] == 0 and attempts >= 2 and ratio >= 0.8:
        return "strong"
    if ratio >= 0.5:
        return "developing"
    return "weak"


def title_for(level: int) -> str:
    return rank_for(level)[0]


def rank_for(level: int) -> tuple[str, str]:
    for min_level, name, short in RANKS:
        if level >= min_level:
            return name, short
    return "Bronze", "Brz"


def pet_stage_for(level: int) -> str:
    if level >= 25:
        return "Mythic"
    if level >= 15:
        return "Aegis"
    if level >= 10:
        return "Vanguard"
    if level >= 6:
        return "Nova"
    if level >= 3:
        return "Pulse"
    return "Ember"


def pet_status(grouped: dict[str, dict[str, Any]]) -> tuple[str, str, str]:
    if not grouped:
        return ("Standby", "No scored attempts yet.", "Finish the first diagnostic quiz.")

    statuses = [status_for(item) for item in grouped.values()]
    strong = statuses.count("strong")
    developing = statuses.count("developing")
    weak = statuses.count("weak")
    attempts = sum(item["attempts"] for item in grouped.values())
    correctish = sum(item["correct"] + item["partial"] for item in grouped.values())
    ratio = correctish / attempts if attempts else 0

    if attempts == 0:
        return ("Standby", "No scored attempts yet.", "Finish the first diagnostic quiz.")
    if ratio >= 0.85 and attempts >= 3:
        return ("Overdrive", "Recent answers are highly stable.", "Try a boss-level mixed question.")
    if ratio >= 0.7 and attempts >= 2:
        return ("Charged", "Recent answers show stable progress.", "Try a harder mixed quiz.")
    if weak > strong:
        return ("Determined", "Weak points currently outnumber strong points.", "Repair one weak point before adding new material.")
    if developing > 0:
        return ("LockedIn", "Some points are close but still need practice.", "Retest developing points with medium questions.")
    return ("Standby", "More scored evidence is needed.", "Complete another short quiz.")


def pet_metrics(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]]) -> dict[str, Any]:
    scored = [record for record in records if normalize_result(record.get("result")) != "unscored"]
    statuses = [status_for(item) for item in grouped.values()]
    tested_points = len(statuses)
    non_weak = sum(1 for status in statuses if status != "weak")
    energy = min(100, len(scored) * 12)
    focus = round(100 * non_weak / tested_points) if tested_points else 0
    bond = min(100, len(records) * 5)
    total_xp, level, _next_target, _current_percent = progress_numbers(records)
    mood, reason, care = pet_status(grouped)
    return {
        "name": "Astra",
        "stage": pet_stage_for(level),
        "mood": mood,
        "reason": reason,
        "care_action": care,
        "energy": energy,
        "focus": focus,
        "bond": bond,
        "level": level,
        "total_xp": total_xp,
    }


def progress_numbers(records: list[dict[str, Any]]) -> tuple[int, int, int, int]:
    total_xp = sum(xp_for(record) + reward_bonus_for(record, index) for index, record in enumerate(records, start=1))
    level = total_xp // 100 + 1
    current_floor = (level - 1) * 100
    next_target = level * 100
    current_percent = total_xp - current_floor
    return total_xp, level, next_target, current_percent


def reward_for(record: dict[str, Any], index: int) -> dict[str, Any] | None:
    if normalize_result(record.get("result")) != "correct":
        return None
    seed = "|".join(
        [
            str(record.get("timestamp") or ""),
            str(record.get("question_id") or ""),
            str(record.get("knowledge_point") or ""),
            str(index),
        ]
    )
    score = sum(ord(char) for char in seed) % 100
    if score >= 97:
        rarity = "legendary"
    elif score >= 85:
        rarity = "epic"
    elif score >= 60:
        rarity = "rare"
    else:
        rarity = "common"
    pool = [item for item in REWARD_BOXES if item[0] == rarity]
    chosen = pool[score % len(pool)]
    return {
        "rarity": chosen[0],
        "name": chosen[1],
        "bonus_xp": chosen[2],
        "box_points": chosen[3],
        "effect": chosen[4],
    }


def reward_bonus_for(record: dict[str, Any], index: int) -> int:
    reward = reward_for(record, index)
    if not reward:
        return 0
    return int(reward.get("bonus_xp") or 0)


def reward_box_points_for(record: dict[str, Any], index: int) -> int:
    reward = reward_for(record, index)
    if not reward:
        return 0
    return int(reward.get("box_points") or 0)


def reward_summary(records: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, int], int, int, int]:
    counts: dict[str, int] = defaultdict(int)
    latest: dict[str, Any] | None = None
    total = 0
    bonus_xp = 0
    box_points = 0
    for index, record in enumerate(records, start=1):
        reward = reward_for(record, index)
        if reward:
            total += 1
            counts[reward["rarity"]] += 1
            bonus_xp += int(reward.get("bonus_xp") or 0)
            box_points += int(reward.get("box_points") or 0)
            latest = reward
    return latest, dict(counts), total, bonus_xp, box_points


def motivation_for(record: dict[str, Any], index: int) -> str:
    result = normalize_result(record.get("result"))
    pool = MOTIVATION_LINES.get(result) or MOTIVATION_LINES["unscored"]
    seed = f"{record.get('timestamp') or ''}|{record.get('knowledge_point') or ''}|{index}|{result}"
    score = sum(ord(char) for char in seed)
    message = pool[score % len(pool)]
    if result in {"partial", "incorrect"} and score % 3 == 0:
        message = f"{message} {MICRO_STORIES[score % len(MICRO_STORIES)]}"
    return message


def weak_point_details(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for index, point in enumerate(sorted(grouped), start=1):
        item = grouped[point]
        status = status_for(item)
        if status != "weak":
            continue
        point_records = [record for record in records if str(record.get("knowledge_point") or "unspecified") == point]
        mistake_counts: dict[str, int] = defaultdict(int)
        last_result = "unscored"
        last_notes = ""
        for record in point_records:
            result = normalize_result(record.get("result"))
            if result != "unscored":
                last_result = result
            if record.get("notes"):
                last_notes = str(record.get("notes"))
            if result in {"partial", "incorrect"}:
                mistake_counts[str(record.get("mistake_type") or "unspecified")] += 1
        details.append(
            {
                "id": f"WP{index:03d}",
                "knowledge_point": point,
                "attempts": item["attempts"],
                "correct": item["correct"],
                "partial": item["partial"],
                "incorrect": item["incorrect"],
                "last_result": last_result,
                "main_mistakes": dict(sorted(mistake_counts.items(), key=lambda pair: (-pair[1], pair[0]))),
                "last_notes": last_notes,
                "recommended_action": "one similar reinforcement question, then one transfer question",
            }
        )
    details.sort(key=lambda item: (-int(item["incorrect"]), -int(item["partial"]), str(item["knowledge_point"])))
    for index, item in enumerate(details, start=1):
        item["id"] = f"WP{index:03d}"
    return details


def source_weight_for(point_records: list[dict[str, Any]]) -> tuple[str, float]:
    joined = " ".join(
        str(record.get(key) or "")
        for record in point_records
        for key in ("scope", "source_mode", "past_exam_mode", "notes")
    ).lower()
    if "teacher" in joined or "focus" in joined:
        return "teacher_focus", 0.95
    if "past" in joined or "exam" in joined or "inspired" in joined:
        return "past_exam", 0.85
    if "syllabus" in joined or "scope" in joined:
        return "exam_scope", 0.80
    if "homework" in joined:
        return "homework", 0.65
    if "note" in joined or "slide" in joined:
        return "notes_or_slides", 0.60
    return "practice_record", 0.50


def point_importance_label(weight: float, status: str) -> str:
    if weight >= 0.85 or status == "weak":
        return "high"
    if weight >= 0.65 or status == "developing":
        return "medium"
    return "normal"


def point_advice(status: str, mistakes: dict[str, Any]) -> str:
    if status == "strong":
        return "keep with one mixed retest before the exam"
    if status == "developing":
        return "review the missing step, then answer one medium transfer question"
    mistake = next(iter(mistakes), "concept")
    return f"repair {mistake} first, then do two similar drills"


def point_assessments(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    assessments: list[dict[str, Any]] = []
    for index, point in enumerate(sorted(grouped), start=1):
        item = grouped[point]
        point_records = [record for record in records if str(record.get("knowledge_point") or "unspecified") == point]
        status = status_for(item)
        source_basis, weight = source_weight_for(point_records)
        mistakes = dict(sorted(item["mistakes"].items(), key=lambda pair: (-pair[1], pair[0])))
        assessments.append(
            {
                "id": f"KP{index:03d}",
                "knowledge_point": point,
                "status": status,
                "exam_importance": point_importance_label(weight, status),
                "source_basis": source_basis,
                "source_weight": round(weight, 2),
                "evidence_count": item["attempts"],
                "correct": item["correct"],
                "partial": item["partial"],
                "incorrect": item["incorrect"],
                "weak_reason": ", ".join(f"{name} x{count}" for name, count in mistakes.items()) if mistakes else "",
                "next_action": point_advice(status, mistakes),
            }
        )
    assessments.sort(
        key=lambda item: (
            {"weak": 0, "developing": 1, "untested": 2, "strong": 3}.get(str(item["status"]), 4),
            -float(item["source_weight"]),
            str(item["knowledge_point"]),
        )
    )
    return assessments


def int_config(config: dict[str, Any] | None, key: str, default: int) -> int:
    if not config:
        return default
    try:
        return int(config.get(key, default))
    except (TypeError, ValueError):
        return default


def exam_readiness(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]], config: dict[str, Any] | None = None) -> dict[str, Any]:
    results = [normalize_result(record.get("result")) for record in records]
    answered = sum(1 for result in results if result != "unscored")
    correct = results.count("correct")
    partial = results.count("partial")
    statuses = [status_for(item) for item in grouped.values()]
    strong = statuses.count("strong")
    developing = statuses.count("developing")
    weak = statuses.count("weak")
    tested_points = len(statuses)
    pass_score = int_config(config, "pass_score", 60)

    if answered == 0:
        return {
            "estimated_score_range": [0, min(pass_score, 55)],
            "pass_score": pass_score,
            "pass_risk": "unknown",
            "readiness": "not_enough_evidence",
            "basis": "no scored attempts yet",
            "most_likely_loss_points": [],
            "priority_review_order": [],
            "disclaimer": "Decision aid only; not an exact score prediction or pass guarantee.",
        }

    accuracy = (correct + 0.5 * partial) / answered
    coverage = min(1.0, tested_points / 6) if tested_points else 0
    weak_repair = 1.0 - (weak / tested_points) if tested_points else 0
    mid = round(100 * (0.62 * accuracy + 0.23 * coverage + 0.15 * weak_repair))
    uncertainty = 18 if answered < 5 else 12 if answered < 10 else 8
    low = max(0, mid - uncertainty)
    high = min(100, mid + uncertainty)
    if high < pass_score:
        risk = "high"
    elif low >= pass_score:
        risk = "low"
    else:
        risk = "medium"
    if mid >= max(85, pass_score + 20):
        readiness = "score_boosting"
    elif mid >= pass_score:
        readiness = "pass_possible"
    else:
        readiness = "needs_repair"

    weak_details = weak_point_details(records, grouped)
    likely_losses = [item["knowledge_point"] for item in weak_details[:5]]
    priority = likely_losses or [
        point
        for point, item in sorted(grouped.items(), key=lambda pair: pair[1]["attempts"])
        if status_for(item) != "strong"
    ][:5]
    return {
        "estimated_score_range": [low, high],
        "pass_score": pass_score,
        "pass_risk": risk,
        "readiness": readiness,
        "basis": f"answered={answered}, correct={correct}, partial={partial}, strong={strong}, developing={developing}, weak={weak}",
        "most_likely_loss_points": likely_losses,
        "priority_review_order": priority,
        "disclaimer": "Decision aid only; not an exact score prediction or pass guarantee.",
    }


def unlocked_modes_for(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]], level: int, box_points: int) -> list[str]:
    modes = ["live_tutor", "memory"]
    statuses = [status_for(item) for item in grouped.values()]
    weak_count = statuses.count("weak")
    strong_count = statuses.count("strong")
    has_past_exam_signal = any(
        "past" in str(record.get("past_exam_mode") or "").lower()
        or "inspired" in str(record.get("past_exam_mode") or "").lower()
        or "past" in str(record.get("scope") or "").lower()
        or "exam" in str(record.get("source_mode") or "").lower()
        for record in records
    )
    if weak_count > 0 or level >= 2:
        modes.append("weak_point_attack")
    if has_past_exam_signal and (level >= 3 or box_points >= 10):
        modes.append("mock_exam")
    if level >= 5 or strong_count >= 3:
        modes.append("boss_mixed")
    return modes


def latest_unlocks_for(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]], level: int, box_points: int) -> list[str]:
    if not records:
        return []
    previous = records[:-1]
    previous_grouped = summarize(previous)
    _prev_xp, prev_level, _prev_next, _prev_percent = progress_numbers(previous)
    _prev_latest, _prev_counts, _prev_total, _prev_bonus, prev_points = reward_summary(previous)
    old_modes = set(unlocked_modes_for(previous, previous_grouped, prev_level, prev_points))
    new_modes = set(unlocked_modes_for(records, grouped, level, box_points))
    return sorted(new_modes - old_modes)


def progress_state(
    records: list[dict[str, Any]],
    title: str = "",
    subject_id: str = "",
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    grouped = summarize(records)
    total_xp, level, _next_target, current_percent = progress_numbers(records)
    rank_name, rank_short = rank_for(level)
    pet = pet_metrics(records, grouped)
    weak_points = [point for point, item in grouped.items() if status_for(item) == "weak"]
    results = [normalize_result(record.get("result")) for record in records]
    answered_count = sum(1 for result in results if result != "unscored")
    correct_count = results.count("correct")
    partial_count = results.count("partial")
    incorrect_count = results.count("incorrect")
    latest_reward, reward_counts, reward_count, reward_bonus_xp, box_points = reward_summary(records)
    weak_details = weak_point_details(records, grouped)
    unlocked_modes = unlocked_modes_for(records, grouped, level, box_points)
    latest_unlocks = latest_unlocks_for(records, grouped, level, box_points)
    latest_motivation = motivation_for(records[-1], len(records)) if records else ""
    readiness = exam_readiness(records, grouped, config)
    return {
        "title": title,
        "subject_id": subject_id,
        "total_xp": total_xp,
        "level": level,
        "level_percent": current_percent,
        "title_label": rank_name,
        "rank_name": rank_name,
        "rank_short": rank_short,
        "attempt_count": len(records),
        "answered_count": answered_count,
        "correct_count": correct_count,
        "partial_count": partial_count,
        "incorrect_count": incorrect_count,
        "reward_count": reward_count,
        "reward_counts": reward_counts,
        "reward_bonus_xp": reward_bonus_xp,
        "box_points": box_points,
        "latest_reward": latest_reward,
        "unlocked_modes": unlocked_modes,
        "latest_unlocks": latest_unlocks,
        "latest_motivation": latest_motivation,
        "exam_readiness": readiness,
        "knowledge_point_assessments": point_assessments(records, grouped),
        "badges": badges_for(records, grouped),
        "pet_name": pet["name"],
        "pet_stage": pet["stage"],
        "pet_mood": pet["mood"],
        "pet_energy": pet["energy"],
        "pet_focus": pet["focus"],
        "pet_bond": pet["bond"],
        "weak_points": weak_points,
        "weak_point_details": weak_details,
        "review_order": [item["id"] for item in weak_details],
        "next_quest": next_quest(grouped),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def write_progress_state(
    path: Path,
    records: list[dict[str, Any]],
    title: str = "",
    subject_id: str = "",
    config: dict[str, Any] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(progress_state(records, title=title, subject_id=subject_id, config=config), ensure_ascii=False, indent=2)
    path.write_text(payload + "\n", encoding="utf-8")


def progress_bar(percent: int, width: int = 10) -> str:
    percent = max(0, min(100, percent))
    filled = round(width * percent / 100)
    return "#" * filled + "-" * (width - filled)


def next_quest(grouped: dict[str, dict[str, Any]]) -> str:
    weakest = [point for point, item in grouped.items() if status_for(item) == "weak"]
    if weakest:
        return f"repair {weakest[0]}"
    return "complete a mixed quiz"


def hud_line(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]]) -> str:
    total_xp, level, next_target, current_percent = progress_numbers(records)
    pet = pet_metrics(records, grouped)
    weak_count = sum(1 for item in grouped.values() if status_for(item) == "weak")
    bar = progress_bar(current_percent)
    return (
        f"[ExamCoach] Lv.{level} {title_for(level)} | XP {total_xp}/{next_target} | "
        f"[{bar}] {current_percent}% | Pet {pet['stage']}/{pet['mood']} | Weak {weak_count} | Next: {next_quest(grouped)}"
    )


def badges_for(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]]) -> list[str]:
    badges: list[str] = []
    scored = [record for record in records if normalize_result(record.get("result")) != "unscored"]
    incorrect_with_type = [
        record
        for record in records
        if normalize_result(record.get("result")) == "incorrect" and record.get("mistake_type")
    ]
    if scored:
        badges.append("First Quiz")
    if len(incorrect_with_type) >= 3:
        badges.append("Mistake Hunter")
    if len(grouped) >= 3 and len(scored) >= 5:
        badges.append("Mixed Practice")
    if len(scored) >= 5 and all(normalize_result(record.get("result")) == "correct" for record in scored[-5:]):
        badges.append("Stable Recall")
    return badges


def progress_markdown(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    total_xp, level, next_target, current_percent = progress_numbers(records)
    xp_to_next = 100 - (total_xp % 100)
    pet = pet_metrics(records, grouped)
    badges = badges_for(records, grouped)
    quest = next_quest(grouped)
    latest_reward, reward_counts, reward_count, reward_bonus_xp, box_points = reward_summary(records)
    unlocked_modes = unlocked_modes_for(records, grouped, level, box_points)
    readiness = exam_readiness(records, grouped)

    badge_lines = "\n".join(f"- {badge}" for badge in badges) if badges else "- None yet."
    reward_lines = [
        f"- Blind boxes opened: {reward_count}",
        f"- Reward bonus XP: {reward_bonus_xp}",
        f"- Box points: {box_points}",
        f"- Latest reward: {latest_reward['rarity']} {latest_reward['name']}" if latest_reward else "- Latest reward: none",
        "- Reward counts: "
        + (", ".join(f"{rarity} x{count}" for rarity, count in sorted(reward_counts.items())) or "none"),
    ]
    unlock_lines = "\n".join(f"- {mode}" for mode in unlocked_modes) if unlocked_modes else "- None yet."
    return "\n".join(
        [
            "# Progress Card",
            "",
            f"Generated: {now}",
            "",
            "## Level",
            "",
            f"- Total XP: {total_xp}",
            f"- Level: {level}",
            f"- Title: {title_for(level)}",
            f"- Progress: [{progress_bar(current_percent)}] {current_percent}% to level {level + 1}",
            f"- XP to next level: {xp_to_next}",
            f"- HUD: `{hud_line(records, grouped)}`",
            "",
            "## Rewards",
            "",
            *reward_lines,
            "",
            "## Unlocked Modes",
            "",
            unlock_lines,
            "",
            "## Badges",
            "",
            badge_lines,
            "",
            "## Study Pet",
            "",
            f"- Name: {pet['name']}",
            f"- Stage: {pet['stage']}",
            f"- Mood: {pet['mood']}",
            f"- Why: {pet['reason']}",
            f"- Energy: [{progress_bar(pet['energy'])}] {pet['energy']}",
            f"- Focus: [{progress_bar(pet['focus'])}] {pet['focus']}",
            f"- Bond: [{progress_bar(pet['bond'])}] {pet['bond']}",
            f"- Care action: {pet['care_action']}",
            "",
            "## Next Quest",
            "",
            f"- {quest}",
            "",
            "## Exam Readiness",
            "",
            f"- Estimated score range: {readiness['estimated_score_range'][0]}-{readiness['estimated_score_range'][1]}",
            f"- Pass score: {readiness['pass_score']}",
            f"- Pass risk: {readiness['pass_risk']}",
            f"- Readiness: {readiness['readiness']}",
            f"- Basis: {readiness['basis']}",
            f"- Disclaimer: {readiness['disclaimer']}",
            "",
        ]
    )


def exam_readiness_markdown(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]], config: dict[str, Any] | None = None) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    readiness = exam_readiness(records, grouped, config)
    losses = readiness["most_likely_loss_points"] or ["none yet"]
    priority = readiness["priority_review_order"] or ["complete more scored attempts"]
    return "\n".join(
        [
            "# Exam Readiness",
            "",
            f"Generated: {now}",
            "",
            "## Score Estimate",
            "",
            f"- Estimated score range: {readiness['estimated_score_range'][0]}-{readiness['estimated_score_range'][1]}",
            f"- Pass score: {readiness['pass_score']}",
            f"- Pass risk: {readiness['pass_risk']}",
            f"- Readiness: {readiness['readiness']}",
            f"- Basis: {readiness['basis']}",
            "",
            "## Most Likely Loss Points",
            "",
            *[f"- {point}" for point in losses],
            "",
            "## Priority Review Order",
            "",
            *[f"- {point}" for point in priority],
            "",
            "## Boundary",
            "",
            f"- {readiness['disclaimer']}",
            "",
        ]
    )


def pet_markdown(records: list[dict[str, Any]], grouped: dict[str, dict[str, Any]]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    pet = pet_metrics(records, grouped)
    return "\n".join(
        [
            "# Study Pet",
            "",
            f"Generated: {now}",
            "",
            f"- Name: {pet['name']}",
            f"- Stage: {pet['stage']}",
            f"- Mood: {pet['mood']}",
            f"- Why: {pet['reason']}",
            f"- Energy: [{progress_bar(pet['energy'])}] {pet['energy']}",
            f"- Focus: [{progress_bar(pet['focus'])}] {pet['focus']}",
            f"- Bond: [{progress_bar(pet['bond'])}] {pet['bond']}",
            f"- Care action: {pet['care_action']}",
            "",
        ]
    )


def pet(args: argparse.Namespace) -> int:
    records = load_attempts(Path(args.attempts))
    grouped = summarize(records)
    text = pet_markdown(records, grouped)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"Wrote pet status to {output}")
    else:
        print(text)
    return 0


def hud(args: argparse.Namespace) -> int:
    records = load_attempts(Path(args.attempts))
    grouped = summarize(records)
    line = hud_line(records, grouped)
    print(line)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(line + "\n", encoding="utf-8")
    return 0


def report(args: argparse.Namespace) -> int:
    attempts_path = Path(args.attempts)
    records = load_attempts(attempts_path)
    grouped = summarize(records)
    config = load_config(args.config) if args.config else {}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "# Mastery Report",
        "",
        f"Generated: {now}",
        f"Source attempts: `{attempts_path}`",
    ]
    if config:
        lines.extend(
            [
                "",
                "## Session Config",
                "",
                f"- Question type: {config_value(config, 'question_type')}",
                f"- Difficulty: {config_value(config, 'difficulty')}",
                f"- Scope: {config_value(config, 'scope')}",
                f"- Source mode: {config_value(config, 'source_mode')}",
                f"- Past exam mode: {config_value(config, 'past_exam_mode')}",
            ]
        )
    readiness = exam_readiness(records, grouped, config)
    assessments = point_assessments(records, grouped)
    lines.extend(
        [
            "",
            "## Exam Readiness",
            "",
            f"- Estimated score range: {readiness['estimated_score_range'][0]}-{readiness['estimated_score_range'][1]}",
            f"- Pass score: {readiness['pass_score']}",
            f"- Pass risk: {readiness['pass_risk']}",
            f"- Readiness: {readiness['readiness']}",
            f"- Basis: {readiness['basis']}",
            f"- Boundary: {readiness['disclaimer']}",
            "",
            "## Knowledge Point Assessment",
            "",
            "| ID | Knowledge Point | Importance | Source | Weight | Status | Evidence | Correct | Partial | Incorrect | Weak Reason | Next Action |",
            "| --- | --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | --- | --- |",
        ]
    )
    for item in assessments:
        weak_reason = item["weak_reason"] or "-"
        lines.append(
            f"| {item['id']} | {item['knowledge_point']} | {item['exam_importance']} | {item['source_basis']} | "
            f"{item['source_weight']} | {item['status']} | {item['evidence_count']} | {item['correct']} | "
            f"{item['partial']} | {item['incorrect']} | {weak_reason} | {item['next_action']} |"
        )
    lines.extend(
        [
            "",
            "## Most Likely Loss Points",
            "",
            *[f"- {point}" for point in (readiness["most_likely_loss_points"] or ["none yet"])],
            "",
            "## Next Actions",
            "",
            *[f"- {point}" for point in (readiness["priority_review_order"] or ["complete more scored attempts"])],
            "- Drill weak points first, then retest developing points with medium mixed questions.",
        ]
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote mastery report to {output}")
    if args.progress_output:
        progress_output = Path(args.progress_output)
        progress_output.parent.mkdir(parents=True, exist_ok=True)
        progress_output.write_text(progress_markdown(records, grouped), encoding="utf-8")
        print(f"Wrote progress card to {progress_output}")
    if args.readiness_output:
        readiness_output = Path(args.readiness_output)
        readiness_output.parent.mkdir(parents=True, exist_ok=True)
        readiness_output.write_text(exam_readiness_markdown(records, grouped, config), encoding="utf-8")
        print(f"Wrote exam readiness report to {readiness_output}")
    return 0


def mistake_markdown(records: list[dict[str, Any]], title: str = "") -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    problem_records = [
        record for record in records if normalize_result(record.get("result")) in {"partial", "incorrect"}
    ]
    grouped = summarize(records)
    weak_details = weak_point_details(records, grouped)
    lines = [
        "# Wrong Questions",
        "",
        f"Generated: {now}",
        f"Subject: {title or 'unknown'}",
        "",
        "## Weak Points",
        "",
    ]
    if not weak_details:
        lines.append("- No weak points detected yet.")
    for item in weak_details:
        mistakes = ", ".join(f"{name} x{count}" for name, count in item["main_mistakes"].items()) or "-"
        lines.append(
            f"- `{item['id']}` {item['knowledge_point']} - attempts {item['attempts']}, "
            f"partial {item['partial']}, incorrect {item['incorrect']}, mistakes: {mistakes}."
        )
    lines.extend(["", "## Mistake Log", ""])
    if not problem_records:
        lines.append("- No partial or incorrect answers recorded yet.")
    for index, record in enumerate(problem_records, start=1):
        lines.extend(
            [
                f"### M{index:03d} - {record.get('knowledge_point') or 'unspecified'}",
                "",
                f"- Result: {normalize_result(record.get('result'))}",
                f"- Question type: {record.get('question_type') or '-'}",
                f"- Difficulty: {record.get('difficulty') or '-'}",
                f"- Mistake type: {record.get('mistake_type') or '-'}",
                f"- Notes: {record.get('notes') or '-'}",
                f"- Next drill: one similar question, then one transfer question.",
                "",
            ]
        )
    return "\n".join(lines)


def write_simple_pdf(markdown_text: str, output: Path) -> bool:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        return False

    output.parent.mkdir(parents=True, exist_ok=True)
    page_width, page_height = A4
    c = canvas.Canvas(str(output), pagesize=A4)
    y = page_height - 48
    for line in markdown_text.splitlines():
        text = line.replace("#", "").strip()
        if not text:
            y -= 10
            continue
        c.drawString(48, y, text[:110])
        y -= 16
        if y < 48:
            c.showPage()
            y = page_height - 48
    c.save()
    return True


def export_mistakes(args: argparse.Namespace) -> int:
    records = load_attempts(Path(args.attempts))
    text = mistake_markdown(records, title=args.title)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text + "\n", encoding="utf-8")
    print(f"Wrote wrong-question Markdown to {output}")

    if args.pdf_output:
        pdf_output = Path(args.pdf_output)
        if write_simple_pdf(text, pdf_output):
            print(f"Wrote wrong-question PDF to {pdf_output}")
        else:
            print("PDF skipped: reportlab is not installed. Use the pdf skill or install reportlab, then rerun.")
    return 0


def record(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    raw_result = str(args.result or "").strip().lower()
    normalized_result = normalize_result(raw_result)
    study_mode = args.study_mode or config_value(config, "study_mode") or "quiz"
    record_data = {
        "timestamp": now,
        "question_id": args.question_id,
        "knowledge_point": args.knowledge_point,
        "study_mode": study_mode,
        "question_type": args.question_type or config_value(config, "question_type"),
        "difficulty": args.difficulty or config_value(config, "difficulty"),
        "scope": args.scope or config_value(config, "scope"),
        "source_mode": args.source_mode or config_value(config, "source_mode"),
        "past_exam_mode": args.past_exam_mode or config_value(config, "past_exam_mode"),
        "result": normalized_result,
        "mistake_type": args.mistake_type,
        "notes": args.notes,
    }
    if raw_result in {"remembered", "fuzzy", "forgotten"} or study_mode == "memory":
        record_data["memory_result"] = raw_result or normalized_result

    attempts_path = Path(args.attempts)
    append_record(attempts_path, record_data)
    print(f"Appended attempt to {attempts_path}")

    if args.session_log and Path(args.session_log) != attempts_path:
        append_record(Path(args.session_log), record_data)
        print(f"Appended session log to {args.session_log}")

    if args.progress_output:
        records = load_attempts(attempts_path)
        write_progress_state(Path(args.progress_output), records, title=args.title, subject_id=args.subject_id, config=config)
        print(f"Wrote progress state to {args.progress_output}")
        reward = reward_for(record_data, len(records))
        if reward:
            print(
                "Opened blind box: "
                f"{reward['rarity']} {reward['name']} (+{reward['bonus_xp']} bonus XP, "
                f"+{reward['box_points']} box points) - {reward['effect']}"
            )
        print(f"Motivation: {motivation_for(record_data, len(records))}")
        state = progress_state(records, title=args.title, subject_id=args.subject_id, config=config)
        if state["latest_unlocks"]:
            print("Unlocked: " + ", ".join(state["latest_unlocks"]))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage exam quiz sessions.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a JSONL attempt skeleton from a quiz Markdown file.")
    init_parser.add_argument("--quiz", required=True, help="Quiz Markdown file.")
    init_parser.add_argument("--output", required=True, help="Output JSONL attempt file.")
    init_parser.add_argument("--config", default="", help="Optional subject config.json.")
    init_parser.set_defaults(func=init_attempts)

    hud_parser = subparsers.add_parser("hud", help="Print a compact HUD-style progress line.")
    hud_parser.add_argument("--attempts", required=True, help="JSONL attempt file.")
    hud_parser.add_argument("--output", default="", help="Optional output text file.")
    hud_parser.set_defaults(func=hud)

    pet_parser = subparsers.add_parser("pet", help="Write a detailed study-pet companion card.")
    pet_parser.add_argument("--attempts", required=True, help="JSONL attempt file.")
    pet_parser.add_argument("--output", default="", help="Optional output Markdown file.")
    pet_parser.set_defaults(func=pet)

    report_parser = subparsers.add_parser("report", help="Summarize mastery from a JSONL attempt file.")
    report_parser.add_argument("--attempts", required=True, help="JSONL attempt file.")
    report_parser.add_argument("--output", required=True, help="Output Markdown report.")
    report_parser.add_argument("--progress-output", default="", help="Optional progress-card Markdown output.")
    report_parser.add_argument("--readiness-output", default="", help="Optional exam-readiness Markdown output.")
    report_parser.add_argument("--config", default="", help="Optional subject config.json.")
    report_parser.set_defaults(func=report)

    export_parser = subparsers.add_parser("export-mistakes", help="Export partial/incorrect attempts.")
    export_parser.add_argument("--attempts", required=True, help="JSONL attempt file.")
    export_parser.add_argument("--output", required=True, help="Output Markdown file.")
    export_parser.add_argument("--pdf-output", default="", help="Optional PDF output file.")
    export_parser.add_argument("--title", default="", help="Subject title.")
    export_parser.set_defaults(func=export_mistakes)

    record_parser = subparsers.add_parser("record", help="Append one graded live-tutor attempt and refresh progress.")
    record_parser.add_argument("--attempts", required=True, help="JSONL attempt file, usually generated/session-log.jsonl.")
    record_parser.add_argument("--config", default="", help="Optional subject config.json.")
    record_parser.add_argument("--session-log", default="", help="Optional second JSONL log path.")
    record_parser.add_argument("--progress-output", default="", help="Optional progress-state JSON output.")
    record_parser.add_argument("--title", default="", help="Course title for progress state.")
    record_parser.add_argument("--subject-id", default="", help="Subject id for progress state.")
    record_parser.add_argument("--question-id", default="", help="Question id.")
    record_parser.add_argument("--knowledge-point", required=True, help="Knowledge point tested.")
    record_parser.add_argument("--question-type", default="", help="Question type override.")
    record_parser.add_argument("--difficulty", default="", help="Difficulty override.")
    record_parser.add_argument("--scope", default="", help="Scope override.")
    record_parser.add_argument("--source-mode", default="", help="Source mode override.")
    record_parser.add_argument("--past-exam-mode", default="", help="Past exam mode override.")
    record_parser.add_argument(
        "--result",
        required=True,
        help="correct, partial, incorrect, unscored, remembered, fuzzy, or forgotten.",
    )
    record_parser.add_argument("--study-mode", default="", help="quiz or memory.")
    record_parser.add_argument("--mistake-type", default="", help="Mistake type.")
    record_parser.add_argument("--notes", default="", help="Short notes.")
    record_parser.set_defaults(func=record)

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
