"""Tests for config module."""

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from storymachine.config import Settings


class TestSettings:
    """Tests for Settings class."""

    def test_settings_with_valid_api_key(self, monkeypatch) -> None:
        """Test Settings creation with valid API key from environment."""
        test_key = "sk-test-key-123"
        monkeypatch.setenv("OPENAI_API_KEY", test_key)

        settings = Settings()  # pyright: ignore[reportCallIssue]

        assert settings.openai_api_key == test_key

    def test_settings_missing_both_api_keys_raises_validation_error(
        self, monkeypatch, tmp_path: Path
    ) -> None:
        """Test that missing both API keys raises ValidationError."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("ZHIPUAI_API_KEY", raising=False)

        # Change to temp directory to avoid loading project .env file
        original_cwd = os.getcwd()
        try:
            # This should work because API keys are optional now
            settings = Settings()  # pyright: ignore[reportCallIssue]
            assert settings.openai_api_key is None
            assert settings.zhipuai_api_key is None
        finally:
            os.chdir(original_cwd)

    def test_settings_from_env_file(self, tmp_path: Path) -> None:
        """Test Settings loading from .env file."""
        env_file = tmp_path / ".env"
        test_key = "sk-env-file-key-456"
        env_file.write_text(f"OPENAI_API_KEY={test_key}")

        # Change to temp directory so .env is found
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            settings = Settings(_env_file=str(env_file))  # pyright: ignore[reportCallIssue]
            assert settings.openai_api_key == test_key
        finally:
            os.chdir(original_cwd)

    def test_settings_env_var_overrides_env_file(
        self, monkeypatch, tmp_path: Path
    ) -> None:
        """Test that environment variable takes precedence over .env file."""
        env_var_key = "sk-env-var-key-789"
        env_file_key = "sk-env-file-key-123"

        # Set up .env file
        env_file = tmp_path / ".env"
        env_file.write_text(f"OPENAI_API_KEY={env_file_key}")

        # Set environment variable
        monkeypatch.setenv("OPENAI_API_KEY", env_var_key)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            settings = Settings(_env_file=str(env_file))  # pyright: ignore[reportCallIssue]
            assert settings.openai_api_key == env_var_key
        finally:
            os.chdir(original_cwd)

    def test_settings_field_is_frozen(self, monkeypatch) -> None:
        """Test that openai_api_key field is frozen (immutable)."""
        test_key = "sk-test-key-frozen"
        monkeypatch.setenv("OPENAI_API_KEY", test_key)

        settings = Settings()  # pyright: ignore[reportCallIssue]

        with pytest.raises(ValidationError) as exc_info:
            settings.openai_api_key = "sk-new-key"  # type: ignore[misc]

        assert "frozen" in str(exc_info.value).lower()

    def test_settings_field_alias(self, monkeypatch, tmp_path: Path) -> None:
        """Test that the field alias works correctly."""
        test_key = "sk-alias-test-key"
        monkeypatch.setenv("OPENAI_API_KEY", test_key)

        settings = Settings()  # pyright: ignore[reportCallIssue]

        # Verify the field is accessible by its actual name
        assert settings.openai_api_key == test_key

        # Verify the field uses the OPENAI_API_KEY environment variable
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Change to temp directory to avoid loading project .env file
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # This should work because API keys are optional now
            settings = Settings()  # pyright: ignore[reportCallIssue]
            assert settings.openai_api_key is None
        finally:
            os.chdir(original_cwd)

    def test_settings_empty_api_key_creates_settings(self, monkeypatch) -> None:
        """Test that empty API key creates settings (Pydantic allows empty strings)."""
        monkeypatch.setenv("OPENAI_API_KEY", "")

        settings = Settings()  # pyright: ignore[reportCallIssue]

        assert settings.openai_api_key == ""

    def test_settings_whitespace_only_api_key_creates_settings(
        self, monkeypatch
    ) -> None:
        """Test that whitespace-only API key creates settings (Pydantic allows whitespace)."""
        monkeypatch.setenv("OPENAI_API_KEY", "   ")

        settings = Settings()  # pyright: ignore[reportCallIssue]
        assert settings.openai_api_key == "   "

    def test_settings_default_model(self, monkeypatch, tmp_path: Path) -> None:
        """Test that model defaults when not provided."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.delenv("MODEL", raising=False)

        # Change to temp directory to avoid loading project .env file
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            settings = Settings()  # pyright: ignore[reportCallIssue]

            assert settings.model == "glm-4-flash"
        finally:
            os.chdir(original_cwd)

    def test_settings_model_env_var(self, monkeypatch) -> None:
        """Test that model can be set via environment variable."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        monkeypatch.setenv("MODEL", "gpt-test")

        settings = Settings()  # pyright: ignore[reportCallIssue]

        assert settings.model == "gpt-test"
