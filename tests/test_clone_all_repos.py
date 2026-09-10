"""GitHub token validation in clone_all_repos.get_github_token.

Guiding story: Kaspars runs the repo cloner without a usable GITHUB_TOKEN
and gets a clean None instead of a crash — whether the env is missing,
GitHub says no, or the network flakes out.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from clone_all_repos import get_github_token


@pytest.fixture(autouse=True)
def _silence_token_logs():
    with patch("clone_all_repos.print_colored"):
        yield


def test_get_github_token_missing_env(monkeypatch):
    """Return None when GITHUB_TOKEN is not set."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    assert get_github_token() is None


@patch("clone_all_repos.requests.get")
def test_get_github_token_success(mock_get, monkeypatch):
    """Return the token when GitHub accepts it."""
    monkeypatch.setenv("GITHUB_TOKEN", "test_token")
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"login": "test_user"}
    mock_get.return_value = mock_response

    token = get_github_token()

    assert token == "test_token"
    mock_get.assert_called_once_with(
        "https://api.github.com/user",
        headers={"Authorization": "token test_token"},
        timeout=10,
    )


@patch("clone_all_repos.requests.get")
def test_get_github_token_invalid_status(mock_get, monkeypatch):
    """Return None when the API returns a non-200 status."""
    monkeypatch.setenv("GITHUB_TOKEN", "test_token")
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    assert get_github_token() is None


@patch("clone_all_repos.requests.get")
def test_get_github_token_request_exception(mock_get, monkeypatch):
    """Return None when requests.get raises RequestException."""
    monkeypatch.setenv("GITHUB_TOKEN", "test_token")
    mock_get.side_effect = requests.RequestException("Connection error")

    assert get_github_token() is None
