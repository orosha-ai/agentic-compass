#!/usr/bin/env python3
"""
Agentic Compass — AI Agent Self-Reflection Tool (v2.0)

Local-only reflection that forces objective action for AI agents.
"""

import argparse
import re
import json
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
DEFAULT_DAILY_PATH = Path.home() / ".openclaw" / "workspace" / "memory" / f"{datetime.now().strftime('%Y-%m-%d')}.md"
DEFAULT_LONG_PATH = Path.home() / ".openclaw" / "workspace" / "MEMORY.md"
OUTPUT_PATH = Path.home() / ".openclaw" / "workspace" / "memory" / "agentic-compass.md"

# Agent-specific scoring axes
AXES = [
    "Completion Rate",
    "Response Relevance",
    "Tool Usage Quality",
    "Memory Consistency",
    "Initiative"
]

def read_file(path):
    """Read file content safely."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except (FileNotFoundError, IOError):
        return ""

def count_markers(content, pattern, flags=None):
    """Count regex matches in content."""
    if flags:
        return len(re.findall(pattern, content, flags))
    return len(re.findall(pattern, content, re.IGNORECASE))

def score_completion_rate(content):
    """Score based on tasks started vs finished."""
    started = count_markers(content, r'\[DOING\]|\[TODO\]|\[IN-PROGRESS\]')
    finished = count_markers(content, r'\[DONE\]|\[COMPLETED\]|\[✓\]')
    if started == 0:
        return 5.0, "No tasks started"
    ratio = finished / max(started, 1)
    score = min(ratio * 5, 5.0)
    return score, f"Finished {finished}/{started} tasks ({ratio*100:.0f}%)"

def score_response_relevance(content):
    """Score based on user confirmations vs corrections."""
    confirmations = count_markers(content, r'confirmed|correct|yes that works|thanks that helped')
    corrections = count_markers(content, r'wrong|incorrect|no that.s not|try again')
    total = confirmations + corrections
    if total == 0:
        return 5.0, "No feedback yet"
    ratio = confirmations / total
    score = ratio * 5
    return score, f"{confirmations} confirmations, {corrections} corrections"

def score_tool_usage(content):
    """Score based on tool errors and retries."""
    errors = count_markers(content, r'tool failed|error:|timeout|retrying')
    if errors == 0:
        return 5.0, "No tool errors"
    if errors < 3:
        return 4.0, f"{errors} minor errors"
    if errors < 10:
        return 2.5, f"{errors} errors detected"
    return 1.0, f"{errors} tool errors - high failure rate"

def score_memory_consistency(content, long_content):
    """Score based on context retention across sessions."""
    # Look for references to prior decisions
    references = count_markers(content + long_content, r'earlier i mentioned|as we discussed|following up on|continuing')
    # Check if contradictions exist (simplistic heuristic)
    contradictions = count_markers(content + long_content, r'actually i changed my mind|contradicting my earlier|never mind')
    if references == 0:
        return 3.0, "No cross-session references"
    if contradictions > 0:
        return 2.0, f"{contradictions} context contradictions"
    return 5.0, f"{references} context references, no contradictions"

def score_initiative(content):
    """Score based on proactive actions."""
    # Count proactive markers
    proactive = count_markers(content, r'i started|i proposed|i initiated|without being asked')
    if proactive == 0:
        return 2.0, "No proactive actions detected"
    if proactive == 1:
        return 3.5, f"{proactive} proactive action"
    if proactive < 5:
        return 4.5, f"{proactive} proactive actions"
    return 5.0, f"{proactive}+ proactive actions - excellent initiative"

def generate_plan(scores, details):
    """Generate an actionable plan based on weakest axis."""
    weakest_idx = min(range(len(scores)), key=lambda i: scores[i])
    weakest_axis = AXES[weakest_idx]

    plans = {
        "Completion Rate": [
            "focus on finishing [DOING] tasks before starting new ones",
            "prioritize one task and see it through to completion"
        ],
        "Response Relevance": [
            "ask clarifying questions before acting",
            "confirm understanding before proceeding with tasks"
        ],
        "Tool Usage Quality": [
            "add error checking and retry logic before tool calls",
            "validate tool inputs before invocation"
        ],
        "Memory Consistency": [
            "review MEMORY.md before starting new tasks",
            "summarize key decisions at end of each session"
        ],
        "Initiative": [
            "identify one high-value task and start without prompt",
            "propose improvements to existing workflows"
        ]
    }

    proactive = plans[weakest_axis][0]
    deferred = "retry any blocked items after diagnostic"
    avoidance = "stop repeating patterns that cause low scores"
    ship = "create one concrete artifact (doc, script, fix)"

    return proactive, deferred, avoidance, ship


def generate_proactive_actions(scores, details):
    """Generate 3 autonomous action ideas with probability scores and security tiers."""
    weakest_idx = min(range(len(scores)), key=lambda i: scores[i])
    weakest_axis = AXES[weakest_idx]

    # Base probability on weakest axis (lower score = higher urgency)
    urgency = 5.0 - scores[weakest_idx]  # 0 to 5
    base_prob = 0.5 + (urgency / 10.0)  # 50% to 100% baseline

    actions = []

    # Safe action (local-only, high probability)
    safe_actions = {
        "Completion Rate": ["review all [DOING] tasks and close completed ones", "prioritize top 3 unfinished tasks"],
        "Response Relevance": ["review recent interactions for clarity", "add confirmation checks to common workflows"],
        "Tool Usage Quality": ["document common error patterns", "create tool input validation checklist"],
        "Memory Consistency": ["summarize key decisions from this session", "update MEMORY.md with current context"],
        "Initiative": ["identify one improvement to existing workflows", "document a pattern that should be automated"]
    }
    actions.append({
        "action": safe_actions[weakest_axis][0],
        "probability": min(base_prob + 0.35, 0.95),  # High probability
        "tier": "safe"
    })

    # External action (network, medium probability)
    external_actions = {
        "Completion Rate": ["publish progress update to relevant channel", "share completed work with team"],
        "Response Relevance": ["request feedback on communication style", "clarify expectations with stakeholders"],
        "Tool Usage Quality": ["share tool usage insights with community", "document error patterns publicly"],
        "Memory Consistency": ["sync documentation to shared repo", "update project status publicly"],
        "Initiative": ["announce new feature or improvement", "share idea with relevant community"]
    }
    actions.append({
        "action": external_actions[weakest_axis][0],
        "probability": min(base_prob - 0.15, 0.75),  # Medium probability
        "tier": "external"
    })

    # Risky action (high-impact, lower probability)
    risky_actions = {
        "Completion Rate": ["re-evaluate and restructure workflow", "abandon low-value tasks to focus on high-impact ones"],
        "Response Relevance": ["change communication approach entirely", "implement new interaction patterns"],
        "Tool Usage Quality": ["refactor tool chain for better reliability", "replace unreliable tools with alternatives"],
        "Memory Consistency": ["reorganize entire memory structure", "migrate to new memory system"],
        "Initiative": ["build new tool to solve recurring problem", "propose major architectural change"]
    }
    actions.append({
        "action": risky_actions[weakest_axis][0],
        "probability": max(base_prob - 0.40, 0.25),  # Low probability
        "tier": "risky"
    })

    return actions

def generate_report(daily_content, long_content):
    """Generate full reflection report."""
    scores = [0] * 5  # Initialize with 5 zeros
    details = {}

    # Calculate scores for each axis
    scores[0], details["Completion Rate"] = score_completion_rate(daily_content)
    scores[1], details["Response Relevance"] = score_response_relevance(daily_content)
    scores[2], details["Tool Usage Quality"] = score_tool_usage(daily_content)
    scores[3], details["Memory Consistency"] = score_memory_consistency(daily_content, long_content)
    scores[4], details["Initiative"] = score_initiative(daily_content)

    # Calculate overall score
    overall = sum(scores) / len(scores)
    weakest_idx = min(range(len(scores)), key=lambda i: scores[i])
    weakest_axis = AXES[weakest_idx]

    # Generate plan
    proactive, deferred, avoidance, ship = generate_plan(scores, details)

    # Build report
    report = []
    report.append(f"Score: {overall:.1f}/5")
    report.append(f"Weakest axis: {weakest_axis}")
    report.append(f"  ({details[weakest_axis]})")
    report.append("")
    report.append("Plan:")
    report.append(f"- Proactive: {proactive}")
    report.append(f"- Deferred: {deferred}")
    report.append(f"- Avoidance: {avoidance}")
    report.append(f"- Ship: {ship}")

    return "\n".join(report), overall, weakest_axis, proactive, deferred, avoidance, ship

def main():
    parser = argparse.ArgumentParser(description="Agentic Compass — AI Agent Self-Reflection Tool")
    parser.add_argument("--write", action="store_true", help="Write plan to memory/agentic-compass.md")
    parser.add_argument("--json", action="store_true", help="Output as JSON for programmatic access")
    parser.add_argument("--proactive-mode", action="store_true", help="Generate 3 autonomous action ideas with probability scores")
    parser.add_argument("--daily", type=str, default=str(DEFAULT_DAILY_PATH), help="Path to daily memory file")
    parser.add_argument("--long", type=str, default=str(DEFAULT_LONG_PATH), help="Path to long-term memory file")

    args = parser.parse_args()

    # Read memory files
    daily_content = read_file(args.daily)
    long_content = read_file(args.long)

    # Generate report
    report, overall_score, weakest_axis, proactive, deferred, avoidance, ship = generate_report(daily_content, long_content)

    # Calculate scores for JSON output
    scores = [
        score_completion_rate(daily_content)[0],
        score_response_relevance(daily_content)[0],
        score_tool_usage(daily_content)[0],
        score_memory_consistency(daily_content, long_content)[0],
        score_initiative(daily_content)[0]
    ]
    weakest_score = min(scores)

    # Proactive mode
    actions = None
    if args.proactive_mode:
        actions = generate_proactive_actions(scores, {})

        print("\nAutonomous Action Ideas:")
        for i, action in enumerate(actions, 1):
            print(f"{i}. [{action['tier']}, {action['probability']*100:.0f}% probability] {action['action']}")
        print()

    # JSON output
    if args.json:
        output = {
            "overall_score": overall_score,
            "weakest_axis": weakest_axis,
            "weakest_score": weakest_score,
            "plan": {
                "proactive": proactive,
                "deferred": deferred,
                "avoidance": avoidance,
                "ship": ship
            },
            "timestamp": datetime.now().isoformat()
        }
        if args.proactive_mode:
            output["autonomous_actions"] = actions
        print(json.dumps(output, indent=2))

    # Default text output
    elif not args.proactive_mode or args.write:
        print(report)

    # Write to file if requested
    if args.write:
        output_path = Path(args.daily).parent / "agentic-compass.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'a', encoding='utf-8') as f:
            f.write(f"\n\n## Agentic Compass Report — {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            f.write(report)
            f.write("\n")

        print(f"\n✓ Report written to {output_path}")

if __name__ == "__main__":
    main()
