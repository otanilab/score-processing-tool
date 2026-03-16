import os
import sys
import tempfile
import unittest
import shutil
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: F401
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import main as main_module
from main import main


class TestMainPipeline(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self._original_data_dir = main_module.data_dir
        self._original_output_dir = main_module.output_dir
        main_module.data_dir = os.path.join(self.tmpdir, 'data')
        main_module.output_dir = os.path.join(self.tmpdir, 'output')
        os.makedirs(main_module.data_dir, exist_ok=True)
        os.makedirs(main_module.output_dir, exist_ok=True)

    def tearDown(self):
        main_module.data_dir = self._original_data_dir
        main_module.output_dir = self._original_output_dir
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    @patch('main.download')
    @patch('main.make_score')
    def test_stage1_called_with_mid_and_png(self, mock_make_score, mock_download):
        song_dir = os.path.join(main_module.data_dir, 'song1')
        os.makedirs(song_dir)
        open(os.path.join(song_dir, 'song1.mid'), 'w').close()
        open(os.path.join(song_dir, 'song1.png'), 'w').close()

        main()

        mock_make_score.assert_called_once_with(song_dir)

    @patch('main.download')
    @patch('main.make_score')
    def test_stage1_skipped_with_pdf_present(self, mock_make_score, mock_download):
        song_dir = os.path.join(main_module.data_dir, 'song1')
        os.makedirs(song_dir)
        open(os.path.join(song_dir, 'song1.mid'), 'w').close()
        open(os.path.join(song_dir, 'song1.png'), 'w').close()
        open(os.path.join(song_dir, 'song1.pdf'), 'w').close()

        main()

        mock_make_score.assert_not_called()

    @patch('main.download')
    @patch('main.make_score')
    @patch('main.pdf_to_jpg')
    @patch('main.embed_qr')
    def test_stage2_called_with_pdf_and_png(self, mock_embed, mock_pdf_to_jpg, mock_make_score, mock_download):
        song_dir = os.path.join(main_module.data_dir, 'song1')
        os.makedirs(song_dir)
        open(os.path.join(song_dir, 'song1.mid'), 'w').close()
        open(os.path.join(song_dir, 'song1.png'), 'w').close()
        open(os.path.join(song_dir, 'song1.pdf'), 'w').close()
        open(os.path.join(song_dir, 'song1.musicxml'), 'w').close()

        main()

        mock_pdf_to_jpg.assert_called_once_with(song_dir)
        mock_embed.assert_called_once_with(song_dir)

    @patch('main.download')
    def test_skips_non_directory_entries(self, mock_download):
        open(os.path.join(main_module.data_dir, 'stray_file.txt'), 'w').close()
        main()

    @patch('main.download')
    @patch('main.print_score')
    def test_print_stage(self, mock_print, mock_download):
        unprint_dir = os.path.join(main_module.output_dir, 'unprint')
        os.makedirs(unprint_dir)
        test_file = os.path.join(unprint_dir, 'score.jpg')
        with open(test_file, 'w') as f:
            f.write('test')

        main()

        mock_print.assert_called_once_with(test_file)


if __name__ == '__main__':
    unittest.main()
