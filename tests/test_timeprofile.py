import unittest
import numpy as np

from timeprofiles import TimeProfile


class TestTimeProfile(unittest.TestCase):
    def setUp(self):
        self.tp = TimeProfile()

    def test_init(self):
        starts = [0, 1]
        ends = [3, 4]
        self.tp = TimeProfile(starts, ends)
        self.assertEqual("[(0, 3), (1, 4)]", str(self.tp))

    def test_init_exc(self):
        starts = [0, 3]
        ends = []
        self.assertRaises(Exception, TimeProfile, starts)
        self.assertRaises(Exception, TimeProfile, starts, ends)

        starts = [0, 3]
        ends = [1, 2]
        self.assertRaises(Exception, TimeProfile, starts, ends)

    def test_add(self):
        self.tp.add(0, 3)
        self.tp.add(1, 4)
        self.assertEqual("[(0, 3), (1, 4)]", str(self.tp))

    def test_add_exc(self):
        self.assertRaises(Exception, self.tp.add, 3, 0)

    def test_clear(self):
        self.tp.add(0, 3)
        self.tp.add(1, 4)
        self.tp.clear()
        self.assertEqual("[]", str(self.tp))

        self.tp.clear()
        self.assertEqual("[]", str(self.tp))

    def test_len(self):
        self.assertEqual(0, len(self.tp))

        self.tp.add(0, 3)
        self.assertEqual(1, len(self.tp))

        self.tp.add(1, 4)
        self.assertEqual(2, len(self.tp))

    def test_min(self):
        self.tp.add(5, 6)
        self.tp.add(3, 8)
        self.assertEqual(3, self.tp.min())

        self.tp.add(1, 2)
        self.assertEqual(1, self.tp.min())

    def test_min_exc(self):
        self.assertRaises(Exception, self.tp.min)

    def test_max(self):
        self.tp.add(5, 6)
        self.tp.add(1, 2)
        self.assertEqual(6, self.tp.max())

        self.tp.add(3, 8)
        self.assertEqual(8, self.tp.max())

    def test_max_exc(self):
        self.assertRaises(Exception, self.tp.max)

    def test_profile(self):
        starts, ends = self.tp.profile
        self.assertEqual("[]", str(starts))
        self.assertEqual("[]", str(ends))

        self.tp.add(0, 3)
        self.tp.add(1, 4)
        starts, ends = self.tp.profile
        self.assertEqual("[0, 1]", str(starts))
        self.assertEqual("[3, 4]", str(ends))

    def test_profile_arr(self):
        self.tp.add(0, 3)
        self.tp.add(1, 4)
        starts, ends = self.tp.profile
        starts_arr, ends_arr = self.tp.profile_arr

        self.assertIsInstance(starts_arr, np.ndarray)
        self.assertIsInstance(ends_arr, np.ndarray)
        for i in range(len(self.tp)):
            self.assertEqual(starts[i], starts_arr[i])
            self.assertEqual(ends[i], ends_arr[i])

    def test_get_bottleneck(self):
        self.tp.add(0, 3)
        self.tp.add(1, 4)
        bn = self.tp.get_bottleneck()
        self.assertEqual(4, bn)

        self.tp.add(6, 8)
        bn = self.tp.get_bottleneck()
        self.assertEqual(6, bn)

    def test_get_squashed_arr(self):
        self.tp.add(0, 3)
        self.tp.add(1, 4)

        starts_arr, ends_arr = self.tp.get_squashed_arr(0, 4)
        self.assertEqual(0, starts_arr[0])
        self.assertEqual(0.75, ends_arr[0])
        self.assertEqual(0.25, starts_arr[1])
        self.assertEqual(1, ends_arr[1])

        starts_arr, ends_arr = self.tp.get_squashed_arr(2, 4)
        self.assertEqual(-1, starts_arr[0])
        self.assertEqual(0.5, ends_arr[0])
        self.assertEqual(-0.5, starts_arr[1])
        self.assertEqual(1, ends_arr[1])

    def test_get_elapsed_arr(self):
        self.tp.add(0, 3)
        self.tp.add(1, 4)
        elapsed_arr = self.tp.get_elapsed_arr()
        self.assertEqual(3, elapsed_arr[0])
        self.assertEqual(3, elapsed_arr[1])


if __name__ == "__main__":
    unittest.main()
