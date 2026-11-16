"""Keep an empty start; restore only the selection of a sole existing feature."""
from pathlib import Path
import json
from training_state import active_feature, resolve_feature


def bootstrap(root=None):
    root = Path(root or Path(__file__).resolve().parents[1]).resolve()
    pointer = root / '.specify/feature.json'
    status = None
    if not pointer.exists():
        specs = list((root / 'specs').glob('*/spec.md'))
        if len(specs) > 1:
            raise ValueError('Multiple specs exist but no active feature is selected. Select one in .specify/feature.json; existing work was preserved.')
        if specs:
            directory = specs[0].parent.relative_to(root).as_posix()
            resolve_feature(root, directory)
            pointer.parent.mkdir(parents=True, exist_ok=True)
            with pointer.open('x', encoding='utf-8') as stream:
                json.dump({'feature_directory': directory}, stream, ensure_ascii=False, indent=2)
                stream.write('\n')
            status = 'restored_selection'
    feature = active_feature(root)
    result = {"status": status or ("preserved" if feature else "awaiting_specification"),
              "feature": feature.relative_to(root).as_posix() if feature else None}
    print(json.dumps(result, ensure_ascii=False))
    return result


if __name__ == "__main__":
    bootstrap()
