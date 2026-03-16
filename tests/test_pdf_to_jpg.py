import os
import sys
import tempfile
import unittest
import shutil
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: F401
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import pdf_to_jpg


class TestPdfToJpg(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_no_pdf_file(self):
        result = pdf_to_jpg(self.tmpdir)
        self.assertIsNone(result)

    @patch('main.convert_from_path')
    def test_handles_conversion_error(self, mock_convert):
        pdf_path = os.path.join(self.tmpdir, 'score.pdf')
        with open(pdf_path, 'w') as f:
            f.write('dummy')

        mock_convert.side_effect = Exception('poppler not found')

        pdf_to_jpg(self.tmpdir)

        jpg_path = os.path.join(self.tmpdir, 'score.jpg')
        self.assertFalse(os.path.exists(jpg_path))


if __name__ == '__main__':
    unittest.main()
