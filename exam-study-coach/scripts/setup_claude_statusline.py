#!/usr/bin/env python3
"""Configure Claude Code statusLine for Guole / ExamCoach progress."""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path


def default_claude_dir() -> Path:
    return Path.home() / ".claude"


def find_node() -> tuple[str, str]:
    windows_node = Path("D:/node.exe")
    if windows_node.exists():
        return (str(windows_node), "/d/node")
    found = shutil.which("node")
    if found:
        return (found, found)
    raise SystemExit("Node.js was not found. Install Node.js first, then rerun setup.")


def bash_single_quote(text: str) -> str:
    return "'" + text.replace("'", "'\"'\"'") + "'"


def powershell_single_quote(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def standalone_command_for(node_win: str, skill_dir: Path) -> str:
    fast_js = skill_dir / "scripts" / "study_statusline_fast.js"
    if not fast_js.exists():
        raise SystemExit(f"Missing fast statusline script: {fast_js}")
    return (
        "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "
        + powershell_single_quote(
            f"& {powershell_single_quote(node_win)} {powershell_single_quote(str(fast_js))} statusline --color"
        )
    )


def claude_hud_command_for(node_win: str, node_bash: str, skill_dir: Path) -> str:
    fast_js = skill_dir / "scripts" / "study_statusline_fast.js"
    if not fast_js.exists():
        raise SystemExit(f"Missing fast statusline script: {fast_js}")
    extra_cmd = f'"{node_win}" "{fast_js}" label'
    script = (
        'plugin_dir=$(ls -d "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"/plugins/cache/claude-hud/claude-hud/*/ '
        "2>/dev/null | awk -F/ '{ print $(NF-1) \"\\t\" $(0) }' | sort -t. -k1,1n -k2,2n -k3,3n -k4,4n "
        f'| tail -1 | cut -f2-); exec "{node_bash}" "${{plugin_dir}}dist/index.js" --extra-cmd '
        f"{bash_single_quote(extra_cmd)}"
    )
    return "bash -c " + bash_single_quote(script)


def load_settings(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return {}


def setup(args: argparse.Namespace) -> int:
    claude_dir = Path(args.claude_dir).expanduser().resolve() if args.claude_dir else default_claude_dir()
    settings_path = claude_dir / "settings.json"
    skill_dir = Path(args.skill_dir).expanduser().resolve() if args.skill_dir else Path(__file__).resolve().parents[1]
    node_win, node_bash = find_node()

    settings = load_settings(settings_path)
    if args.mode == "off":
        settings.pop("statusLine", None)
    else:
        if args.mode == "claude-hud-extra":
            command = claude_hud_command_for(node_win=node_win, node_bash=node_bash, skill_dir=skill_dir)
        else:
            command = standalone_command_for(node_win=node_win, skill_dir=skill_dir)
        settings["statusLine"] = {"type": "command", "command": command}

    if args.dry_run:
        print(json.dumps(settings.get("statusLine", {"disabled": True}), ensure_ascii=False, indent=2))
        return 0

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    if settings_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = settings_path.with_suffix(f".json.examcoach-{timestamp}.bak")
        backup.write_text(settings_path.read_text(encoding="utf-8-sig"), encoding="utf-8")
        print(f"Backed up settings to {backup}")
    settings_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.mode == "off":
        print(f"Disabled Claude Code statusLine in {settings_path}")
    else:
        print(f"Updated Claude Code statusLine in {settings_path}")
    print("Restart Claude Code to load the new status line.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configure Guole / ExamCoach progress in Claude Code statusLine.")
    parser.add_argument("--claude-dir", default="", help="Claude config directory. Defaults to ~/.claude.")
    parser.add_argument("--skill-dir", default="", help="Installed exam-study-coach skill directory.")
    parser.add_argument(
        "--mode",
        choices=["standalone", "claude-hud-extra", "off"],
        default="standalone",
        help="standalone does not depend on claude-hud; claude-hud-extra appends to claude-hud; off disables.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print statusLine config without writing settings.")
    return parser.parse_args()


def main() -> int:
    return setup(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
