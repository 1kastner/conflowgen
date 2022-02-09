import unittest

from conflowgen import ModeOfTransport, ContainerLength
from conflowgen.tools import hashable


class TestHashable(unittest.TestCase):

    def test_mutable_collections_are_hashable(self):
        self.assertFalse(hashable([]))
        self.assertFalse(hashable({}))

    def test_enums_are_hashable(self):
        self.assertTrue(hashable(ModeOfTransport.feeder))
        self.assertTrue(hashable(ContainerLength.forty_feet))
