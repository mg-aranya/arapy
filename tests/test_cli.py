import unittest
from main import parse_cli

class TestCLIParsing(unittest.TestCase):
    def test_parse_module_service_action(self):
        argv = ["main.py", "identities", "endpoint", "list", "-vvv", "--limit=5", "--out=./x.csv"]
        args = parse_cli(argv)
        self.assertEqual(args["module"], "identities")
        self.assertEqual(args["service"], "endpoint")
        self.assertEqual(args["action"], "list")
        self.assertTrue(args["verbose"])
        self.assertEqual(args["limit"], "5")
        self.assertEqual(args["out"], "./x.csv")

    def test_unknown_flag_raises(self):
        argv = ["main.py", "identities", "endpoint", "list", "-x"]
        with self.assertRaises(ValueError):
            parse_cli(argv)

if __name__ == "__main__":
    unittest.main()