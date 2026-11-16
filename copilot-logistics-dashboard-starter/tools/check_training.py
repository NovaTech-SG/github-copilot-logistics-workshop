"""Check infrastructure and the current SDD stage, without credentials or queries."""
from pathlib import Path
import json
from training_state import inspect_stage


def main():
    root = Path(__file__).resolve().parents[1]
    config = json.loads((root / '.specify/training.json').read_text(encoding='utf-8-sig'))
    integration = json.loads((root / '.specify/integration.json').read_text(encoding='utf-8-sig'))
    assert integration['version'] == config['specify_cli_version'] == '1.3.2'
    assert integration['default_integration'] == config['integration'] == 'copilot'
    for name in ('constitution', 'specify', 'clarify', 'plan', 'tasks', 'implement', 'analyze', 'converge'):
        text = (root / f'.github/skills/speckit-{name}/SKILL.md').read_text(encoding='utf-8')
        assert 'author: "github-spec-kit"' in text, name
        assert 'disable-model-invocation: true' in text, name
    for relative in ('AGENTS.md', '.specify/memory/constitution.md', 'mockup/index.html',
                     'docs/data-source.md', 'docs/prompts.md'):
        assert (root / relative).is_file(), relative
    state = inspect_stage(root)
    print(json.dumps({'status': 'ready', 'specify_cli_version': integration['version'],
                      **state, 'business_verified': False, 'live_mcp_checked': False,
                      'copilot_chat_executed': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
