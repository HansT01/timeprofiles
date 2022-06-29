import unittest
from unittest.mock import patch
from tabulate import tabulate

from timeprofiles import TimeProfileCollection as TPC


class TestTimeProfileCollection(unittest.TestCase):
    def setUp(self):
        TPC.clear()
        self.profiles = TPC.profiles

    def assert_one_profile(self, f):
        profiles = self.profiles
        self.assertEqual(1, len(profiles))
        for k in profiles:
            tp = profiles[k]
            self.assertEqual(k.__qualname__, f.__qualname__)
            self.assertEqual(1, len(tp))

    def assert_no_profiles(self):
        profiles = self.profiles
        self.assertEqual(0, len(profiles))

    def test_profile_method(self):
        @TPC.profile_method
        def my_func(a, b):
            return a + b

        a = my_func(1, 2)
        b = my_func(2, 3)
        c = my_func(3, 4)
        self.assertEqual(3, a)
        self.assertEqual(5, b)
        self.assertEqual(7, c)

        for k in self.profiles:
            self.assertEqual(k.__qualname__, my_func.__qualname__)

            tp = self.profiles[k]
            self.assertEqual(3, len(tp))

    def test_profile_exception(self):
        @TPC.profile_method
        def my_func():
            raise Exception()

        try:
            my_func()
        except:
            pass

        self.assert_one_profile(my_func)

    def test_profile_class_methods(self):
        @TPC.profile_class_methods
        class MyClass:
            def my_method(self):
                pass

        obj = MyClass()
        obj.my_method()
        self.assert_one_profile(MyClass.my_method)

    def test_profile_init(self):
        @TPC.profile_class_methods
        class MyClass:
            def __init__(self):
                pass

        obj = MyClass()
        self.assert_one_profile(MyClass.__init__)

    def test_profile_repr(self):
        @TPC.profile_class_methods
        class MyClass:
            def __repr__(self):
                return ""

        obj = MyClass()
        str(obj)
        self.assert_one_profile(MyClass.__repr__)

    def test_profile_str(self):
        @TPC.profile_class_methods
        class MyClass:
            def __repr__(self):
                return ""

            def __str__(self):
                return ""

        obj = MyClass()
        str(obj)
        self.assert_one_profile(MyClass.__str__)

    def test_profile_staticmethod(self):
        @TPC.profile_class_methods
        class MyClass:
            @staticmethod
            def my_static_method():
                pass

        MyClass.my_static_method()
        self.assert_one_profile(MyClass.my_static_method)

    def test_profile_subclass(self):
        @TPC.profile_class_methods
        class MyClass:
            class MySubClass:
                def my_method(self):
                    pass

        obj = MyClass.MySubClass()
        obj.my_method()
        self.assert_one_profile(MyClass.MySubClass.my_method)

    def test_profile_subsubclass(self):
        @TPC.profile_class_methods
        class MyClass:
            class MySubClass:
                class MySubSubClass:
                    def my_method(self):
                        pass

        obj = MyClass.MySubClass.MySubSubClass()
        obj.my_method()
        self.assert_one_profile(MyClass.MySubClass.MySubSubClass.my_method)

    def test_profile_object(self):
        class MyClass:
            def __init__(self):
                pass

            def my_method(self):
                pass

        obj_a = TPC.profile_class_methods(MyClass())
        obj_a.my_method()
        self.assert_one_profile(MyClass.my_method)

        obj_b = MyClass()
        obj_b.my_method()
        self.assert_one_profile(MyClass.my_method)

        TPC.clear()
        obj_c = MyClass()
        TPC.profile_class_methods(obj_c)
        obj_c.my_method()
        self.assert_one_profile(MyClass.my_method)

    def test_profile_ignore(self):
        @TPC.profile_class_methods
        class MyClass:
            @TPC.profile_ignore
            def __init__(self):
                pass

            def my_method(self):
                pass

            @TPC.profile_ignore
            def my_other_method(self):
                pass

        obj = MyClass()
        obj.my_method()
        obj.my_other_method()
        self.assert_one_profile(MyClass.my_method)

    def test_profile_ignore_subclass(self):
        @TPC.profile_class_methods
        class MyClass:
            @TPC.profile_ignore
            class MySubClass:
                def my_method(self):
                    pass

            def __init__(self):
                pass

        obj_a = MyClass.MySubClass()
        obj_a.my_method()
        self.assert_no_profiles()

        obj_b = MyClass()
        self.assert_one_profile(MyClass.__init__)

    @patch("builtins.print")
    def test_display_profiles(self, mock_print):
        def my_method():
            pass

        TPC.add(my_method, 0, 3)
        TPC.add(my_method, 2, 4)

        table = [
            [
                "my_method",
                2,
                round(2.5 * 1000, 2),
                round(3.0 * 1000, 2),
                round(4.0 * 1000, 2),
            ]
        ]

        table_str = tabulate(
            table,
            headers=[
                "Name",
                "Calls",
                "Average (ms)",
                "Longest (ms)",
                "Bottleneck (ms)",
            ],
            floatfmt=",.2f",
        )
        TPC.display_profiles()
        mock_print.assert_called_with(table_str)


if __name__ == "__main__":
    unittest.main()
