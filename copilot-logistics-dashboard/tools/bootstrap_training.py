"""Restore the default classroom feature after a fresh GitHub clone."""
from pathlib import Path
import json


def bootstrap():
    root = Path(__file__).resolve().parents[1]
    pointer = root / ".specify/feature.json"
    if pointer.exists():
        active = json.loads(pointer.read_text(encoding="utf-8-sig"))
        directory = active.get("feature_directory")
        if not isinstance(directory, str):
            raise ValueError("Existing feature.json must contain feature_directory")
        feature = (root / directory).resolve()
        if not feature.is_relative_to(root) or not (feature / "spec.md").is_file():
            raise ValueError("Existing feature is invalid; it was preserved for manual review")
        result = {"status": "preserved", "feature": directory}
    else:
        config = json.loads((root / ".specify/training.json").read_text(encoding="utf-8-sig"))
        directory = config["feature_directory"]
        feature = (root / directory).resolve()
        if not feature.is_relative_to(root) or not (feature / "spec.md").is_file():
            raise ValueError("The packaged default classroom feature is missing or outside this project")
        # Exclusive creation preserves any pointer created concurrently.
        with pointer.open("x", encoding="utf-8") as f:
            json.dump({"feature_directory": directory}, f, ensure_ascii=False, indent=2)
            f.write("\n")
        result = {"status": "restored", "feature": directory}
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    bootstrap()
