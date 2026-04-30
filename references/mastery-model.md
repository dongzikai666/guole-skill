# Mastery Model

Use this reference when reviewing answers, building mistake logs, or writing mastery reports.

## Status Labels

- `strong`: accurate, fast, and transferable across variants.
- `developing`: mostly correct but slow, incomplete, or dependent on hints.
- `weak`: wrong, guessed, confused, or unable to start.
- `untested`: no recent evidence.

## Evidence

Track evidence by knowledge point:

- attempts
- correct count
- difficulty level
- mistake types
- response confidence if provided
- time pressure if provided
- latest result

Do not infer strong mastery from one easy correct answer. Require either medium difficulty success or repeated correct recall.

## Scoring Heuristic

Use this default if the user does not provide a rubric:

- Easy correct: +1
- Medium correct: +2
- Hard correct: +3
- Incorrect: -1
- Same mistake repeated: additional -1
- Correct after hint: count as partial, not strong

Map score and evidence to status:

- Strong: at least 2 correct attempts including one medium or hard, with no recent core mistake.
- Developing: at least one correct attempt but gaps remain.
- Weak: recent incorrect answer, repeated mistake, or cannot explain the method.
- Untested: no attempt yet.

## Feedback Format

For each weak or developing point, write:

- Diagnosis: what went wrong.
- Repair: the missing idea or method.
- Drill: one next exercise.
- Review action: what to read, derive, memorize, or practice.

## Exam Readiness Estimate

Use this only as a study decision aid, not as a score guarantee.

Inputs:

- teacher-focus and official scope signals,
- past-exam frequency or style signals,
- attempts, correctness, partial credit, difficulty,
- recent weak points and mistake types,
- memory-mode recall results.

Output:

- estimated score range, such as `58-72`, not a single exact score;
- pass risk: `low`, `medium`, `high`, or `unknown`;
- most likely loss points;
- priority review order;
- boundary sentence: "This is a study decision aid, not an exact score prediction or pass guarantee."

Knowledge-point assessment fields:

- `KPxxx`
- exam importance
- source basis and source weight
- mastery status
- evidence count
- weak reason
- next action

## Mistake Types

- `concept`: misunderstood definition or principle.
- `formula`: wrong formula, condition, sign, or unit.
- `procedure`: wrong sequence of steps.
- `calculation`: arithmetic or algebra slip.
- `reading`: missed condition or misunderstood wording.
- `memory`: forgot a fact that should be memorized.
- `transfer`: knows the base case but fails in a new context.
- `time`: method works but is too slow.

## Report Sections

Use this structure:

1. Overall readiness.
2. Strong points.
3. Developing points.
4. Weak points.
5. Untested high-priority points.
6. Next 24 hours.
7. Next quiz recommendation.
