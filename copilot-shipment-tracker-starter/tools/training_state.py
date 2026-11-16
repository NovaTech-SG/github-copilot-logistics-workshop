"""Inspect learner-created artifacts without generating or overwriting them."""
import json
from pathlib import Path
import re


def resolve_feature(root, directory):
    """Validate a selection before reading it or restoring a local pointer."""
    root = Path(root).resolve()
    if not isinstance(directory, str) or not directory.strip():
        raise ValueError('feature.json must contain a nonempty feature_directory')
    feature = (root / directory).resolve()
    if not feature.is_relative_to((root / 'specs').resolve()) or feature == root / 'specs':
        raise ValueError('Active feature must be a directory under this project\'s specs/')
    spec = feature / 'spec.md'
    if not spec.is_file() or not spec.read_text(encoding='utf-8-sig').strip():
        raise ValueError('Active feature has no written spec.md; existing pointer was preserved for review')
    return feature


def active_feature(root):
    root = Path(root).resolve()
    pointer = root / '.specify/feature.json'
    if not pointer.exists():
        if any((root / 'specs').glob('*/spec.md')):
            raise ValueError('Specs exist but no active feature is selected. Run tools/bootstrap_training.py; for multiple features, select one in .specify/feature.json. Existing work was preserved.')
        return None
    active = json.loads(pointer.read_text(encoding='utf-8-sig'))
    return resolve_feature(root, active.get('feature_directory'))


def inspect_stage(root):
    root = Path(root).resolve()
    feature = active_feature(root)
    if feature is None:
        return {'stage': 'requirements', 'feature': None, 'tasks': 0, 'next': '/speckit-specify'}
    spec = (feature / 'spec.md').read_text(encoding='utf-8-sig')
    for heading in ('## User Scenarios & Testing', '## Requirements', '## Success Criteria'):
        if heading not in spec:
            raise ValueError(f'Spec is missing a required section: {heading}')
    plan = feature / 'plan.md'
    tasks = feature / 'tasks.md'
    stage, following, count = 'specified', '/speckit-clarify or /speckit-plan', 0
    if plan.exists():
        if not plan.read_text(encoding='utf-8-sig').strip():
            raise ValueError('plan.md is empty; finish planning before generating tasks')
        stage, following = 'planned', '/speckit-tasks'
    if tasks.exists():
        if not plan.exists():
            raise ValueError('tasks.md exists without plan.md; complete the plan first')
        ids = re.findall(r'^- \[[ xX]\] (T\d+)\b', tasks.read_text(encoding='utf-8-sig'), re.M)
        if not ids or len(ids) != len(set(ids)):
            raise ValueError('tasks.md must contain tasks with unique IDs')
        count = len(ids)
        stage, following = 'tasks-generated', '/speckit-analyze then scoped /speckit-implement'
    checklist = feature / 'checklists/requirements.md'
    pending = '[NEEDS CLARIFICATION' in spec or (checklist.exists() and '- [ ]' in checklist.read_text(encoding='utf-8-sig'))
    return {'stage': stage, 'feature': feature.relative_to(root).as_posix(), 'tasks': count,
            'requirements_review_pending': pending, 'next': following}
