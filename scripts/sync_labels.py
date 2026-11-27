#!/usr/bin/env python3
"""Sync GitHub labels in one repository from labels.yml.

Usage (labels.yml is converted to JSON first, so this script needs only the
Python standard library and the gh CLI):

    yq -o=json labels.yml | python3 scripts/sync_labels.py --repo OWNER/NAME [--dry-run]
    yq -o=json labels.yml | python3 scripts/sync_labels.py --validate

The script creates missing labels, updates changed ones and renames aliases.
It never deletes a label. Labels it does not know are listed as extras.
"""

import argparse
import json
import re
import subprocess
import sys
import urllib.parse

COLOR_RE = re.compile(r"^[0-9A-Fa-f]{6}$")
MAX_DESCRIPTION = 100


def validate(labels):
    """Return a list of problems with the desired labels. Empty means valid."""
    problems = []
    if not isinstance(labels, list) or not labels:
        return ["labels file must be a non-empty list"]
    seen = {}
    for i, label in enumerate(labels):
        where = f"label {i + 1}"
        if not isinstance(label, dict):
            problems.append(f"{where}: must be a mapping")
            continue
        name = label.get("name")
        if not isinstance(name, str) or not name.strip():
            problems.append(f"{where}: missing name")
            continue
        where = f"label {name!r}"
        unknown = set(label) - {"name", "color", "description", "aliases"}
        if unknown:
            problems.append(f"{where}: unknown fields {sorted(unknown)}")
        if not COLOR_RE.match(str(label.get("color", ""))):
            problems.append(f"{where}: color must be 6 hex digits without #")
        description = label.get("description")
        if not isinstance(description, str) or not description.strip():
            problems.append(f"{where}: missing description")
        elif len(description) > MAX_DESCRIPTION:
            problems.append(f"{where}: description over {MAX_DESCRIPTION} characters")
        aliases = label.get("aliases", [])
        if not isinstance(aliases, list) or not all(isinstance(a, str) for a in aliases):
            problems.append(f"{where}: aliases must be a list of names")
            aliases = []
        for key in [name] + aliases:
            k = key.lower()
            if k in seen:
                problems.append(f"{where}: {key!r} already used by {seen[k]!r}")
            else:
                seen[k] = name
    return problems


def plan(desired, existing):
    """Work out the changes needed. Pure function, no API calls.

    desired:  list of {name, color, description, aliases?}
    existing: list of {name, color, description} from the GitHub API
    Returns (actions, extras). Each action is a tuple:
      ("create", label) | ("update", current_name, label) | ("rename", old_name, label)
    """
    by_name = {e["name"].lower(): e for e in existing}
    used = set()
    actions = []
    for label in desired:
        want_color = label["color"].lower()
        want_desc = label["description"]
        current = by_name.get(label["name"].lower())
        if current:
            used.add(current["name"].lower())
            if (
                current["name"] != label["name"]
                or (current.get("color") or "").lower() != want_color
                or (current.get("description") or "") != want_desc
            ):
                actions.append(("update", current["name"], label))
            continue
        alias = next(
            (by_name[a.lower()] for a in label.get("aliases", []) if a.lower() in by_name),
            None,
        )
        if alias:
            used.add(alias["name"].lower())
            actions.append(("rename", alias["name"], label))
        else:
            actions.append(("create", label))
    extras = sorted(e["name"] for e in existing if e["name"].lower() not in used)
    return actions, extras


def gh(args, stdin=None):
    """Run the gh CLI and return its stdout. Arguments are never passed through a shell."""
    result = subprocess.run(["gh", *args], input=stdin, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])} failed: {result.stderr.strip()}")
    return result.stdout


def fetch_existing(repo):
    out = gh(["api", "--paginate", "--slurp", f"repos/{repo}/labels?per_page=100"])
    pages = json.loads(out)
    return [label for page in pages for label in page]


def apply(repo, actions, run=gh):
    for action in actions:
        label = action[-1]
        body = {"color": label["color"].upper(), "description": label["description"]}
        if action[0] == "create":
            body["name"] = label["name"]
            run(["api", "--method", "POST", f"repos/{repo}/labels", "--input", "-"], json.dumps(body))
        else:
            body["new_name"] = label["name"]
            path = urllib.parse.quote(action[1], safe="")
            run(["api", "--method", "PATCH", f"repos/{repo}/labels/{path}", "--input", "-"], json.dumps(body))


def describe(action):
    if action[0] == "create":
        return f"create  {action[1]['name']}"
    if action[0] == "rename":
        return f"rename  {action[1]} -> {action[2]['name']}"
    return f"update  {action[2]['name']}"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", help="OWNER/NAME to sync")
    parser.add_argument("--dry-run", action="store_true", help="print changes, change nothing")
    parser.add_argument("--validate", action="store_true", help="only check the labels file")
    args = parser.parse_args(argv)

    labels = json.load(sys.stdin)
    problems = validate(labels)
    if problems:
        for p in problems:
            print(f"error: {p}", file=sys.stderr)
        return 1
    if args.validate:
        print(f"{len(labels)} labels, all valid")
        return 0
    if not args.repo or not re.match(r"^[\w.-]+/[\w.-]+$", args.repo):
        parser.error("--repo OWNER/NAME is required")

    actions, extras = plan(labels, fetch_existing(args.repo))
    for action in actions:
        print(("would " if args.dry_run else "") + describe(action))
    for name in extras:
        print(f"extra   {name} (not in labels.yml, left in place)")
    if not actions:
        print("labels already in sync")
    if not args.dry_run:
        apply(args.repo, actions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
