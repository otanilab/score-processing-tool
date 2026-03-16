import os
import sys
import tempfile
import unittest
import shutil

sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: F401
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import main
from main import print_score


class TestPrintScore(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.output_tmpdir = tempfile.mkdtemp()
        self._original_output_dir = main.output_dir
        main.output_dir = self.output_tmpdir

    def tearDown(self):
        main.output_dir = self._original_output_dir
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        shutil.rmtree(self.output_tmpdir, ignore_errors=True)

    def test_moves_file_to_printed_directory(self):
        test_file = os.path.join(self.tmpdir, 'score.jpg')
        with open(test_file, 'w') as f:
            f.write('test')

        print_score(test_file)

        printed_dir = os.path.join(self.output_tmpdir, 'printed')
        self.assertTrue(os.path.exists(os.path.join(printed_dir, 'score.jpg')))
        self.assertFalse(os.path.exists(test_file))

    def test_nonexistent_file(self):
        result = print_score('/nonexistent/path/score.jpg')
        self.assertIsNone(result)

    def test_creates_printed_directory(self):
        test_file = os.path.join(self.tmpdir, 'score.jpg')
        with open(test_file, 'w') as f:
            f.write('test')

        print_score(test_file)

        printed_dir = os.path.join(self.output_tmpdir, 'printed')
        self.assertTrue(os.path.isdir(printed_dir))


if __name__ == '__main__':
    unittest.main()
