import json
import pytest

from framework.snapshot_manager import SnapshotManager


def test_save_snapshot(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    data = {
        "status_code": 200,
        "response_body": {
            "message": "success"
        }
    }

    snapshot_path = manager.save_snapshot(
        "test_snapshot",
        data
    )

    assert snapshot_path.exists()

    with open(
        snapshot_path,
        "r",
        encoding="utf-8"
    ) as file:

        saved_data = json.load(file)

    assert saved_data == data


def test_load_snapshot(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    data = {
        "status_code": 200,
        "response_body": {
            "message": "success"
        }
    }

    manager.save_snapshot(
        "test_snapshot",
        data
    )

    loaded_data = manager.load_snapshot(
        "test_snapshot"
    )

    assert loaded_data == data


def test_snapshot_exists(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    manager.save_snapshot(
        "test_snapshot",
        {"data": "value"}
    )

    assert manager.snapshot_exists(
        "test_snapshot"
    ) is True


def test_delete_snapshot(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    manager.save_snapshot(
        "test_snapshot",
        {"data": "value"}
    )

    result = manager.delete_snapshot(
        "test_snapshot"
    )

    assert result is True

    assert manager.snapshot_exists(
        "test_snapshot"
    ) is False


def test_load_missing_snapshot(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    with pytest.raises(FileNotFoundError):

        manager.load_snapshot(
            "missing_snapshot"
        )


# --------------------------------------------------
# METADATA TESTS
# --------------------------------------------------


def test_snapshot_metadata_is_created(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    manager.save_snapshot(
        "test_snapshot",
        {"data": "value"}
    )

    metadata = manager.load_metadata(
        "test_snapshot"
    )

    assert metadata is not None

    assert metadata["snapshot_name"] == "test_snapshot"

    assert metadata["version"] == 1

    assert "created_at" in metadata

    assert metadata["framework"] == (
        "REST API Regression Testing Framework"
    )


def test_custom_metadata_is_saved(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    custom_metadata = {
        "endpoint": "/api/products/1",
        "method": "GET"
    }

    manager.save_snapshot(
        "test_snapshot",
        {"data": "value"},
        metadata=custom_metadata
    )

    metadata = manager.load_metadata(
        "test_snapshot"
    )

    assert metadata["endpoint"] == "/api/products/1"

    assert metadata["method"] == "GET"


def test_snapshot_version_increments(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    manager.save_snapshot(
        "test_snapshot",
        {"version": "first"}
    )

    first_metadata = manager.load_metadata(
        "test_snapshot"
    )

    assert first_metadata["version"] == 1


    manager.save_snapshot(
        "test_snapshot",
        {"version": "second"}
    )

    second_metadata = manager.load_metadata(
        "test_snapshot"
    )

    assert second_metadata["version"] == 2


def test_snapshot_overwrite_protection(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    original_data = {
        "data": "original"
    }

    manager.save_snapshot(
        "test_snapshot",
        original_data
    )


    with pytest.raises(FileExistsError):

        manager.save_snapshot(
            "test_snapshot",
            {"data": "updated"},
            overwrite=False
        )


    loaded_data = manager.load_snapshot(
        "test_snapshot"
    )

    assert loaded_data == original_data


# --------------------------------------------------
# SNAPSHOT LISTING TESTS
# --------------------------------------------------


def test_list_snapshots(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    manager.save_snapshot(
        "snapshot_one",
        {"data": 1}
    )

    manager.save_snapshot(
        "snapshot_two",
        {"data": 2}
    )


    snapshots = manager.list_snapshots()


    snapshot_names = [
        snapshot["name"]
        for snapshot in snapshots
    ]


    assert "snapshot_one" in snapshot_names

    assert "snapshot_two" in snapshot_names

    assert len(snapshots) == 2


def test_list_snapshots_includes_metadata(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    manager.save_snapshot(
        "test_snapshot",
        {"data": "value"},
        metadata={
            "endpoint": "/api/health"
        }
    )


    snapshots = manager.list_snapshots()


    assert len(snapshots) == 1

    snapshot = snapshots[0]

    assert snapshot["name"] == "test_snapshot"

    assert snapshot["metadata"]["endpoint"] == (
        "/api/health"
    )


# --------------------------------------------------
# VALIDATION TESTS
# --------------------------------------------------


def test_invalid_snapshot_name_is_rejected(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    invalid_names = [
        "",
        "../outside",
        "folder/snapshot",
        "folder\\snapshot",
        "snapshot name",
        "snapshot:name"
    ]


    for name in invalid_names:

        with pytest.raises(ValueError):

            manager.save_snapshot(
                name,
                {"data": "value"}
            )


def test_snapshot_name_must_be_string(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    with pytest.raises(ValueError):

        manager.save_snapshot(
            123,
            {"data": "value"}
        )


# --------------------------------------------------
# CORRUPTED FILE TESTS
# --------------------------------------------------


def test_corrupted_snapshot_raises_error(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    snapshot_path = tmp_path / "corrupted.json"


    with open(
        snapshot_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "{invalid json"
        )


    with pytest.raises(ValueError):

        manager.load_snapshot(
            "corrupted"
        )


def test_missing_metadata_returns_none(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    manager.save_snapshot(
        "test_snapshot",
        {"data": "value"}
    )


    metadata_path = (
        tmp_path / "test_snapshot.meta.json"
    )

    metadata_path.unlink()


    metadata = manager.load_metadata(
        "test_snapshot"
    )


    assert metadata is None


# --------------------------------------------------
# DELETION TESTS
# --------------------------------------------------


def test_delete_snapshot_also_deletes_metadata(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    manager.save_snapshot(
        "test_snapshot",
        {"data": "value"}
    )


    snapshot_path = (
        tmp_path / "test_snapshot.json"
    )

    metadata_path = (
        tmp_path / "test_snapshot.meta.json"
    )


    assert snapshot_path.exists()

    assert metadata_path.exists()


    manager.delete_snapshot(
        "test_snapshot"
    )


    assert snapshot_path.exists() is False

    assert metadata_path.exists() is False


def test_delete_missing_snapshot_returns_false(tmp_path):

    manager = SnapshotManager(
        snapshot_dir=tmp_path
    )

    result = manager.delete_snapshot(
        "missing_snapshot"
    )

    assert result is False