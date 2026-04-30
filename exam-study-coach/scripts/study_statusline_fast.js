#!/usr/bin/env node
// Fast statusline helper for claude-hud --extra-cmd.
// Reads generated/progress-state.json directly without starting Python.

const fs = require("fs");
const path = require("path");

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, "utf8").replace(/^\uFEFF/, ""));
  } catch {
    return null;
  }
}

function findProgressState(explicit) {
  if (explicit && fs.existsSync(explicit)) return explicit;
  if (process.env.EXAM_STUDY_PROGRESS_STATE && fs.existsSync(process.env.EXAM_STUDY_PROGRESS_STATE)) {
    return process.env.EXAM_STUDY_PROGRESS_STATE;
  }

  let current = process.cwd();
  while (true) {
    const workspace = path.join(current, "exam-coach-workspace");
    const currentSubject = path.join(workspace, "current-subject.txt");
    if (fs.existsSync(currentSubject)) {
      const subjectId = fs.readFileSync(currentSubject, "utf8").replace(/^\uFEFF/, "").trim();
      const candidate = path.join(workspace, "subjects", subjectId, "generated", "progress-state.json");
      if (fs.existsSync(candidate)) return candidate;
    }

    const generatedCandidate = path.join(current, "generated", "progress-state.json");
    if (fs.existsSync(generatedCandidate)) return generatedCandidate;

    const parent = path.dirname(current);
    if (parent === current) return "";
    current = parent;
  }
}

function label(state) {
  if (!state) return "Guole | setup";
  const level = Number(state.level) || 1;
  const percent = Number(state.level_percent) || 0;
  const answered = Number(state.answered_count) || 0;
  const correct = Number(state.correct_count) || 0;
  const partial = Number(state.partial_count) || 0;
  const rank = String(state.rank_short || state.title_label || "Brz").replace(/\s+/g, "").slice(0, 4);
  const pet = String(state.pet_stage || state.pet_mood || "Ember").replace(/\s+/g, "").slice(0, 7);
  const weak = Array.isArray(state.weak_points) ? state.weak_points.length : 0;
  const box = Number(state.box_points) || 0;
  return `EC ${rank}${level} ${percent}XP ${percent}% A${answered} C${correct}/P${partial} W${weak} B${box} ${pet}`;
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
  if (!state) return `${color(enabled, ANSI.cyan, "[Guole]")} ${color(enabled, ANSI.yellow, "setup needed")} | Run $guole`;
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
    `${color(enabled, ANSI.cyan, "[Guole]")} ${color(enabled, rankColor(title), rankText)} | ${color(enabled, ANSI.brightYellow, xpText)} | ${progressText} | ${answerText}`,
    `${color(enabled, ANSI.brightCyan, "Companion")} ${color(enabled, ANSI.magenta, `${stage}/${mood}`)} | ${color(enabled, ANSI.brightMagenta, `Box ${box}`)} | ${color(enabled, weakColor, `Weak ${weak}`)} | ${color(enabled, ANSI.gray, `${unlockText} | Next: ${quest}`)}`,
  ].join("\n");
}

function argValue(name) {
  const index = process.argv.indexOf(name);
  if (index >= 0 && index + 1 < process.argv.length) return process.argv[index + 1];
  return "";
}

const mode = process.argv[2] || "label";
const statePath = findProgressState(argValue("--state"));
const state = statePath ? readJson(statePath) : null;

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
