# Study Pet System

Use this reference when the user wants a pet-like companion, growth system, mood feedback, or a more playful progress layer.

## Design Principle

The study companion is a compact game-style progress layer for learning evidence. It should feel cooler than a generic pet, but every state must map to a real study signal.

## State Fields

Track these fields in reports or JSON state:

- `name`: user-chosen name, default `Astra`.
- `stage`: growth stage from level.
- `mood`: recent learning rhythm.
- `energy`: practice volume and recency.
- `focus`: weak-point repair progress.
- `bond`: consistency across sessions.
- `care_action`: one concrete next study action.

## Growth Stages

Map stage to level:

- Level 1-2: Ember
- Level 3-5: Pulse
- Level 6-9: Nova
- Level 10-14: Vanguard
- Level 15-24: Aegis
- Level 25+: Mythic

Stages should be motivational labels, not claims of mastery.

## Mood Rules

- `Overdrive`: correct or partial ratio is at least 85 percent across three or more scored attempts.
- `Charged`: correct or partial ratio is at least 70 percent across two or more scored attempts.
- `LockedIn`: mixed results with at least one developing point.
- `Focused`: weak count decreased compared with prior state, if prior state is available.
- `Determined`: weak points outnumber strong points.
- `Standby`: no scored attempts yet.

## Energy, Focus, Bond

Use 0-100 bars:

- Energy: based on scored attempt count in the current attempt file.
- Focus: based on the share of non-weak knowledge points.
- Bond: based on total attempts, capped at 100.

Default formulas:

- `energy = min(100, scored_attempts * 12)`
- `focus = round(100 * non_weak_points / tested_points)` if tested points exist, else 0
- `bond = min(100, total_attempts * 5)`

## Care Actions

Choose exactly one:

- If no attempts: "Finish the first diagnostic quiz."
- If weak points exist: "Repair one weak point with three focused questions."
- If developing points exist: "Retest developing points with medium questions."
- If mostly strong: "Try a mixed hard quiz."
- If many attempts but low ratio: "Pause new material and review the mistake log."

## Output Format

Keep the pet card compact:

```text
Companion: Astra
Stage: Nova
Mood: Charged
Energy: [######----] 60
Focus: [####------] 40
Bond: [###-------] 30
Care action: Repair one weak point with three focused questions.
```

Avoid long roleplay. The pet should make progress feel alive without distracting from the study plan.
