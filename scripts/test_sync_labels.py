"""Unit tests for sync_labels.py. Run: python3 -m unittest discover -s scripts"""

import json
import os
import unittest

import sync_labels as s


def label(name, color="AABBCC", description="desc", aliases=None):
    out = {"name": name, "color": color, "description": description}
    if aliases is not None:
        out["aliases"] = aliases
    return out


class ValidateTest(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(s.validate([label("a"), label("b", aliases=["old"])]), [])

    def test_empty(self):
        self.assertTrue(s.validate([]))

    def test_bad_color(self):
        self.assertIn("color", s.validate([label("a", color="#AABBCC")])[0])

    def test_missing_description(self):
        self.assertIn("description", s.validate([label("a", description="")])[0])

    def test_long_description(self):
        self.assertIn("over", s.validate([label("a", description="x" * 101)])[0])

    def test_duplicate_name_ignores_case(self):
        self.assertIn("already used", s.validate([label("Bug"), label("bug")])[0])

    def test_alias_clashes_with_name(self):
        self.assertIn("already used", s.validate([label("a"), label("b", aliases=["A"])])[0])

    def test_unknown_field(self):
        bad = label("a")
        bad["colour"] = "AABBCC"
        self.assertIn("unknown fields", s.validate([bad])[0])


class PlanTest(unittest.TestCase):
    def test_create_missing(self):
        actions, extras = s.plan([label("a")], [])
        self.assertEqual(actions, [("create", label("a"))])
        self.assertEqual(extras, [])

    def test_no_change(self):
        actions, extras = s.plan([label("a")], [label("a", color="aabbcc")])
        self.assertEqual(actions, [])

    def test_update_color_and_description(self):
        actions, _ = s.plan([label("a")], [label("a", color="000000", description="old")])
        self.assertEqual(actions, [("update", "a", label("a"))])

    def test_update_name_case(self):
        actions, _ = s.plan([label("Bug")], [label("bug")])
        self.assertEqual(actions, [("update", "bug", label("Bug"))])

    def test_rename_alias(self):
        want = label("type: bug", aliases=["bug"])
        actions, extras = s.plan([want], [label("bug", color="D73A4A")])
        self.assertEqual(actions, [("rename", "bug", want)])
        self.assertEqual(extras, [])

    def test_existing_name_wins_over_alias(self):
        want = label("type: bug", aliases=["bug"])
        actions, extras = s.plan([want], [label("type: bug"), label("bug")])
        self.assertEqual(actions, [])
        self.assertEqual(extras, ["bug"])

    def test_never_deletes(self):
        actions, extras = s.plan([label("a")], [label("a"), label("custom")])
        self.assertEqual(actions, [])
        self.assertEqual(extras, ["custom"])

    def test_null_description_from_api(self):
        actions, _ = s.plan([label("a")], [{"name": "a", "color": "aabbcc", "description": None}])
        self.assertEqual(actions, [("update", "a", label("a"))])


class ApplyTest(unittest.TestCase):
    def test_calls(self):
        calls = []
        actions = [("create", label("new")), ("rename", "old name", label("type: bug"))]
        s.apply("o/r", actions, run=lambda args, stdin: calls.append((args, json.loads(stdin))))
        self.assertEqual(calls[0][0], ["api", "--method", "POST", "repos/o/r/labels", "--input", "-"])
        self.assertEqual(calls[0][1]["name"], "new")
        self.assertEqual(calls[1][0][3], "repos/o/r/labels/old%20name")
        self.assertEqual(calls[1][1]["new_name"], "type: bug")


class LabelsFileTest(unittest.TestCase):
    """Checks the real labels file when CI passes it in as JSON."""

    def test_labels_file(self):
        path = os.environ.get("LABELS_JSON")
        if not path:
            self.skipTest("LABELS_JSON not set")
        with open(path, encoding="utf-8") as f:
            labels = json.load(f)
        self.assertEqual(s.validate(labels), [])
        names = {l["name"] for l in labels}
        for required in ["status: needs-triage", "status: pending-info", "duplicate",
                         "security", "pinned", "priority: critical", "stale",
                         "good first issue", "help wanted"]:
            self.assertIn(required, names, "the workflows depend on this label")


if __name__ == "__main__":
    unittest.main()
