import json
import pytest

from framework.config_manager import ConfigManager


@pytest.fixture
def valid_config():
    return {
        "project": {
            "name": "Test Framework",
            "version": "1.0.0",
            "description": "Testing configuration manager"
        },
        "api": {
            "base_url": "http://127.0.0.1:5000",
            "timeout": 10
        },
        "directories": {
            "snapshots": "snapshots",
            "reports": "reports"
        },
        "settings": {
            "save_response_headers": True,
            "save_response_time": True,
            "compare_status_codes": True,
            "compare_response_body": True
        },
        "tests": [
            {
                "name": "Health Check",
                "endpoint": "/api/health",
                "method": "GET",
                "snapshot": "health_baseline",
                "enabled": True
            },
            {
                "name": "Products Test",
                "endpoint": "/api/products",
                "method": "GET",
                "snapshot": "products_baseline",
                "enabled": False
            }
        ]
    }


@pytest.fixture
def config_file(tmp_path, valid_config):
    config_path = tmp_path / "config.json"

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(valid_config, file)

    return config_path


def test_load_config(config_file):
    manager = ConfigManager(config_file)

    config = manager.get_config()

    assert config["project"]["name"] == "Test Framework"
    assert config["api"]["base_url"] == "http://127.0.0.1:5000"


def test_get_api_config(config_file):
    manager = ConfigManager(config_file)

    api_config = manager.get_api_config()

    assert api_config["base_url"] == "http://127.0.0.1:5000"
    assert api_config["timeout"] == 10


def test_get_project_config(config_file):
    manager = ConfigManager(config_file)

    project_config = manager.get_project_config()

    assert project_config["name"] == "Test Framework"


def test_get_directory_config(config_file):
    manager = ConfigManager(config_file)

    directory_config = manager.get_directory_config()

    assert directory_config["snapshots"] == "snapshots"
    assert directory_config["reports"] == "reports"


def test_get_settings(config_file):
    manager = ConfigManager(config_file)

    settings = manager.get_settings()

    assert settings["compare_response_body"] is True


def test_get_tests(config_file):
    manager = ConfigManager(config_file)

    tests = manager.get_tests()

    assert len(tests) == 2


def test_get_enabled_tests(config_file):
    manager = ConfigManager(config_file)

    enabled_tests = manager.get_enabled_tests()

    assert len(enabled_tests) == 1
    assert enabled_tests[0]["name"] == "Health Check"


def test_get_disabled_tests(config_file):
    manager = ConfigManager(config_file)

    disabled_tests = manager.get_disabled_tests()

    assert len(disabled_tests) == 1
    assert disabled_tests[0]["name"] == "Products Test"


def test_missing_config_file(tmp_path):
    missing_path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        ConfigManager(missing_path)


def test_invalid_json(tmp_path):
    config_path = tmp_path / "invalid.json"

    config_path.write_text(
        "{ invalid json }",
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Invalid JSON"):
        ConfigManager(config_path)


def test_missing_required_section(tmp_path, valid_config):
    del valid_config["api"]

    config_path = tmp_path / "config.json"

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(valid_config, file)

    with pytest.raises(ValueError, match="api"):
        ConfigManager(config_path)


def test_invalid_timeout(tmp_path, valid_config):
    valid_config["api"]["timeout"] = -5

    config_path = tmp_path / "config.json"

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(valid_config, file)

    with pytest.raises(ValueError, match="timeout"):
        ConfigManager(config_path)


def test_invalid_http_method(tmp_path, valid_config):
    valid_config["tests"][0]["method"] = "INVALID"

    config_path = tmp_path / "config.json"

    with open(config_path, "w", encoding="utf-8") as file:
        json.dump(valid_config, file)

    with pytest.raises(ValueError, match="HTTP method"):
        ConfigManager(config_path)