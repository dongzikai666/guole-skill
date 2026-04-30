#!/usr/bin/env node
// Fast statusline helper for Claude Code.
// Reads generated/progress-state.json directly without starting Python.

const fs = require("fs");
const os = require("os");
const path = require("path");

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8").replace(/^\uFEFF/, ""));
  } catch {
    return null;
  }
}

function readStdinJson() {
  try {
    if (process.stdin.isTTY) return null;
    const input = fs.readFileSync(0, "utf8").replace(/^\uFEFF/, "").trim();
    if (!input) return null;
    return JSON.parse(input);
  } catch {
    return null;
  }
}

const DIFFICULTY_XP = {
  easy: 10,
  basic: 10,
  medium: 20,
  final_regular: 20,
  hard: 35,
  advanced: 35,
  challenge: 50,
  sprint: 50,
};

const RANKS = [
  [30, "Legend", "Leg"],
  [25, "King", "King"],
  [20, "Master", "Mst"],
  [15, "Diamond", "Dia"],
  [10, "Platinum", "Plat"],
  [6, "Gold", "Gold"],
  [3, "Silver", "Sil"],
  [1, "Bronze", "Brz"],
];

const REWARD_BOXES = [
  ["common", "Recall Coin", 1, 1],
  ["common", "Focus Shard", 1, 1],
  ["common", "Formula Spark", 1, 1],
  ["rare", "Error Scanner", 3, 2],
  ["rare", "Sprint Token", 3, 2],
  ["epic", "Diamond Key", 6, 4],
  ["legendary", "King Star", 10, 8],
];

function readJsonl(file) {
  try {
    return fs
      .readFileSync(file, "utf8")
      .replace(/^\uFEFF/, "")
      .split(/\r?\n/)
      .filter((line) => line.trim())
      .map((line) => JSON.parse(line));
  } catch {
    return [];
  }
}

function fileMtime(file) {
  try {
    return fs.statSync(file).mtimeMs;
  } catch {
    return -1;
  }
}

function normalizeResult(value) {
  const text = String(value || "").trim().toLowerCase();
  if (["correct", "right", "yes", "true", "1", "remembered", "remember"].includes(text)) return "correct";
  if (["partial", "hinted", "fuzzy"].includes(text)) return "partial";
  if (["incorrect", "wrong", "no", "false", "0", "forgotten", "forget"].includes(text)) return "incorrect";
  return "unscored";
}

function xpFor(record) {
  const difficulty = String(record.difficulty || "easy").trim().toLowerCase();
  const base = DIFFICULTY_XP[difficulty] || 10;
  const result = normalizeResult(record.result);
  if (result === "correct") return base;
  if (result === "partial") return Math.max(1, Math.round(base * 0.4));
  if (result === "incorrect" && (record.mistake_type || record.notes)) return 5;
  return 0;
}

function rewardFor(record, index) {
  if (normalizeResult(record.result) !== "correct") return null;
  const seed = [record.timestamp || "", record.question_id || "", record.knowledge_point || "", String(index)].join("|");
  let score = 0;
  for (const char of seed) score += char.charCodeAt(0);
  score %= 100;
  let rarity = "common";
  if (score >= 97) rarity = "legendary";
  else if (score >= 85) rarity = "epic";
  else if (score >= 60) rarity = "rare";
  const pool = REWARD_BOXES.filter((item) => item[0] === rarity);
  const chosen = pool[score % pool.length];
  return { rarity: chosen[0], name: chosen[1], bonus_xp: chosen[2], box_points: chosen[3] };
}

function rankFor(level) {
  for (const [minLevel, name, short] of RANKS) {
    if (level >= minLevel) return [name, short];
  }
  return ["Bronze", "Brz"];
}

function petStageFor(level) {
  if (level >= 25) return "Mythic";
  if (level >= 15) return "Aegis";
  if (level >= 10) return "Vanguard";
  if (level >= 6) return "Nova";
  if (level >= 3) return "Pulse";
  return "Ember";
}

function summarize(records) {
  const grouped = new Map();
  for (const record of records) {
    const point = String(record.knowledge_point || "unspecified");
    if (!grouped.has(point)) grouped.set(point, { attempts: 0, correct: 0, partial: 0, incorrect: 0 });
    const item = grouped.get(point);
    const result = normalizeResult(record.result);
    item.attempts += 1;
    if (result === "correct") item.correct += 1;
    else if (result === "partial") item.partial += 1;
    else if (result === "incorrect") item.incorrect += 1;
  }
  return grouped;
}

function statusFor(item) {
  if (!item || !item.attempts) return "untested";
  const ratio = (item.correct + 0.5 * item.partial) / item.attempts;
  if (item.incorrect === 0 && item.attempts >= 2 && ratio >= 0.8) return "strong";
  if (ratio >= 0.5) return "developing";
  return "weak";
}

function progressFromRecords(records, baseState = {}) {
  let totalXp = 0;
  let boxPoints = 0;
  let rewardCount = 0;
  records.forEach((record, index) => {
    totalXp += xpFor(record);
    const reward = rewardFor(record, index + 1);
    if (reward) {
      totalXp += Number(reward.bonus_xp) || 0;
      boxPoints += Number(reward.box_points) || 0;
      rewardCount += 1;
    }
  });
  const level = Math.floor(totalXp / 100) + 1;
  const currentPercent = totalXp - (level - 1) * 100;
  const [rankName, rankShort] = rankFor(level);
  const results = records.map((record) => normalizeResult(record.result));
  const grouped = summarize(records);
  const weakPoints = [...grouped.entries()].filter(([, item]) => statusFor(item) === "weak").map(([point]) => point);
  const strongCount = [...grouped.values()].filter((item) => statusFor(item) === "strong").length;
  const weakCount = weakPoints.length;
  const petMood = weakCount > strongCount ? "Determined" : records.length ? "Charged" : "Standby";
  return {
    ...baseState,
    total_xp: totalXp,
    level,
    level_percent: currentPercent,
    title_label: rankName,
    rank_name: rankName,
    rank_short: rankShort,
    attempt_count: records.length,
    answered_count: results.filter((result) => result !== "unscored").length,
    correct_count: results.filter((result) => result === "correct").length,
    partial_count: results.filter((result) => result === "partial").length,
    incorrect_count: results.filter((result) => result === "incorrect").length,
    reward_count: rewardCount,
    box_points: boxPoints,
    weak_points: weakPoints,
    pet_stage: petStageFor(level),
    pet_mood: petMood,
    next_quest: weakPoints.length ? `repair ${weakPoints[0]}` : "complete a mixed quiz",
  };
}

function stateWithFreshLog(statePath, state) {
  if (!statePath) return state;
  const logPath = path.join(path.dirname(statePath), "session-log.jsonl");
  if (!fs.existsSync(logPath)) return state;
  const records = readJsonl(logPath);
  if (!records.length) return state;
  if (!state || fileMtime(logPath) > fileMtime(statePath)) {
    return progressFromRecords(records, state || {});
  }
  return state;
}

function existingDir(value) {
  if (!value || typeof value !== "string") return "";
  try {
    const resolved = path.resolve(value);
    if (fs.existsSync(resolved) && fs.statSync(resolved).isDirectory()) return resolved;
    const repaired = repairHomePath(resolved);
    if (repaired && fs.existsSync(repaired) && fs.statSync(repaired).isDirectory()) return repaired;
    return "";
  } catch {
    return "";
  }
}

function repairHomePath(value) {
  const match = String(value || "").match(/^([A-Za-z]:\\Users\\)[^\\]+\\(.+)$/i);
  if (!match) return "";
  return path.join(os.homedir(), match[2]);
}

function unique(items) {
  const seen = new Set();
  const result = [];
  for (const item of items) {
    if (!item || seen.has(item)) continue;
    seen.add(item);
    result.push(item);
  }
  return result;
}

function rootsFromSession(session) {
  const roots = [];
  if (session && typeof session === "object") {
    const workspace = session.workspace && typeof session.workspace === "object" ? session.workspace : {};
    roots.push(workspace.current_dir);
    roots.push(workspace.project_dir);
    if (Array.isArray(workspace.added_dirs)) roots.push(...workspace.added_dirs);
    roots.push(session.cwd);
    const worktree = session.worktree && typeof session.worktree === "object" ? session.worktree : {};
    roots.push(worktree.path);
    roots.push(worktree.original_cwd);
  }
  roots.push(process.cwd());
  return unique(roots.map(existingDir));
}

function newestProgressState(workspace) {
  const subjects = path.join(workspace, "subjects");
  if (!fs.existsSync(subjects)) return "";
  let newest = "";
  let newestMtime = -1;
  for (const subjectId of fs.readdirSync(subjects)) {
    const candidate = path.join(subjects, subjectId, "generated", "progress-state.json");
    try {
      const stat = fs.statSync(candidate);
      if (stat.isFile() && stat.mtimeMs > newestMtime) {
        newest = candidate;
        newestMtime = stat.mtimeMs;
      }
    } catch {
      // Ignore missing or unreadable subjects.
    }
  }
  return newest;
}

function stateFromWorkspace(workspace) {
  const currentSubject = path.join(workspace, "current-subject.txt");
  if (fs.existsSync(currentSubject)) {
    const subjectId = fs.readFileSync(currentSubject, "utf8").replace(/^\uFEFF/, "").trim();
    const candidate = path.join(workspace, "subjects", subjectId, "generated", "progress-state.json");
    if (fs.existsSync(candidate)) return candidate;
  }
  return newestProgressState(workspace);
}

function stateFromRoot(root) {
  let current = path.resolve(root);
  while (true) {
    const workspace = path.join(current, "exam-coach-workspace");
    if (fs.existsSync(workspace)) {
      const candidate = stateFromWorkspace(workspace);
      if (candidate) return candidate;
    }

    const generatedCandidate = path.join(current, "generated", "progress-state.json");
    if (fs.existsSync(generatedCandidate)) return generatedCandidate;

    const parent = path.dirname(current);
    if (parent === current) return "";
    current = parent;
  }
}

function findProgressState(explicit, session) {
  if (explicit && fs.existsSync(explicit)) return explicit;
  if (process.env.EXAM_STUDY_PROGRESS_STATE && fs.existsSync(process.env.EXAM_STUDY_PROGRESS_STATE)) {
    return process.env.EXAM_STUDY_PROGRESS_STATE;
  }

  for (const root of rootsFromSession(session)) {
    const candidate = stateFromRoot(root);
    if (candidate) return candidate;
  }
  return "";
}

function label(state) {
  if (!state) return "GL | setup";
  const level = Number(state.level) || 1;
  const percent = Number(state.level_percent) || 0;
  const totalXp = Number(state.total_xp) || 0;
  const answered = Number(state.answered_count) || 0;
  const correct = Number(state.correct_count) || 0;
  const partial = Number(state.partial_count) || 0;
  const rank = String(state.rank_short || state.title_label || "Brz").replace(/\s+/g, "").slice(0, 4);
  const pet = String(state.pet_stage || state.pet_mood || "Ember").replace(/\s+/g, "").slice(0, 7);
  const weak = Array.isArray(state.weak_points) ? state.weak_points.length : 0;
  const box = Number(state.box_points) || 0;
  return `GL ${rank}${level} ${totalXp}XP ${percent}% A${answered} C${correct}/P${partial} W${weak} B${box} ${pet}`;
}

function bar(percent, width = 12) {
  const value = Math.max(0, Math.min(100, Number(percent) || 0));
  const filled = Math.round((width * value) / 100);
  return "#".repeat(filled) + "-".repeat(width - filled);
}

const ANSI = {
  reset: "\x1b[0m",
  dim: "\x1b[2m",
  bold: "\x1b[1m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  magenta: "\x1b[35m",
  cyan: "\x1b[36m",
  white: "\x1b[37m",
  gray: "\x1b[90m",
  brightGreen: "\x1b[92m",
  brightYellow: "\x1b[93m",
  brightMagenta: "\x1b[95m",
  brightCyan: "\x1b[96m",
};

function color(enabled, code, text) {
  if (!enabled) return text;
  return `${code}${text}${ANSI.reset}`;
}

function rankColor(rank) {
  const value = String(rank || "").toLowerCase();
  if (value.includes("legend") || value.includes("king")) return ANSI.brightMagenta;
  if (value.includes("master") || value.includes("diamond")) return ANSI.cyan;
  if (value.includes("platinum")) return ANSI.brightCyan;
  if (value.includes("gold")) return ANSI.brightYellow;
  if (value.includes("silver")) return ANSI.white;
  return ANSI.yellow;
}

function percentColor(percent) {
  const value = Number(percent) || 0;
  if (value >= 70) return ANSI.green;
  if (value >= 35) return ANSI.yellow;
  return ANSI.red;
}

function coloredBar(percent, width, enabled) {
  const raw = bar(percent, width);
  if (!enabled) return raw;
  const value = Math.max(0, Math.min(100, Number(percent) || 0));
  const filled = Math.round((width * value) / 100);
  return color(true, percentColor(value), raw.slice(0, filled)) + color(true, ANSI.gray, raw.slice(filled));
}

function statusline(state) {
  const enabled = useColor();
  if (!state) return `${color(enabled, ANSI.cyan, "GL")} ${color(enabled, ANSI.yellow, "setup needed")} | Run /guole`;
  const level = Number(state.level) || 1;
  const percent = Number(state.level_percent) || 0;
  const totalXp = Number(state.total_xp) || 0;
  const nextTarget = Math.max(100, level * 100);
  const title = String(state.title_label || "Starter");
  const stage = String(state.pet_stage || "Spark");
  const mood = String(state.pet_mood || "Waiting");
  const weak = Array.isArray(state.weak_points) ? state.weak_points.length : 0;
  const answered = Number(state.answered_count) || 0;
  const correct = Number(state.correct_count) || 0;
  const partial = Number(state.partial_count) || 0;
  const incorrect = Number(state.incorrect_count) || 0;
  const quest = String(state.next_quest || "first diagnostic quiz");
  const box = Number(state.box_points) || 0;
  const modes = Array.isArray(state.unlocked_modes) ? state.unlocked_modes : [];
  const unlocked = modes.filter((mode) => !["live_tutor", "memory"].includes(String(mode))).join(",");
  const rankText = `${title} Lv.${level}`;
  const xpText = `XP ${totalXp}/${nextTarget}`;
  const progressText = `[${coloredBar(percent, 12, enabled)}] ${percent}%`;
  const answerText = [
    color(enabled, ANSI.gray, `A${answered}`),
    color(enabled, ANSI.green, `C${correct}`),
    color(enabled, ANSI.yellow, `P${partial}`),
    color(enabled, ANSI.red, `I${incorrect}`),
  ].join(" ");
  const weakColor = weak > 0 ? ANSI.red : ANSI.green;
  const unlockText = unlocked ? `Unlocked ${unlocked}` : "Unlocked base";
  return [
    `${color(enabled, ANSI.cyan, "GL")} ${color(enabled, rankColor(title), rankText)} | ${color(enabled, ANSI.brightYellow, xpText)} | ${progressText} | ${answerText}`,
    `${color(enabled, ANSI.brightCyan, "Companion")} ${color(enabled, ANSI.magenta, `${stage}/${mood}`)} | ${color(enabled, ANSI.brightMagenta, `Box ${box}`)} | ${color(enabled, weakColor, `Weak ${weak}`)} | ${color(enabled, ANSI.gray, `${unlockText} | Next: ${quest}`)}`,
  ].join("\n");
}

function argValue(name) {
  const index = process.argv.indexOf(name);
  if (index >= 0 && index + 1 < process.argv.length) return process.argv[index + 1];
  return "";
}

const mode = process.argv[2] || "label";
const session = readStdinJson();
const statePath = findProgressState(argValue("--state"), session);
const state = stateWithFreshLog(statePath, statePath ? readJson(statePath) : null);

function hasArg(name) {
  return process.argv.includes(name);
}

function useColor() {
  if (hasArg("--plain")) return false;
  if (hasArg("--color")) return true;
  if (process.env.NO_COLOR) return false;
  return mode === "statusline";
}

if (mode === "statusline") {
  process.stdout.write(statusline(state) + "\n");
} else {
  process.stdout.write(JSON.stringify({ label: label(state) }) + "\n");
}
