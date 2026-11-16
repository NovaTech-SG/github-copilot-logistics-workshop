"""Check the classroom starting point without manufacturing a feature."""
from pathlib import Path
import json
from training_state import active_feature


def bootstrap(root=None):
    root = Path(root or Path(__file__).resolve().parents[1]).resolve()
    feature = active_feature(root)
    result = {"status": "preserved" if feature else "awaiting_specification",
              "feature": feature.relative_to(root).as_posix() if feature else None}
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    bootstrap()
