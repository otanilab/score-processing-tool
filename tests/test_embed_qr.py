import os
import sys
import tempfile
import unittest
import shutil

sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: F401
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from PIL import Image

import main
from main import embed_qr


class TestEmbedQr(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.output_tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)
        shutil.rmtree(self.output_tmpdir, ignore_errors=True)

    def test_embed_qr_no_jpg(self):
        # Only a PNG, no JPG
        open(os.path.join(self.tmpdir, 'test.png'), 'w').close()
        result = embed_qr(self.tmpdir)
        self.assertIsNone(result)

    def test_embed_qr_no_png(self):
        # Only a JPG, no PNG
        open(os.path.join(self.tmpdir, 'test.jpg'), 'w').close()
        result = embed_qr(self.tmpdir)
        self.assertIsNone(result)

    def test_embed_qr_empty_dir(self):
        result = embed_qr(self.tmpdir)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
