import unittest
from isign.provisioner import IdMatcher
from isign.exceptions import BadIdentifier


class TestWildcardMatch(unittest.TestCase):
    def test_bad_input(self):
        with self.assertRaises(BadIdentifier):
            IdMatcher.get_score('', '')
        with self.assertRaises(BadIdentifier):
            IdMatcher.get_score(None, None)

    def test_no_match(self):
        self.assertEqual(IdMatcher.get_score('a', 'b'), 0)
        self.assertEqual(IdMatcher.get_score('ab', 'ba'), 0)

    def test_exact_match(self):
        self.assertEqual(IdMatcher.get_score('a', 'a'), 1)
        self.assertEqual(IdMatcher.get_score('a.b', 'a.b'), 2)
        self.assertEqual(IdMatcher.get_score('ABC.def.ghi.jkl', 'ABC.def.ghi.jkl'), 4)

    def test_wildcard_too_specific(self):
        self.assertEqual(IdMatcher.get_score('a.b', 'a.b.c'), 0)
        self.assertEqual(IdMatcher.get_score('a.b', 'a.b.*'), 0)

    def test_wildcard_match(self):
        self.assertEqual(IdMatcher.get_score('ABC.def.ghi', 'ABC.*'), 1)
        self.assertEqual(IdMatcher.get_score('ABC.def.ghi.jkl', 'ABC.def.ghi.*'), 3)


if __name__ == '__main__':
    unittest.main()
