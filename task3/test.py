import unittest
from config_translator import json_to_config, evaluate_expression

class TestConfigTranslator(unittest.TestCase):

    def test_simple_dictionary(self):
        input_data = {"A": 1, "B": 2}
        expected_output = "{\n  A : 1,\n  B : 2\n}"
        self.assertEqual(json_to_config(input_data), expected_output)

    def test_nested_dictionary(self):
        input_data = {"A": {"B": 2}}
        expected_output = "{\n  A : {\n    B : 2\n  }\n}"
        self.assertEqual(json_to_config(input_data), expected_output)

    def test_constant_expression(self):
        self.assertEqual(evaluate_expression("|+ 1 2 3|"), 6)
        self.assertEqual(evaluate_expression("|min 3 5 2|"), 2)

    def test_invalid_name(self):
        input_data = {"invalid_name": 1}
        with self.assertRaises(ValueError):
            json_to_config(input_data)

    def test_invalid_expression(self):
        input_data = {"A": "|invalid 1 2|"}
        with self.assertRaises(ValueError):
            json_to_config(input_data)

if __name__ == "__main__":
    unittest.main()
