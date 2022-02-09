import unittest

from conflowgen.tools import docstring_parameter


class TestDocstringParameter(unittest.TestCase):

    def test_decorate(self):
        my_test_var = "hello"

        @docstring_parameter(test_var=my_test_var)
        def function_with_var_in_docstring():
            """
            {test_var}
            """
            pass

        expected_trimmed_docstring = "hello"
        self.assertEqual(expected_trimmed_docstring, function_with_var_in_docstring.__doc__.strip())
