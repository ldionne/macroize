#/usr/bin/env python

import macroize
import unittest


class TestChecker(unittest.TestCase):
    """Unit tests for the Checker class."""

    def setUp(self):
        # hack to be able to pass strings
        self.check = macroize.Checker()._check

    def test_should_have_no_failures_with_empty_input(self):
        self.assertListEqual([ ], self.check(""))

    def test_should_not_detect_anything_not_enclosed_in_tags(self):
        input = """
        foobar
        not enclosed
        a == 4
        1 == 1
        """
        self.assertListEqual([ ], self.check(input))

    def test_should_not_detect_failures_when_both_sides_match(self):
        input = """
        [[[
        1 == 1
        abc == abc
        ]]]
        """
        self.assertListEqual([ ], self.check(input))

    def test_should_ignore_empty_lines_inside_tags(self):
        input = """
        [[[

        ]]]
        """
        self.assertListEqual([ ], self.check(input))

    def test_should_detect_failure_when_both_sides_dont_match(self):
        input = """
        [[[
        1 == 3
        abc == abb
        ]]]
        """
        self.assertSetEqual({(3, "1==3"), (4, "abc==abb")},
                            set(self.check(input)))

    def test_should_strip_multiple_whitespaces_according_to_trans_1(self):
        input = """
        [[[
        abc    ==abc
        a b    c == a b c
        ]]]
        """
        self.assertListEqual([ ], self.check(input))

    def test_should_strip_spaces_around_special_characters(self):
        input = """
        [[[
        a,b(c)d-e+f*g=h == a  ,b (c )d - e+ f*g =h
        ]]]
        """
        self.assertListEqual([ ], self.check(input))

    def test_with_multiple_blocks(self):
        input = """
        [[[
        2 == 4
        ]]]

        [[[
        1 == 3
        ]]]
        """
        self.assertSetEqual({(3, "2==4"), (7, "1==3")},set(self.check(input)))


if __name__ == "__main__":
    unittest.main()
