import unittest

from edgesafe.doctor import baseline_results, parse_target


class DoctorTests(unittest.TestCase):
    def test_parse_target(self):
        self.assertEqual(parse_target("127.0.0.1:5000"), ("127.0.0.1", 5000))

    def test_baseline_has_python_and_disk(self):
        names = {item.name for item in baseline_results()}
        self.assertIn("python", names)
        self.assertIn("disk", names)


if __name__ == "__main__":
    unittest.main()
