# Focus Checklist

Use this reference when the user wants to start practice, choose topics, or drill a weak point.

## Default Flow

Before the first normal practice question:

1. Read or build `generated/focus-checklist.md`.
2. Show the top 5 focus points with `KPxxx`, priority, topic, basis, and suggested question type.
3. Ask the user to choose a focus ID, or choose `mixed` for a rotating review.
4. Ask only one question for the selected focus point.

If the user chooses a weak point such as `WP001`, read `progress-state.json`, map the ID to `weak_point_details`, and ask one reinforcement question for that knowledge point.

## Priority Order

Rank focus points by:

1. Teacher focus and official scope.
2. Past-exam style and recurring concepts.
3. Existing weak points and wrong answers.
4. Homework, slides, notes, and small private excerpts.
5. Public links or permitted web search.

## Output

Use compact output:

```text
Choose focus:
KP001 [S] Matrix diagonalization - teacher-focus, past-exams - calculation
KP002 [A] Eigenvalue definition - slides, notes - short_answer
KP003 [A] Linear independence - homework - proof

Reply KP001, KP002, KP003, or mixed.
```

Do not paste long source excerpts. Use source folders as basis labels.
