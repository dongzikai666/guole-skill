# Initialization

Use this reference before tutoring when the user has not created an exam workspace or active subject.

## Workspace First

Default workspace:

```text
exam-coach-workspace/
  current-subject.txt
  subjects/
    <subject-id>/
      course-profile.md
      config.json
      materials/
      generated/
```

If the workspace does not exist, offer to initialize it. If the user invokes the skill by a short trigger and there is no active subject, ask for the course or exam name and initialize a subject.

Use the helper:

```bash
python exam-study-coach/scripts/init_subject.py --title "Course name"
```

## Subject Layout

Create these material folders for every subject:

- `syllabus/` - course outline, assessment rules, official scope.
- `slides/` - lecture slides or class materials for topic coverage.
- `notes/` - the learner's own notes and summaries.
- `teacher-focus/` - teacher hints, review scope, emphasized points.
- `textbook-excerpts/` - small private excerpts or chapter notes.
- `homework/` - assignments and practice style evidence.
- `past-exams/` - past papers or recalled question types for private analysis.
- `past-exam-answers/` - private answer keys or learner solutions.
- `user-mistakes/` - screenshots, notes, and logs of wrong answers.
- `public-links/` - URLs to public resources, courses, videos, or docs.

Generated files:

- `source-index.md`
- `focus-checklist.md`
- `focus-checklist.json`
- `knowledge-map.md`
- `question-bank.jsonl`
- `session-log.jsonl`
- `mastery-report.md`
- `progress-state.json`
- `wrong-questions.md`

## Startup Decision

When the user starts:

1. Look for `exam-coach-workspace/current-subject.txt`.
2. If it points to a valid subject, use that subject and its `config.json`.
3. If there are multiple subjects and no active subject, ask the user to pick one.
4. If no subject exists, initialize a subject before tutoring.
5. If material folders are empty, tell the user where to put files and offer a first diagnostic based on any provided context.

Do not silently mix materials across subjects.

## Source Index

After files are added, run or recommend:

```bash
python exam-study-coach/scripts/index_sources.py --subject exam-coach-workspace/subjects/<subject-id>
```

Use the generated index to decide which sources are reliable for scope, question style, explanations, and public resource recommendations.

## Focus Checklist

After indexing sources, run or recommend:

```bash
python exam-study-coach/scripts/focus_checklist.py --subject exam-coach-workspace/subjects/<subject-id>
```

Use `generated/focus-checklist.md` before normal practice. Ask the user to pick `KP001`, `KP002`, or `mixed` instead of jumping directly into a question.

## Default Study Goal

Assume the learner is an undergraduate or graduate student trying to pass quickly or rapidly master a course/knowledge point, unless they ask for a high-score or research-depth mode.

Source priority:

1. `teacher-focus/` and official scope for exam priority.
2. `past-exams/` for style, difficulty, and common concepts.
3. `user-mistakes/` for weak-point repair.
4. `slides/`, `notes/`, `homework/`, and small private excerpts for explanation.
5. `public-links/` or permitted web search for supplemental public learning resources.
