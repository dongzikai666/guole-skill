# Question Session Config

Use this reference before starting live tutoring or generating questions.

## Required Choices

Before the first question, collect only missing choices. Reuse the subject's `config.json` when present.

Defaults:

```json
{
  "setup_complete": false,
  "configured_at": "",
  "fast_mode": true,
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
    "public_links"
  ],
  "mode": "live_tutor",
  "question_type": "mixed",
  "difficulty": "final_regular",
  "scope": "teacher_focus_then_core",
  "source_mode": "local_only",
  "past_exam_mode": "inspired_similar",
  "answer_mode": "one_by_one",
  "feedback": "grade_explain_then_ask",
  "web_search": "ask_each_time"
}
```

If `setup_complete` is missing or `false`, do not start with a question yet. Ask the user to choose the missing session options, then set `setup_complete` to `true`. The user does not need to delete the resource pack.

After setup is complete, do not start normal practice until a focus point is selected. Show or build `generated/focus-checklist.md`, then ask the user to choose `KPxxx`, `WPxxx`, or `mixed`.

Compact setup prompt:

```text
先选刷题模式：
1. 题型：选择 / 填空 / 判断 / 简答 / 计算 / 证明 / 编程 / 综合 / 混合
2. 难度：基础 / 期末常规 / 提高 / 冲刺
3. 范围：全部 / 指定章节 / 老师重点 / 薄弱点 / 真题相关 / 随机混合
4. 来源：仅本地资料 / 本地优先+公开搜索 / 只真题 / 真题仿题 / 混合
5. 反馈：简洁判题 / 详细讲解 / 错题自动巩固 / 错题后问我

你也可以直接回复“默认”。
```

## Study Mode

- `quiz`: normal one-question tutoring.
- `memory`: one knowledge card, one recall prompt, one self-check.
- `weak_point_attack`: repair `WPxxx` weak points after unlock or direct user request.
- `mock_exam`: timed/past-exam-style simulation after unlock or direct user request.
- `boss_mixed`: harder mixed questions after unlock or direct user request.

Always let the user return to this choice with `0`, `返回`, `重选`, or `菜单`.

## Question Types

- `multiple_choice`
- `blank`
- `true_false`
- `short_answer`
- `calculation`
- `proof`
- `coding`
- `case_analysis`
- `mixed`

## Difficulty

- `basic` - concepts, definitions, simple examples.
- `final_regular` - normal final-exam level.
- `advanced` - harder transfer and combined topics.
- `sprint` - time-pressure and exam-style mixed practice.

## Scope

- `all_materials`
- `specific_chapter`
- `teacher_focus`
- `weak_points`
- `past_exam_related`
- `random_mixed`
- `teacher_focus_then_core`
- `selected_focus_point`
- `selected_weak_point`

Default scope is pass-oriented: teacher focus first, then official scope/core concepts, then past-exam-related drills.

## Source Mode

- `local_only` - use only the subject folder.
- `local_plus_public_search` - local first, public web search only with permission and citations.
- `past_exams_only` - use past-exam materials to select question style and scope.
- `past_exam_inspired` - generate original similar questions based on past-exam style.
- `mixed` - combine local materials, weak points, and permitted public resources.

## Past Exam Mode

- `none`
- `original_only`
- `inspired_similar`
- `style_and_topic_only`

Use `original_only` only for private study if the user has provided the material and is allowed to use it. Do not publish or redistribute original past-paper text. Prefer `inspired_similar` for normal tutoring.

## Web Search

Search only when:

1. The user chooses a source mode that permits public search.
2. The environment has a search or browse tool.
3. The user has given permission for this session or this question.

If search is unavailable, ask the user to paste public links or continue local-only.

## Live Session Contract

After config is resolved:

1. Ask one question.
2. Wait.
3. Grade and explain.
4. Record the attempt if a subject workspace exists.
5. Offer reinforcement, concept explanation, public resources, next topic, or `0 return/reselect`.

## Assessment Config

- `pass_score`: default 60. Use this as the pass-risk threshold in score estimates.
- `score_goal`: default `pass_first`; optimize priorities toward passing before high-score polishing.
- `assessment_mode`: default `readiness_estimate`; output ranges and risk labels instead of exact promises.

When reporting readiness, use local evidence: teacher focus, exam scope, past-exam signal, answer accuracy, difficulty, and recent weak points.
