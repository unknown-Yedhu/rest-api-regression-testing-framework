import json
import re
from datetime import datetime, timezone
from pathlib import Path


class SnapshotManager:
    """
    Manage API regression snapshots.

    Features:
    - Save and load JSON snapshots
    - Snapshot metadata
    - Snapshot version tracking
    - Snapshot listing
    - Safe snapshot name validation
    - Atomic file writing
    - Corrupted snapshot handling
    - Optional overwrite protection
    """

    FRAMEWORK_NAME = "REST API Regression Testing Framework"

    def __init__(self, snapshot_dir="snapshots"):

        self.snapshot_dir = Path(snapshot_dir)

        self.snapshot_dir.mkdir(
            parents=True,
            exist_ok=True
        )


    def _validate_name(self, name):

        if not isinstance(name, str):

            raise ValueError(
                "Snapshot name must be a string."
            )


        name = name.strip()


        if not name:

            raise ValueError(
                "Snapshot name cannot be empty."
            )


        if not re.fullmatch(
            r"[a-zA-Z0-9_.-]+",
            name
        ):

            raise ValueError(
                "Snapshot name contains invalid characters. "
                "Use letters, numbers, underscores, hyphens, "
                "and periods only."
            )


        if name in {".", ".."}:

            raise ValueError(
                "Invalid snapshot name."
            )


        return name


    def _get_snapshot_path(self, name):

        name = self._validate_name(name)

        return self.snapshot_dir / f"{name}.json"


    def _get_metadata_path(self, name):

        name = self._validate_name(name)

        return self.snapshot_dir / f"{name}.meta.json"


    def _get_timestamp(self):

        return datetime.now(
            timezone.utc
        ).isoformat()


    def _atomic_write_json(self, file_path, data):

        temporary_path = file_path.with_suffix(
            file_path.suffix + ".tmp"
        )


        try:

            with open(
                temporary_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=4,
                    sort_keys=True
                )


            temporary_path.replace(file_path)


        finally:

            if temporary_path.exists():

                temporary_path.unlink()


    def save_snapshot(
        self,
        name,
        data,
        metadata=None,
        overwrite=True
    ):
        """
        Save API response data as a JSON snapshot.

        Args:
            name:
                Snapshot name.

            data:
                Snapshot data.

            metadata:
                Optional additional metadata.

            overwrite:
                Whether an existing snapshot can be overwritten.

        Returns:
            Path to the saved snapshot.
        """

        name = self._validate_name(name)

        snapshot_path = self._get_snapshot_path(name)

        metadata_path = self._get_metadata_path(name)


        if snapshot_path.exists() and not overwrite:

            raise FileExistsError(
                f"Snapshot '{name}' already exists."
            )


        # Determine the next snapshot version

        version = 1


        if metadata_path.exists():

            try:

                existing_metadata = self.load_metadata(name)

                version = (
                    existing_metadata.get("version", 0) + 1
                )

            except (ValueError, json.JSONDecodeError):

                version = 1


        # Save snapshot data without changing
        # the existing RegressionEngine format

        self._atomic_write_json(
            snapshot_path,
            data
        )


        # Create metadata

        snapshot_metadata = {
            "snapshot_name": name,
            "created_at": self._get_timestamp(),
            "version": version,
            "framework": self.FRAMEWORK_NAME
        }


        if metadata:

            snapshot_metadata.update(metadata)


        self._atomic_write_json(
            metadata_path,
            snapshot_metadata
        )


        return snapshot_path


    def load_snapshot(self, name):
        """
        Load an existing JSON snapshot.
        """

        snapshot_path = self._get_snapshot_path(name)


        if not snapshot_path.exists():

            raise FileNotFoundError(
                f"Snapshot '{name}' does not exist."
            )


        try:

            with open(
                snapshot_path,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)


        except json.JSONDecodeError as error:

            raise ValueError(
                f"Snapshot '{name}' contains invalid JSON."
            ) from error


    def load_metadata(self, name):
        """
        Load metadata associated with a snapshot.
        """

        metadata_path = self._get_metadata_path(name)


        if not metadata_path.exists():

            return None


        try:

            with open(
                metadata_path,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)


        except json.JSONDecodeError as error:

            raise ValueError(
                f"Metadata for snapshot '{name}' "
                "contains invalid JSON."
            ) from error


    def snapshot_exists(self, name):
        """
        Check whether a snapshot exists.
        """

        snapshot_path = self._get_snapshot_path(name)

        return snapshot_path.exists()


    def delete_snapshot(self, name):
        """
        Delete a snapshot and its metadata.
        """

        snapshot_path = self._get_snapshot_path(name)

        metadata_path = self._get_metadata_path(name)


        deleted = False


        if snapshot_path.exists():

            snapshot_path.unlink()

            deleted = True


        if metadata_path.exists():

            metadata_path.unlink()

            deleted = True


        return deleted


    def list_snapshots(self):
        """
        Return information about all available snapshots.
        """

        snapshots = []


        for snapshot_path in sorted(
            self.snapshot_dir.glob("*.json")
        ):

            # Exclude metadata files

            if snapshot_path.name.endswith(
                ".meta.json"
            ):

                continue


            snapshot_name = snapshot_path.stem


            try:

                metadata = self.load_metadata(
                    snapshot_name
                )


            except ValueError:

                metadata = {
                    "metadata_error": "Invalid metadata JSON."
                }


            snapshots.append({

                "name": snapshot_name,

                "path": str(snapshot_path),

                "metadata": metadata

            })


        return snapshots