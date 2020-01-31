import unittest
from isign.identifier_matcher import IdentifierMatcher
from isign.exceptions import BadIdentifier


class TestIdentifierMatcher(unittest.TestCase):
    def test_bad_input(self):
        with self.assertRaises(BadIdentifier):
            IdentifierMatcher.get_score('', '')
        with self.assertRaises(BadIdentifier):
            IdentifierMatcher.get_score(None, None)
        with self.assertRaises(BadIdentifier):
            IdentifierMatcher.get_score('a', 'a.*.b')

    def test_no_match(self):
        self.assertEqual(0, IdentifierMatcher.get_score('a', 'b'))
        self.assertEqual(0, IdentifierMatcher.get_score('ab', 'ba'))

    def test_exact_match(self):
        self.assertEqual(1, IdentifierMatcher.get_score('a', 'a'))
        self.assertEqual(2, IdentifierMatcher.get_score('a.b', 'a.b'))
        self.assertEqual(4, IdentifierMatcher.get_score('ABC.def.ghi.jkl', 'ABC.def.ghi.jkl'))

    def test_pattern_too_specific(self):
        self.assertEqual(0, IdentifierMatcher.get_score('a.b', 'a'))
        self.assertEqual(0, IdentifierMatcher.get_score('a', 'a.b'))
        self.assertEqual(0, IdentifierMatcher.get_score('a.b', 'a.b.c'))
        self.assertEqual(0, IdentifierMatcher.get_score('a.b', 'a.b.*'))

    def test_wildcard_matches(self):
        self.assertEqual(1, IdentifierMatcher.get_score('ABC.def.ghi', 'ABC.*'))
        self.assertEqual(3, IdentifierMatcher.get_score('ABC.def.ghi.jkl', 'ABC.def.ghi.*'))

    def test_wildcard_no_match(self):
        self.assertEqual(0, IdentifierMatcher.get_score('ABC.def.ghi', 'ABC.xyz.*'))
        self.assertEqual(0, IdentifierMatcher.get_score('ABC.def.ghi', 'ABC.def.ghi.*'))

    def test_best_match(self):
        self.assertEqual(None, IdentifierMatcher.get_best_pattern('ABC.def.ghi', []))
        self.assertEqual(None, IdentifierMatcher.get_best_pattern('ABC.def.ghi', ['XYZ']))
        self.assertEqual(None, IdentifierMatcher.get_best_pattern('ABC.def.ghi', ['ABC', 'XYZ']))
        self.assertEqual('ABC.*', IdentifierMatcher.get_best_pattern('ABC.def.ghi', ['ABC.*', 'XYZ']))
        self.assertEqual(
            'ABC.def.*', 
            IdentifierMatcher.get_best_pattern('ABC.def.ghi', ['ABC.*', 'ABC.def.*', 'XYZ'])
        )
        self.assertEqual(
            'ABC.def.ghi', 
            IdentifierMatcher.get_best_pattern('ABC.def.ghi', ['ABC.*', 'ABC.def.ghi', 'XYZ'])
        )
        self.assertEqual(
            'ABC.*',
            IdentifierMatcher.get_best_pattern('ABC.def.ghi', ['ABC.*', 'ABC.def.jkl', 'XYZ'])
        )


if __name__ == '__main__':
    unittest.main()
