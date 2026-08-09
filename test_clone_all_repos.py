import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Mock requests before importing clone_all_repos
mock_requests = MagicMock()
sys.modules['requests'] = mock_requests

import clone_all_repos
from clone_all_repos import get_github_token

class TestGetGithubToken(unittest.TestCase):
    def setUp(self):
        # Reset mock before each test
        mock_requests.get.reset_mock()
        mock_requests.get.side_effect = None
        mock_requests.get.return_value = MagicMock()
        mock_requests.RequestException = Exception # Fallback

    @patch.dict(os.environ, {}, clear=True)
    def test_get_github_token_missing_env(self):
        """Test returns None when GITHUB_TOKEN is not set."""
        self.assertIsNone(get_github_token())

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_get_github_token_success(self):
        """Test returns token when validation is successful."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "test_user"}
        mock_requests.get.return_value = mock_response

        token = get_github_token()
        self.assertEqual(token, "test_token")
        mock_requests.get.assert_called_once_with('https://api.github.com/user', headers={'Authorization': 'token test_token'}, timeout=10)

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_get_github_token_invalid_status(self):
        """Test returns None when API returns non-200 status."""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_requests.get.return_value = mock_response

        self.assertIsNone(get_github_token())

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    def test_get_github_token_request_exception(self):
        """Test returns None when requests.get raises RequestException."""
        class MockRequestException(Exception):
            pass

        mock_requests.RequestException = MockRequestException
        mock_requests.get.side_effect = MockRequestException("Connection error")

        self.assertIsNone(get_github_token())

if __name__ == "__main__":
    unittest.main()
