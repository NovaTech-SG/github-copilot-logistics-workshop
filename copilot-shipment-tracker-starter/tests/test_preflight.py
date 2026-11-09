import unittest
from services.store import validate_change
from services.queries import build_query


class PreparedRulesTests(unittest.TestCase):
    def test_allowed_transition_and_trim(self):
        self.assertEqual(validate_change('OPEN', 'IN_PROGRESS', ' 跟进中 '), '跟进中')

    def test_invalid_rule_inputs(self):
        for status,note in (('RESOLVED','跳过'),('IN_PROGRESS','  '),('IN_PROGRESS','a'*1001)):
            with self.subTest(status=status), self.assertRaises(ValueError):
                validate_change('OPEN',status,note)

    def test_query_rejects_invalid_id(self):
        with self.assertRaises(ValueError):
            build_query('`catalog`.`schema`', "x' OR 1=1")


if __name__ == '__main__':
    unittest.main()
