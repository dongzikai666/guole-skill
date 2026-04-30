# Question Generation

Use this reference before creating practice questions, mock exams, or reinforcement drills.

For live tutoring, generate only one question at a time and hide the answer until the user responds. Use batch generation only when the user explicitly asks for a full quiz, mock exam, worksheet, or export.

Before generating the first live question, resolve the subject's session config. Respect question type, difficulty, scope, source mode, and past-exam mode from `config.json` unless the user overrides them.

If `study_mode=memory`, do not generate a normal question. Generate one memory card and recall prompt instead. If `study_mode=mock_exam` or `boss_mixed`, still ask one item at a time unless the user explicitly asks for a full paper.

## Question Metadata

For exported quizzes, every question should include:

- `id`: stable label such as `Q1`.
- `knowledge_point`: one primary concept.
- `difficulty`: easy, medium, hard, or challenge.
- `question_type`: multiple-choice, fill-in, short-answer, calculation, proof, coding, case-analysis, or mixed.
- `estimated_time`: minutes.
- `source_basis`: source topic or public citation, not a long excerpt.
- `answer`
- `explanation`
- `grading_notes`: what counts as correct, partial, or wrong.
- `scope`
- `source_mode`
- `past_exam_mode`

For live tutoring, show only `knowledge_point`, `question_type`, `difficulty`, and `source_basis` before the question. Keep hidden fields for grading or logs.

## Distribution

For a normal quiz, use:

- 30 percent easy recall and definitions.
- 40 percent medium application.
- 20 percent hard mixed or multi-step reasoning.
- 10 percent challenge or exam-style integration.

Adjust for the exam type:

- Closed-book: more recall, derivation, formulas, and definitions.
- Open-book: more application, comparison, and case analysis.
- Calculation-heavy: include units, assumptions, intermediate steps, and common numeric traps.
- Proof-heavy: include lemma selection, proof skeletons, and counterexamples.
- Coding-heavy: include edge cases, complexity, and test cases.

## Style Rules

- Create original questions inspired by the user's materials, not copied questions.
- Avoid reproducing full homework or past-paper questions unless the user owns or is allowed to use them.
- Do not imitate a private teacher's exam wording too closely.
- Prefer concise, testable prompts.
- Use one concept per question for diagnosis, then add mixed questions later.
- Include explanations that teach the repair, not just the final answer.
- In live tutoring, do not include the explanation until after the user's answer.
- If `past_exam_mode` is `inspired_similar`, generate an original similar question and state the tested style or concept, not the private original wording.
- If `source_mode` allows public search, search only with user permission and cite public sources.

## Reinforcement

When the user misses a question:

1. Identify mistake type: concept, formula, procedure, calculation, reading, memory, transfer, or time-management.
2. Explain the smallest missing idea.
3. Ask one near-transfer question.
4. Ask one far-transfer question if the near-transfer question is correct.
5. Update the mastery status.
6. Ask whether the user wants one similar drill, a short concept explanation, public resources/videos, or to move on.

Always include `0 return/reselect` in the next-step menu so the learner can change question type, difficulty, source mode, or focus point.

## No-Answer Mode

If the user requests a real test mode, hide answers during the quiz and place answers in a separate section or file. After the user submits responses, reveal grading and explanations.
