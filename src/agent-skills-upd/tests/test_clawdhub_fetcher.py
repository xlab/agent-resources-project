"""Tests for Clawdhub skill fetching."""

import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from agent_skills_upd.fetcher import fetch_clawdhub_skill


def create_clawdhub_zip(tmp_path: Path, skill_name: str) -> bytes:
    """Create a zip archive with a single root folder and SKILL.md."""
    content_root = tmp_path / "content"
    content_root.mkdir(parents=True)
    archive_root = content_root / "package"
    archive_root.mkdir()

    (archive_root / "SKILL.md").write_text(
        f"---\nname: {skill_name}\n---\n# Test Skill",
        encoding="utf-8",
    )
    (archive_root / "note.txt").write_text("note", encoding="utf-8")

    archive_path = tmp_path / "skill.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        for path in archive_root.rglob("*"):
            archive.write(path, arcname=str(path.relative_to(content_root)))

    return archive_path.read_bytes()


def mock_httpx(metadata: dict, archive_bytes: bytes) -> MagicMock:
    """Create a mocked httpx client for metadata + download."""
    metadata_response = MagicMock()
    metadata_response.status_code = 200
    metadata_response.json.return_value = metadata
    metadata_response.raise_for_status.return_value = None

    download_response = MagicMock()
    download_response.status_code = 200
    download_response.content = archive_bytes
    download_response.raise_for_status.return_value = None

    mock_client = MagicMock()
    mock_client.__enter__.return_value.get.side_effect = [
        metadata_response,
        download_response,
    ]
    return mock_client


def test_clawdhub_fetch_writes_metadata_and_version():
    """Clawdhub fetch should validate root SKILL.md and store metadata."""
    skill_name = "weather"
    metadata = {"latestVersion": {"version": "1.2.3"}}

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        dest_path = tmp_path / "skills"
        archive_bytes = create_clawdhub_zip(tmp_path, skill_name)

        with patch("httpx.Client", return_value=mock_httpx(metadata, archive_bytes)):
            result = fetch_clawdhub_skill(skill_name, dest_path, overwrite=False)

        assert result.path == dest_path / skill_name
        assert result.new_version == "1.2.3"
        assert result.was_existing is False

        metadata_path = result.path / "SKILL.json"
        stored = json.loads(metadata_path.read_text(encoding="utf-8"))
        assert stored["latestVersion"]["version"] == "1.2.3"


def test_clawdhub_fetch_reads_old_version():
    """Existing SKILL.json should be used as the old version."""
    skill_name = "weather"
    metadata = {"latestVersion": {"version": "2.0.0"}}

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        dest_path = tmp_path / "skills"
        existing = dest_path / skill_name
        existing.mkdir(parents=True)
        (existing / "SKILL.json").write_text(
            json.dumps({"latestVersion": {"version": "1.0.0"}}),
            encoding="utf-8",
        )

        archive_bytes = create_clawdhub_zip(tmp_path, skill_name)

        with patch("httpx.Client", return_value=mock_httpx(metadata, archive_bytes)):
            result = fetch_clawdhub_skill(skill_name, dest_path, overwrite=True)

        assert result.was_existing is True
        assert result.old_version == "1.0.0"
        assert result.new_version == "2.0.0"
