import os
import sys
import tempfile
import unittest

# Setup mocks before importing main
sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: F401
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import get_extensions


class TestGetExtensions(unittest.TestCase):
    def test_returns_extensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, 'song.mid'), 'w').close()
            open(os.path.join(tmpdir, 'qr.png'), 'w').close()
            result = get_extensions(tmpdir)
            self.assertEqual(result, {'.mid', '.png'})

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_extensions(tmpdir)
            self.assertEqual(result, set())

    def test_mixed_extensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ['a.mid', 'b.png', 'c.pdf', 'd.jpg', 'e.musicxml']:
                open(os.path.join(tmpdir, name), 'w').close()
            result = get_extensions(tmpdir)
            self.assertEqual(result, {'.mid', '.png', '.pdf', '.jpg', '.musicxml'})

    def test_case_insensitive(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, 'song.MID'), 'w').close()
            open(os.path.join(tmpdir, 'image.PNG'), 'w').close()
            result = get_extensions(tmpdir)
            self.assertEqual(result, {'.mid', '.png'})


if __name__ == '__main__':
    unittest.main()
