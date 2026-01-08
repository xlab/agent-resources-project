"""Generic resource fetcher for skills, commands, and agents."""

import io
import json
import shutil
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import frontmatter
import httpx

from agent_skills_upd.exceptions import (
    SkillUpdError,
    RepoNotFoundError,
    ResourceExistsError,
    ResourceNotFoundError,
)


class ResourceType(Enum):
    """Type of resource to fetch."""

    SKILL = "skill"
    COMMAND = "command"
    AGENT = "agent"


@dataclass
class ResourceConfig:
    """Configuration for a resource type."""

    resource_type: ResourceType
    source_subdir: str  # e.g., ".claude/skills", ".claude/commands"
    dest_subdir: str  # e.g., "skills", "commands"
    is_directory: bool  # True for skills, False for commands/agents
    file_extension: str | None  # None for skills, ".md" for commands/agents


RESOURCE_CONFIGS: dict[ResourceType, ResourceConfig] = {
    ResourceType.SKILL: ResourceConfig(
        resource_type=ResourceType.SKILL,
        source_subdir=".claude/skills",
        dest_subdir="skills",
        is_directory=True,
        file_extension=None,
    ),
    ResourceType.COMMAND: ResourceConfig(
        resource_type=ResourceType.COMMAND,
        source_subdir=".claude/commands",
        dest_subdir="commands",
        is_directory=False,
        file_extension=".md",
    ),
    ResourceType.AGENT: ResourceConfig(
        resource_type=ResourceType.AGENT,
        source_subdir=".claude/agents",
        dest_subdir="agents",
        is_directory=False,
        file_extension=".md",
    ),
}

# Pattern-based search for different repository structures
RESOURCE_SEARCH_PATTERNS = {
    ResourceType.SKILL: [
        ".claude/skills/{name}/",  # Current (first for backward compat)
        "{name}/",  # Repo root skill directory
        "skills/{name}/",  # Anthropics pattern
        "skill/{name}/",  # opencode pattern
        "skills/.curated/{name}/",  # OpenAI pattern
        "skills/.experimental/{name}/",  # OpenAI pattern
    ],
    ResourceType.COMMAND: [
        ".claude/commands/{name}.md",  # Current
        "commands/{name}.md",
        "command/{name}.md",  # opencode pattern
    ],
    ResourceType.AGENT: [
        ".claude/agents/{name}.md",  # Current
        "agents/{name}.md",
        "agent/{name}.md",  # opencode pattern
    ],
}

# Name of the repository to fetch resources from
REPO_NAME = "agent-resources"

CLAWDHUB_HOST = "clawdhub.com"
CLAWDHUB_DOWNLOAD_URL = "https://auth.clawdhub.com/api/download"
CLAWDHUB_METADATA_URL = "https://auth.clawdhub.com/api/skill"
CLAWDHUB_METADATA_FILENAME = "SKILL.json"


@dataclass
class ClawdhubFetchResult:
    """Result from a Clawdhub skill fetch."""

    path: Path
    old_version: str | None
    new_version: str
    was_existing: bool


def find_root_skill_file(repo_dir: Path) -> Path | None:
    """Find a root-level SKILL.md file case-insensitively."""
    for path in sorted(repo_dir.iterdir(), key=lambda entry: entry.name.lower()):
        if path.is_file() and path.name.lower() == "skill.md":
            return path
    return None


def parse_frontmatter_name(skill_file: Path) -> tuple[str | None, str | None]:
    """Parse the skill name from frontmatter."""
    content = skill_file.read_text(encoding="utf-8")
    try:
        post = frontmatter.loads(content)
    except Exception:
        return None, "Root SKILL.md frontmatter is invalid."

    name = post.metadata.get("name") if post.metadata else None
    name_value = str(name).strip() if name is not None else ""
    if not name_value:
        return None, "Root SKILL.md frontmatter missing name."

    return name_value, None


def parse_clawdhub_version(metadata: dict) -> str | None:
    """Extract the latest version string from Clawdhub metadata."""
    latest = metadata.get("latestVersion")
    if isinstance(latest, dict):
        version = latest.get("version")
        if isinstance(version, str) and version.strip():
            return version.strip()
    return None


def read_clawdhub_version(skill_dir: Path) -> str | None:
    """Read the stored Clawdhub version from SKILL.json, if present."""
    metadata_path = skill_dir / CLAWDHUB_METADATA_FILENAME
    if not metadata_path.exists():
        return None
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return parse_clawdhub_version(metadata) if isinstance(metadata, dict) else None


def write_clawdhub_metadata(skill_dir: Path, metadata: dict) -> None:
    """Persist Clawdhub metadata alongside SKILL.md."""
    metadata_path = skill_dir / CLAWDHUB_METADATA_FILENAME
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def select_archive_root(extract_path: Path) -> Path:
    """Resolve the real archive root for validation and copying."""
    entries = [entry for entry in extract_path.iterdir()]
    if len(entries) == 1 and entries[0].is_dir():
        return entries[0]
    return extract_path


def extract_archive(archive_bytes: bytes, extract_path: Path) -> None:
    """Extract zip or tar archives into extract_path."""
    archive_buffer = io.BytesIO(archive_bytes)
    if zipfile.is_zipfile(archive_buffer):
        archive_buffer.seek(0)
        with zipfile.ZipFile(archive_buffer) as archive:
            archive.extractall(extract_path)
        return

    archive_buffer.seek(0)
    try:
        with tarfile.open(fileobj=archive_buffer, mode="r:*") as tar:
            try:
                tar.extractall(extract_path, filter="data")
            except TypeError:
                tar.extractall(extract_path)
    except tarfile.TarError as exc:
        raise SkillUpdError("Unable to extract Clawdhub archive.") from exc


def validate_repository_structure(repo_dir: Path) -> dict:
    """Simple validation that provides useful feedback."""
    patterns_found = []
    for pattern in [
        ".claude/skills",
        "skills",
        "skill",
        ".claude/commands",
        "commands",
        "command",
        ".claude/agents",
        "agents",
        "agent",
    ]:
        if (repo_dir / pattern).exists():
            patterns_found.append(pattern)

    suggestions = []
    if not patterns_found:
        suggestions.append("Repository doesn't match common agent-resources patterns.")
        suggestions.append("Expected: .claude/skills/, skills/, or skill/ directories.")

    return {"patterns_found": patterns_found, "suggestions": suggestions}


def find_resource_in_repo(
    repo_dir: Path, resource_type: ResourceType, name: str
) -> Path | None:
    """Simple pattern-based search - no caching, no complexity."""
    config = RESOURCE_CONFIGS[resource_type]

    for pattern in RESOURCE_SEARCH_PATTERNS[resource_type]:
        search_path = pattern.format(name=name)
        if config.file_extension and not search_path.endswith(config.file_extension):
            search_path += config.file_extension

        resource_path = repo_dir / search_path
        if resource_path.exists():
            return resource_path

    return None


def fetch_resource(
    username: str,
    name: str | None,
    dest: Path,
    resource_type: ResourceType,
    overwrite: bool = True,
    host: str = "github.com",
    repo: str = REPO_NAME,
) -> Path:
    """
    Fetch a resource from a user's agent-resources repo and copy it to dest.

    Args:
        username: GitHub (or alternative Git host) username
        name: Name of the resource to fetch (optional for root-level skills)
        dest: Destination directory (e.g., .claude/skills/, .claude/commands/)
        resource_type: Type of resource (SKILL, COMMAND, or AGENT)
        overwrite: Whether to overwrite existing resource
        host: Repository host (default: github.com)

    Returns:
        Path to the installed resource

    Raises:
        RepoNotFoundError: If the agent-resources repo doesn't exist
        ResourceNotFoundError: If the resource doesn't exist in the repo
        ResourceExistsError: If resource exists locally and overwrite=False
    """
    config = RESOURCE_CONFIGS[resource_type]

    resource_dest = None
    if name is not None:
        # Determine destination path
        if config.is_directory:
            resource_dest = dest / name
        else:
            resource_dest = dest / f"{name}{config.file_extension}"

        # Check if resource already exists locally
        if resource_dest.exists() and not overwrite:
            raise ResourceExistsError(
                f"{resource_type.value.capitalize()} '{name}' already exists at {resource_dest}\n"
                f"Use --overwrite to replace it."
            )

    # Download tarball
    tarball_url = f"https://{host}/{username}/{repo}/archive/refs/heads/main.tar.gz"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        tarball_path = tmp_path / "repo.tar.gz"

        # Download
        try:
            with httpx.Client(follow_redirects=True, timeout=30.0) as client:
                response = client.get(tarball_url)
                if response.status_code == 404:
                    raise RepoNotFoundError(
                        f"Repository '{username}/{repo}' not found on {host}."
                    )
                response.raise_for_status()

                tarball_path.write_bytes(response.content)
        except httpx.HTTPStatusError as e:
            raise SkillUpdError(f"Failed to download repository: {e}")
        except httpx.RequestError as e:
            raise SkillUpdError(f"Network error: {e}")

        # Extract
        extract_path = tmp_path / "extracted"
        with tarfile.open(tarball_path, "r:gz") as tar:
            try:
                tar.extractall(extract_path, filter="data")
            except TypeError:
                tar.extractall(extract_path)

        # Find the resource in extracted content using pattern-based search
        # Tarball extracts to: <repo>-main/<patterns>
        repo_dir = extract_path / f"{repo}-main"

        resource_source = (
            find_resource_in_repo(repo_dir, resource_type, name) if name else None
        )
        root_skill_message = None
        root_skill_name = None
        if (
            resource_source is None
            and resource_type == ResourceType.SKILL
            and repo != REPO_NAME
        ):
            root_skill_file = find_root_skill_file(repo_dir)
            if root_skill_file is None:
                root_skill_message = (
                    "Root SKILL.md not found (case-insensitive) in repo root."
                )
            else:
                root_skill_name, root_skill_error = parse_frontmatter_name(
                    root_skill_file
                )
                if root_skill_error:
                    root_skill_message = root_skill_error
                else:
                    if name is None:
                        name = root_skill_name
                        resource_source = root_skill_file.parent
                    elif root_skill_name != name:
                        root_skill_message = (
                            "Root SKILL.md frontmatter name "
                            f"'{root_skill_name}' does not match requested '{name}'."
                        )
                    else:
                        resource_source = root_skill_file.parent

        if resource_source is None or not resource_source.exists():
            display_name = name or "<unspecified>"
            patterns_name = name or "<skill-name>"
            patterns_tried = [
                p.format(name=patterns_name)
                for p in RESOURCE_SEARCH_PATTERNS[resource_type]
            ]
            patterns_list = "\n".join([f"- {pattern}" for pattern in patterns_tried])

            validation = validate_repository_structure(repo_dir)

            error_msg = (
                f"{resource_type.value.capitalize()} '{display_name}' not found in {username}/{repo}.\n"
                f"Tried these locations:\n{patterns_list}\n"
            )

            if validation["suggestions"]:
                error_msg += "\nRepository structure issues:\n"
                error_msg += "\n".join([f"- {msg}" for msg in validation["suggestions"]])
                error_msg += "\n"
            elif validation["patterns_found"]:
                error_msg += (
                    f"\nFound directories: {', '.join(validation['patterns_found'])}\n"
                )

            if root_skill_message:
                error_msg += "\nManual repo override check:\n"
                error_msg += f"- {root_skill_message}\n"

            error_msg += (
                "\nQuick fixes:\n"
                "- Double-check the resource name\n"
                "- Try --repo REPO_NAME if using a different repository\n"
                "- Try --dest PATH for custom installation location\n"
                f"- Visit https://{host}/{username}/{repo} to verify the resource exists"
            )

            raise ResourceNotFoundError(error_msg)

        if resource_dest is None:
            if name is None:
                raise SkillUpdError("Skill name could not be determined.")
            if config.is_directory:
                resource_dest = dest / name
            else:
                resource_dest = dest / f"{name}{config.file_extension}"

            if resource_dest.exists() and not overwrite:
                raise ResourceExistsError(
                    f"{resource_type.value.capitalize()} '{name}' already exists at {resource_dest}\n"
                    f"Use --overwrite to replace it."
                )

        # Remove existing if overwriting
        if resource_dest.exists():
            if config.is_directory:
                shutil.rmtree(resource_dest)
            else:
                resource_dest.unlink()

        # Ensure destination parent exists
        dest.mkdir(parents=True, exist_ok=True)

        # Copy resource to destination
        if config.is_directory:
            shutil.copytree(str(resource_source), str(resource_dest))
        else:
            shutil.copy2(str(resource_source), str(resource_dest))

    return resource_dest


def fetch_clawdhub_skill(
    name: str,
    dest: Path,
    overwrite: bool = True,
) -> ClawdhubFetchResult:
    """
    Fetch a skill from Clawdhub via the API and copy it to dest.

    Args:
        name: Clawdhub skill slug (no username)
        dest: Destination directory (e.g., .claude/skills/)
        overwrite: Whether to overwrite existing resource

    Returns:
        ClawdhubFetchResult with install path and version info.
    """
    resource_dest = dest / name
    was_existing = resource_dest.exists()
    old_version = read_clawdhub_version(resource_dest) if was_existing else None

    if was_existing and not overwrite:
        raise ResourceExistsError(
            f"Skill '{name}' already exists at {resource_dest}\n"
            f"Use --overwrite to replace it."
        )

    try:
        with httpx.Client(follow_redirects=True, timeout=30.0) as client:
            metadata_response = client.get(CLAWDHUB_METADATA_URL, params={"slug": name})
            if metadata_response.status_code == 404:
                raise ResourceNotFoundError(
                    f"Skill '{name}' not found on {CLAWDHUB_HOST}."
                )
            metadata_response.raise_for_status()
            try:
                metadata = metadata_response.json()
            except ValueError as exc:
                raise SkillUpdError("Clawdhub metadata response was not valid JSON.") from exc

            new_version = parse_clawdhub_version(metadata)
            if not new_version:
                raise SkillUpdError(
                    "Clawdhub metadata missing latestVersion.version."
                )

            download_response = client.get(
                CLAWDHUB_DOWNLOAD_URL, params={"slug": name, "tag": "latest"}
            )
            if download_response.status_code == 404:
                raise ResourceNotFoundError(
                    f"Skill '{name}' not found on {CLAWDHUB_HOST}."
                )
            download_response.raise_for_status()
            archive_bytes = download_response.content
    except httpx.HTTPStatusError as exc:
        raise SkillUpdError(f"Failed to download Clawdhub skill: {exc}") from exc
    except httpx.RequestError as exc:
        raise SkillUpdError(f"Network error: {exc}") from exc

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        extract_path = tmp_path / "extracted"
        extract_path.mkdir(parents=True, exist_ok=True)
        extract_archive(archive_bytes, extract_path)

        archive_root = select_archive_root(extract_path)
        root_skill_file = find_root_skill_file(archive_root)
        if root_skill_file is None:
            raise SkillUpdError("Root SKILL.md not found in Clawdhub archive.")

        root_skill_name, root_skill_error = parse_frontmatter_name(root_skill_file)
        if root_skill_error:
            raise SkillUpdError(root_skill_error)
        if root_skill_name != name:
            raise SkillUpdError(
                "Root SKILL.md frontmatter name "
                f"'{root_skill_name}' does not match requested '{name}'."
            )

        if resource_dest.exists():
            if resource_dest.is_dir():
                shutil.rmtree(resource_dest)
            else:
                resource_dest.unlink()

        dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree(str(archive_root), str(resource_dest))
        write_clawdhub_metadata(resource_dest, metadata)

    return ClawdhubFetchResult(
        path=resource_dest,
        old_version=old_version,
        new_version=new_version,
        was_existing=was_existing,
    )
