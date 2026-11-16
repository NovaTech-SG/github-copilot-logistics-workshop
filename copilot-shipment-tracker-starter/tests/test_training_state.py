"""Regression checks for a genuinely empty starting point and learner progress."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from bootstrap_training import bootstrap
from training_state import inspect_stage


SPEC = '''# Test feature
## User Scenarios & Testing
An operator saves a follow-up.
## Requirements
The note is stored locally.
## Success Criteria
Reading the exception returns the saved note.
'''


class TrainingStateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / '.specify').mkdir()
        (self.root / 'specs').mkdir()
        (self.root / 'specs/.gitkeep').touch()
        self.pointer = self.root / '.specify/feature.json'

    def feature(self, directory='specs/003-followup-save'):
        feature = self.root / directory
        feature.mkdir(parents=True)
        (feature / 'spec.md').write_text(SPEC, encoding='utf-8')
        self.pointer.write_text(json.dumps({'feature_directory': directory}), encoding='utf-8')
        return feature

    def run_bootstrap(self):
        with contextlib.redirect_stdout(io.StringIO()):
            return bootstrap(self.root)

    def test_fresh_clone_does_not_generate_feature_or_pointer(self):
        self.assertEqual(self.run_bootstrap()['status'], 'awaiting_specification')
        self.assertEqual(self.run_bootstrap()['status'], 'awaiting_specification')
        self.assertFalse(self.pointer.exists())
        self.assertEqual(list((self.root / 'specs').iterdir()), [self.root / 'specs/.gitkeep'])
        self.assertEqual(inspect_stage(self.root)['stage'], 'requirements')

    def test_only_spec_is_a_valid_intermediate_stage(self):
        self.feature()
        state = inspect_stage(self.root)
        self.assertEqual(state['stage'], 'specified')
        self.assertEqual(state['tasks'], 0)

    def test_document_stages_advance_without_prepared_answers(self):
        feature = self.feature()
        (feature / 'plan.md').write_text('# Learner plan', encoding='utf-8')
        self.assertEqual(inspect_stage(self.root)['stage'], 'planned')
        (feature / 'tasks.md').write_text('- [ ] T001 Verify inputs\n- [ ] T002 Implement P1\n', encoding='utf-8')
        state = inspect_stage(self.root)
        self.assertEqual(state['stage'], 'tasks-generated')
        self.assertEqual(state['tasks'], 2)

    def test_nondefault_active_feature_and_learner_edits_are_preserved(self):
        feature = self.feature()
        pointer_before = self.pointer.read_bytes()
        spec_before = (feature / 'spec.md').read_bytes()
        self.assertEqual(self.run_bootstrap(), {'status': 'preserved', 'feature': 'specs/003-followup-save'})
        self.assertEqual(self.pointer.read_bytes(), pointer_before)
        self.assertEqual((feature / 'spec.md').read_bytes(), spec_before)

    def test_missing_selection_does_not_silently_choose_or_overwrite_work(self):
        feature = self.feature()
        self.pointer.unlink()
        with self.assertRaisesRegex(ValueError, 'no active feature'):
            self.run_bootstrap()
        self.assertEqual((feature / 'spec.md').read_text(encoding='utf-8'), SPEC)
        self.assertFalse(self.pointer.exists())

    def test_invalid_selection_stays_untouched(self):
        for directory in ('../outside', 'docs/feature', 'specs', 'specs/missing'):
            with self.subTest(directory=directory):
                self.pointer.write_text(json.dumps({'feature_directory': directory}), encoding='utf-8')
                original = self.pointer.read_bytes()
                with self.assertRaises(ValueError):
                    self.run_bootstrap()
                self.assertEqual(self.pointer.read_bytes(), original)

    def test_empty_spec_is_not_a_generated_specification(self):
        feature = self.feature()
        (feature / 'spec.md').write_text('', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'no written spec'):
            inspect_stage(self.root)

    def test_tasks_require_a_plan(self):
        feature = self.feature()
        (feature / 'tasks.md').write_text('- [ ] T001 Implement', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'without plan'):
            inspect_stage(self.root)

    def test_duplicate_task_ids_are_rejected(self):
        feature = self.feature()
        (feature / 'plan.md').write_text('# Plan', encoding='utf-8')
        (feature / 'tasks.md').write_text('- [ ] T001 First\n- [ ] T001 Second\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'unique IDs'):
            inspect_stage(self.root)

    def test_clarification_and_unreviewed_requirements_are_reported(self):
        feature = self.feature()
        (feature / 'spec.md').write_text(SPEC + '\n[NEEDS CLARIFICATION: scope]\n', encoding='utf-8')
        self.assertTrue(inspect_stage(self.root)['requirements_review_pending'])
        (feature / 'spec.md').write_text(SPEC, encoding='utf-8')
        (feature / 'checklists').mkdir()
        checklist = feature / 'checklists/requirements.md'
        checklist.write_text('- [ ] Review scope', encoding='utf-8')
        self.assertTrue(inspect_stage(self.root)['requirements_review_pending'])
        checklist.write_text('- [x] Review scope', encoding='utf-8')
        self.assertFalse(inspect_stage(self.root)['requirements_review_pending'])


if __name__ == '__main__':
    unittest.main()
