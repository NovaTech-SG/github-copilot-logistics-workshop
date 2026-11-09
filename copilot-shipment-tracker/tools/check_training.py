"""Validate the training Spec Kit checkpoint without reading credentials or querying data."""
from pathlib import Path
import json
import re


def main():
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / ".specify/training.json").read_text(encoding="utf-8-sig"))
    if not (root / ".specify/feature.json").exists():
        raise SystemExit("Run: uv run --locked python tools/bootstrap_training.py")
    active = json.loads((root / ".specify/feature.json").read_text(encoding="utf-8-sig"))
    integration = json.loads((root / ".specify/integration.json").read_text(encoding="utf-8-sig"))
    assert integration["version"] == config["specify_cli_version"] == "1.3.2"
    assert integration["default_integration"] == "copilot"
    assert active["feature_directory"] == config["feature_directory"]
    feature = (root / active["feature_directory"]).resolve()
    assert feature.is_relative_to(root), "Active feature must stay in the current project"
    for name in ("spec.md", "plan.md", "tasks.md", "research.md", "data-model.md", "quickstart.md", "contracts/api.md", "checklists/requirements.md"):
        assert (feature / name).is_file(), name
    spec = (feature / "spec.md").read_text(encoding="utf-8")
    for heading in ("## User Scenarios & Testing", "## Requirements", "## Success Criteria", "## Assumptions"):
        assert heading in spec, heading
    assert "NEEDS CLARIFICATION" not in spec
    required = ("constitution", "specify", "clarify", "plan", "tasks", "implement", "analyze", "converge")
    for name in required:
        skill = root / f".github/skills/speckit-{name}/SKILL.md"
        text = skill.read_text(encoding="utf-8")
        assert 'author: "github-spec-kit"' in text, name
        assert "disable-model-invocation: true" in text, name
    for alias, destination in (("spec.md", "spec.md"), ("tasks.md", "tasks.md")):
        assert config["feature_directory"] + "/" + destination in (root / "docs" / alias).read_text(encoding="utf-8")
    tasks = (feature / "tasks.md").read_text(encoding="utf-8")
    lines = [line for line in tasks.splitlines() if re.match(r"- \[[ xX]\] T\d+", line)]
    assert len(lines) >= 10, "Missing executable tasks"
    ids = [re.search(r"T\d+", line).group() for line in lines]
    assert len(ids) == len(set(ids))
    for n, ident in enumerate(ids, 1):
        assert ident == f"T{n:03d}", "Task IDs must be sequential"
    checklist = (feature / "checklists/requirements.md").read_text(encoding="utf-8")
    assert "- [ ]" not in checklist, "Spec quality checklist needs review"
    if config["checkpoint"] == "learner-start":
        if config["feature_directory"].endswith("carrier-dashboard"):
            assert "raise NotImplementedError" in (root / "services/dashboard.py").read_text(encoding="utf-8")
        else:
            assert "raise NotImplementedError" in (root / "services/store.py").read_text(encoding="utf-8")
    print(json.dumps({"status": "ready", "specify_cli_version": integration["version"], "feature": active["feature_directory"], "checkpoint": config["checkpoint"], "tasks": len(lines), "live_mcp_checked": False, "copilot_chat_executed": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
