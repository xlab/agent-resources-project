"""Shared exception classes for agent-resources."""


class SkillUpdError(Exception):
    """Base exception for skill-upd errors."""

    pass


class RepoNotFoundError(SkillUpdError):
    """Raised when the agent-resources repo doesn't exist."""

    pass


class ResourceNotFoundError(SkillUpdError):
    """Raised when the skill/command/agent doesn't exist in the repo."""

    pass


class ResourceExistsError(SkillUpdError):
    """Raised when the resource already exists locally."""

    pass
