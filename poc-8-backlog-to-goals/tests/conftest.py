import pytest

@pytest.fixture(autouse=True)
def patch_load_dotenv(monkeypatch):
    """
    Automatically patch dotenv.load_dotenv for all tests to prevent
    issues with find_dotenv in the test environment.
    AppConfig should rely on environment variables set directly by fixtures
    or monkeypatch.setenv in tests.
    """
    monkeypatch.setattr("src.config.load_dotenv", lambda *args, **kwargs: None)
    # Also patch the one in src.main if it were to be used, though AppConfig is the primary user.
    # monkeypatch.setattr("src.main.load_dotenv", lambda *args, **kwargs: None) # If main also called it directly.
    # For now, AppConfig is the only direct caller of load_dotenv.
