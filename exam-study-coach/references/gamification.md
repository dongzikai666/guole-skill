# Gamification

Use this reference when the user wants a level system, XP, badges, streaks, a study pet, or any game-like learning feedback.

## Purpose

Gamification should make progress visible and encourage repair of weak points. It must not hide the actual mastery diagnosis.

## XP Model

Award XP from quiz evidence:

- Easy correct: 10 XP
- Medium correct: 20 XP
- Hard correct: 35 XP
- Challenge correct: 50 XP
- Partial answer: 40 percent of the correct XP
- Incorrect answer with a clear mistake type or notes: 5 reflection XP
- Unscored answer: 0 XP

Level formula:

- Level starts at 1.
- Every 100 XP gives one level.
- Show current-level XP as `total_xp % 100`.

## Mastery Titles

Use titles as encouragement, not certification:

- Level 1-2: Bronze
- Level 3-5: Silver
- Level 6-9: Gold
- Level 10-14: Platinum
- Level 15-19: Diamond
- Level 20-24: Master
- Level 25-29: King
- Level 30+: Legend

Short HUD labels:

- `Brz`, `Sil`, `Gold`, `Plat`, `Dia`, `Mst`, `King`, `Leg`

## Blind-Box Rewards

Open one reward only after a correct answer. Keep it short and deterministic from the attempt record so repeated report generation does not create duplicate rewards.

Rewards have real lightweight effects:

- `bonus_xp`: added to total XP and can help level up.
- `box_points`: unlocks stage modes such as weak-point attack and mock exam.
- `effect`: a suggested next action or perk.

Rewards must not change correctness, weak-point status, or mastery labels. Mastery still comes from answer evidence.

Reward rarities:

- `common`: Recall Coin, Focus Shard, Formula Spark. +1 bonus XP, +1 box point.
- `rare`: Error Scanner, Sprint Token. +3 bonus XP, +2 box points.
- `epic`: Diamond Key. +6 bonus XP, +4 box points.
- `legendary`: King Star. +10 bonus XP, +8 box points.

Reward output format:

```text
Blind box: rare Sprint Token (+3 bonus XP, +2 box points) - Unlock one timed mini-drill.
```

Do not award blind boxes for partial or incorrect answers. Those can still earn reflection XP.

## Stage Unlocks

Default unlocks:

- `live_tutor` and `memory`: always available.
- `weak_point_attack`: unlock when any weak point appears or level reaches 2.
- `mock_exam`: unlock when past-exam evidence exists and level reaches 3 or box points reach 10.
- `boss_mixed`: unlock when level reaches 5 or at least three knowledge points are strong.

Unlocks are motivational guidance, not hard locks. If the user explicitly asks for a locked mode, allow it and explain what evidence is still missing.

## Badges

Award badges only from evidence:

- `First Quiz`: at least one scored attempt.
- `Mistake Hunter`: at least three incorrect attempts with mistake types recorded.
- `Core Repair`: a previously weak point becomes developing or strong.
- `Mixed Practice`: at least five attempts across three or more knowledge points.
- `Stable Recall`: at least five correct attempts and no incorrect attempts in the latest quiz set.

## Study Pet

The study pet is a lightweight status symbol for learning rhythm.

Pet status rules:

- `Energized`: at least 70 percent correct or partial, with two or more scored attempts.
- `Curious`: mixed results and at least one developing point.
- `Needs Review`: weak points outnumber strong points.
- `Waiting`: no scored attempts yet.

Pet feedback format:

- Mood.
- Why it changed.
- One care action: review, drill, rest, or retest.

Do not make the pet feedback longer than the mastery feedback. The pet is a motivational wrapper around evidence, not the main report.

## Progress Card

Include:

- Total XP.
- Level and title.
- Progress bar to next level.
- XP to next level.
- Badges.
- Pet mood.
- One next quest.

Next quests should be concrete:

- "Answer 5 medium questions on linear algebra eigenvalues."
- "Repair 3 formula mistakes from the mistake log."
- "Retest the two weak points after reviewing notes."

## HUD-Style Progress

When the user wants a compact dashboard similar to a coding HUD/status panel, provide both:

- A one-line status string for terminal, bot, or status bar use.
- A short Markdown card for human review.

One-line format:

```text
EC Dia15 42XP 42% A27 C18/P5 W2 B10 Aegis
```

Rules:

- Keep it under one terminal line when possible.
- Show rank, level, current-level XP/progress, answered/correct/partial, weak count, box points, and companion stage.
- Avoid decorative clutter. The HUD should be glanceable.
- If no scored attempts exist, show `EC Brz1 0XP 0% A0 C0/P0 W0 Ember`.
