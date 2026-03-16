import os
import sys
import tempfile
import unittest
import shutil
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: F401
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import main
from main import download


class TestDownload(unittest.TestCase):
    def test_missing_credentials_exits(self):
        original = main.credentials_path
        main.credentials_path = '/nonexistent/credentials.json'
        try:
            with self.assertRaises(SystemExit):
                download()
        finally:
            main.credentials_path = original

    @patch('main.build')
    @patch('main.service_account.Credentials.from_service_account_file')
    def test_auth_failure_returns_gracefully(self, mock_creds, mock_build):
        mock_creds.side_effect = Exception('Invalid credentials')
        original = main.credentials_path
        tmpdir = tempfile.mkdtemp()
        cred_path = os.path.join(tmpdir, 'credentials.json')
        with open(cred_path, 'w') as f:
            f.write('{}')
        main.credentials_path = cred_path
        try:
            result = download()
            self.assertIsNone(result)
        finally:
            main.credentials_path = original
            shutil.rmtree(tmpdir, ignore_errors=True)

    @patch('main.build')
    @patch('main.service_account.Credentials.from_service_account_file')
    def test_file_list_failure_returns_gracefully(self, mock_creds, mock_build):
        mock_service = MagicMock()
        mock_service.files().list().execute.side_effect = Exception('Network error')
        mock_build.return_value = mock_service

        original = main.credentials_path
        tmpdir = tempfile.mkdtemp()
        cred_path = os.path.join(tmpdir, 'credentials.json')
        with open(cred_path, 'w') as f:
            f.write('{}')
        main.credentials_path = cred_path
        try:
            result = download()
            self.assertIsNone(result)
        finally:
            main.credentials_path = original
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
