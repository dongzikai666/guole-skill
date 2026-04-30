# Status Line

Use this reference when the user wants a bottom-of-terminal study HUD.

## What Is Possible

Claude Code can run a `statusLine.command` that prints text under the input box. Reloading plugins is not enough; the user must configure `statusLine` once.

This skill provides two helper implementations:

- `scripts/study_statusline_fast.js`: preferred because it starts quickly and reads `generated/progress-state.json` directly.
- `scripts/study_statusline.py`: Python fallback with more detailed standalone output.

## Recommended Setup

Default to standalone mode. It does not require claude-hud and prints ANSI-colored progress in Claude Code.

If the user asks inside `/guole` to enable the status line, run setup once:

```bash
python scripts/setup_statusline.py --mode standalone --claude-dir ~/.claude --skill-dir ~/.claude/skills/guole
```

The setup script backs up `settings.json` and writes a direct 过了.skill status line.

If the user already sees the bottom status line after `/guole`, do not repeat setup.

Use `claude-hud-extra` only when the user already has claude-hud and wants to append 过了.skill:

Example command shape:

```text
node path/to/claude-hud/dist/index.js --extra-cmd "node path/to/guole/scripts/study_statusline_fast.js label"
```

Disable:

```bash
python scripts/setup_statusline.py --mode off --claude-dir ~/.claude
```

Use `statusline` mode when the study HUD owns the whole bottom display.

```text
node path/to/guole/scripts/study_statusline_fast.js statusline --color --state exam-coach-workspace/subjects/course-name/generated/progress-state.json
```

Use `--plain` when the terminal does not render ANSI colors correctly.

The compact label includes box points:

```text
EC Dia15 42XP 42% A27 C18/P5 W2 B10 Aegis
```

The colored standalone status line should show rank/XP/progress, answer counts, companion, box points, weak count, unlocked modes, and next quest. It must not depend on claude-hud.

## Study Pack Discovery

The fast helper finds progress state in this order:

1. `--state` argument.
2. `EXAM_STUDY_PROGRESS_STATE` environment variable.
3. `exam-coach-workspace/current-subject.txt` in the current directory or its parents.
4. `generated/progress-state.json` if the terminal is inside a subject directory.

## Motivational Quotes

Quotes are short and rotate deterministically by date and level. Keep them concise. They should encourage the next study behavior, not shame the learner.

Examples:

- "One repaired mistake is real progress."
- "Active recall beats passive rereading."
- "Small drills compound before the exam."

## Safety

Do not put private material or answer content in the status line. Show only aggregate progress, pet mood, weak count, next quest, and short motivational text.
