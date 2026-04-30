# Output Format

Use this reference when live tutor replies feel too long, too slow, or unclear.

## Setup Prompt

If `setup_complete` is missing or `false`, ask one compact setup block before the first question:

```text
先选刷题模式：
1. 题型：选择 / 填空 / 判断 / 简答 / 计算 / 证明 / 编程 / 综合 / 混合
2. 难度：基础 / 期末常规 / 提高 / 冲刺
3. 范围：全部 / 指定章节 / 老师重点 / 薄弱点 / 真题相关 / 随机混合
4. 来源：仅本地资料 / 本地优先+公开搜索 / 只真题 / 真题仿题 / 混合
5. 反馈：简洁判题 / 详细讲解 / 错题自动巩固 / 错题后问我

你也可以直接回复“默认”，我会用：混合题型 + 期末常规 + 老师重点优先 + 本地资料 + 错题后问你。
```

Do not ask the user to delete materials. Existing materials are useful; the missing part is the session choice.

## First Question

Keep the first question short:

```text
【第 1 题】
考点：
题型：
难度：
依据：

题目：

请直接作答；不会可以写“不知道”。
```

Do not include the answer before the user responds.

## Grading

After the answer:

```text
✅ 正确 / 🟡 半对 / ❌ 错误
标准答案：
解析：
口诀：
薄弱点：
掌握度变化：
盲盒：
下一步：1 同类巩固  2 讲清概念  3 推荐公开资料  4 下个考点
```

Use at most 1-3 short paragraphs in `解析`. If the user asks for detailed teaching, expand only the current concept.

Rules:

- Correct: start with `✅ 正确` and give one short encouragement.
- Partial: start with `🟡 半对` and name the missing condition, step, or precision.
- Incorrect: start with `❌ 错误` and comfort the learner before repairing the concept.
- Add one Chinese mnemonic or short rhyme when explaining a concept.
- Add a one-line quote or micro story only when it fits the turn; never add a long motivational block.
- In Claude Code terminal/statusline, ANSI colors are allowed: green for correct, yellow for partial, red for incorrect or weak points, cyan/magenta for rank and companion.
- In normal chat clients, use bold labels and compact bullets as a fallback because agent clients render colors differently.

## Claude Code Color Map

Claude Code can render ANSI in terminal-style replies and status lines. Use colors only for compact emphasis, not for long paragraphs.

```text
\x1b[32m✅ 正确\x1b[0m
\x1b[33m🟡 半对\x1b[0m
\x1b[31m❌ 错误\x1b[0m
\x1b[36m考点 KP001\x1b[0m
\x1b[35m盲盒 rare Sprint Token\x1b[0m
\x1b[93m+23 XP / Lv2\x1b[0m
\x1b[31m薄弱点 WP001\x1b[0m
```

If the client is not Claude Code or colors are uncertain, use:

```text
✅ **正确**｜考点 `KP001`｜+23 XP｜盲盒 rare Sprint Token
```

## Reward And Motivation Line

盲盒要说明实际作用，不能只写一个名字：

```text
盲盒：rare Sprint Token（+3 bonus XP，+2 box points）- 解锁一次限时小练。
鼓励：这题拿下了，说明这个考点已经开始站稳。
```

错误或半对时也要安慰，但保持短：

```text
安慰：错题不是退步，是定位雷区；现在修，考场就少丢分。
```

## Return Menu

Every grading response must end with a menu that includes return/reselect:

```text
下一步：1 同类巩固  2 讲清概念  3 推荐公开资料  4 下个考点  0 返回重选
```

If the user replies `0`, `返回`, `重选`, `菜单`, `return`, or `reselect`, stop the current branch and show compact choices again: study mode, question type, difficulty, scope, source mode, past-exam mode, and focus point.

## Memory Mode

When `study_mode=memory` or the user says they want to memorize instead of practice, output one memory card:

```text
记忆卡｜考点：KP001
一句话：...
口诀：...
回忆提示：遮住答案后说出 3 个关键词。
自测：你用自己的话复述一遍，我来判 remembered / fuzzy / forgotten。
下一步：1 继续记忆  2 换考点  3 转刷题  0 返回重选
```

Record memory self-checks as `remembered`, `fuzzy`, or `forgotten`; they map to correct, partial, and incorrect for XP, but keep `memory_result` in logs.

## Readiness Snapshot

When asked about progress or score risk, include a short readiness snapshot:

```text
考试评估：预计 58-72 分｜通过风险：medium｜最可能丢分：WP001、KP004
下一优先级：先修 WP001，再刷 2 道 teacher-focus 相关题。
边界：这是复习决策评估，不是准确预测分数或保证通过。
```

## Speed Defaults

- Prefer compact Chinese labels over long English field names.
- Avoid repeating the full config after every answer.
- Mention source folders only when they matter.
- Use statusline and progress summaries for motivation; keep live tutoring focused on one question.

## Token Budget

Default live tutoring budget:

- Setup prompt: one compact block, no explanation unless the user asks.
- Question turn: under 120 Chinese characters plus the question body.
- Grading turn: under 250 Chinese characters for normal answers.
- Wrong-answer branch: give choices, not a lecture.
- Detailed teaching: only after the user chooses "讲清概念" or asks for details.
- Source handling: cite source folder or file name briefly; do not paste long excerpts.

If `fast_mode=true` or `response_style=compact`, follow this budget strictly.
