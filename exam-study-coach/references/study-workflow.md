# Study Workflow

Use this reference when turning user-provided materials into a study pack.

## Inputs to Collect

- Course or exam name.
- Exam date, remaining days, or desired review duration.
- Exam scope, allowed materials, and question types if known.
- User level: beginner, basic, pass-oriented, high-score, or unknown.
- Available materials: notes, PDFs, PPTs, textbook chapters, homework, quiz records, or teacher review hints.
- Constraints: daily study time, weak chapters, target grade, language preference.

Do not block on missing details. If a detail is unknown, make a conservative assumption and label it.

## Artifact Set

Create these files when the user wants reusable output:

- `source-summary.md` - file-by-file source inventory and short summaries.
- `knowledge-map.md` - units, prerequisites, formulas, methods, definitions, traps, and priority.
- `study-plan.md` - daily tasks, checkpoints, and review rhythm.
- `quizzes/quiz-001.md` - practice questions with metadata, answers, and explanations.
- `mistake-log.md` - errors, causes, corrected idea, and follow-up drills.
- `mastery-report.md` - mastered, developing, weak, untested, and next actions.

For multi-subject exam prep, prefer the V2 workspace in `references/initialization.md` over the older single `study-pack/` layout.

## Material Intake

For each source:

1. Identify source type and likely reliability: syllabus, slides, notes, homework, exam guide, textbook, paper, or user summary.
2. Extract topic headings and repeated concepts.
3. Capture formulas, definitions, algorithms, proof patterns, and common examples.
4. Record uncertainty instead of inventing missing exam scope.
5. Use short paraphrases. Quote only brief fragments when needed for precision.

## Knowledge Map

Represent each knowledge unit with:

- `name`
- `priority`: core, likely, supporting, or low
- `evidence`: where the priority came from
- `prerequisites`
- `must_know`
- `common_traps`
- `practice_style`

Priority heuristics:

- Core: explicitly in exam scope, repeated across sources, or required by many later topics.
- Likely: appears in homework, review hints, examples, or common exam patterns.
- Supporting: needed to understand core topics but less likely to be directly tested.
- Low: background, optional reading, or only lightly mentioned.

## Study Plan

Use active recall before rereading:

1. Preview the map and mark unknown units.
2. Learn or repair prerequisites.
3. Drill core units with short questions.
4. Do mixed practice.
5. Review mistakes.
6. Compress into final checklists.

Daily plan format:

- Goal.
- Materials to inspect.
- Active recall prompts.
- Practice set.
- Mistake review.
- Exit check.

## Final Deliverable

End with a short next-action list:

- Review today.
- Practice today.
- Memorize or derive today.
- Stop spending time on.
- Bring to the next session.
