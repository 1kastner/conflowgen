import unittest

from conflowgen.tools.continuous_distribution import Uniform


class TestUniform(unittest.TestCase):

    def setUp(self) -> None:
        self.cln = Uniform(minimum=1, maximum=15)

    def assertArrayEqual(self, array_1, array_2, msg=""):
        self.assertListEqual(list(array_1), list(array_2), msg=msg)  # pylint: disable=invalid-name

    def test_minimum_is_respected(self):
        self.assertArrayEqual(self.cln.get_probabilities([0.5, 4]), [0, 1])
        self.assertArrayEqual(self.cln.get_probabilities([0, 6]), [0, 1])
        self.assertArrayEqual(self.cln.get_probabilities([-2, 5]), [0, 1])

    def test_maximum_is_respected(self):
        self.assertArrayEqual(self.cln.get_probabilities([14, 15.1]), [1, 0])
        self.assertArrayEqual(self.cln.get_probabilities([14, 16]), [1, 0])
        self.assertArrayEqual(self.cln.get_probabilities([14, 100]), [1, 0])
