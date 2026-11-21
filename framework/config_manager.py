
import json
from pathlib import Path


class ConfigManager:

    def __init__(self, config_path="config.json"):
        self.config_path = Path(config_path)
        self.config = self.load_config()

    def load_config(self):
        """
        Load configuration from the JSON file.
        """

        if not self.config_path.exists:
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}"
            )

        try:
            with open(
                self.config_path,
                "r",
                encoding="utf-8"
            ) as file:
                config = json.load(file)

        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid JSON configuration: {error}"
            )

        self.validate_config(config)

        return config

    def validate_config(self, config):
        """
        Validate the configuration structure and values.
        """

        required_sections = [
            "project",
            "api",
            "directories",
            "settings",
            "tests"
        ]

        for section in required_sections:
            if section not in config:
                raise ValueError(
                    f"Missing required configuration section: {section}"
                )

        # Validate project configuration
        if not config["project"].get("name"):
            raise ValueError(
                "Project name is required."
            )

        # Validate API configuration
        api_config = config["api"]

        if not api_config.get("base_url"):
            raise ValueError(
                "API base URL is required."
            )

        if not isinstance(api_config.get("timeout"), (int, float)):
            raise ValueError(
                "API timeout must be a number."
            )

        if api_config["timeout"] <= 0:
            raise ValueError(
                "API timeout must be greater than zero."
            )

        # Validate directory configuration
        directories = config["directories"]

        if not directories.get("snapshots"):
            raise ValueError(
                "Snapshots directory is required."
            )

        if not directories.get("reports"):
            raise ValueError(
                "Reports directory is required."
            )

        # Validate tests
        if not isinstance(config["tests"], list):
            raise ValueError(
                "Tests configuration must be a list."
            )

        for index, test in enumerate(config["tests"]):

            required_test_fields = [
                "name",
                "endpoint",
                "method",
                "snapshot",
                "enabled"
            ]

            for field in required_test_fields:
                if field not in test:
                    raise ValueError(
                        f"Test {index + 1} is missing field: {field}"
                    )

            if not test["name"]:
                raise ValueError(
                    f"Test {index + 1} name cannot be empty."
                )

            if not test["endpoint"]:
                raise ValueError(
                    f"Test {index + 1} endpoint cannot be empty."
                )

            allowed_methods = [
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE"
            ]

            if test["method"].upper() not in allowed_methods:
                raise ValueError(
                    f"Invalid HTTP method in test '{test['name']}': "
                    f"{test['method']}"
                )

            if not isinstance(test["enabled"], bool):
                raise ValueError(
                    f"Test '{test['name']}' enabled value must be boolean."
                )

            # Validate optional ignored comparison paths
            ignore_paths = test.get("ignore_paths", [])

            if not isinstance(ignore_paths, list):
                raise ValueError(
                    f"Test '{test['name']}' ignore_paths must be a list."
                )

            for path in ignore_paths:

                if not isinstance(path, str) or not path.strip():
                    raise ValueError(
                        f"Test '{test['name']}' contains an invalid "
                        "ignore path."
                    )

        return True

    def get_config(self):
        """
        Return the complete configuration.
        """

        return self.config

    def get_api_config(self):
        """
        Return API configuration.
        """

        return self.config["api"]

    def get_project_config(self):
        """
        Return project metadata.
        """

        return self.config["project"]

    def get_directory_config(self):
        """
        Return directory configuration.
        """

        return self.config["directories"]

    def get_settings(self):
        """
        Return framework settings.
        """

        return self.config["settings"]

    def get_tests(self):
        """
        Return all configured tests.
        """

        return self.config["tests"]

    def get_enabled_tests(self):
        """
        Return only enabled tests.
        """

        return [
            test
            for test in self.config["tests"]
            if test["enabled"]
        ]

    def get_disabled_tests(self):
        """
        Return only disabled tests.
        """

        return [
            test
            for test in self.config["tests"]
            if not test["enabled"]
        ]
