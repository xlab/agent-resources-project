# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Overview

This is a Python monorepo containing CLI tools for updating Claude Code resources (skills, commands, and sub-agents) or Codex / OpenCode / Amp / Clawdbot Skills from GitHub and Upd.dev git repositories.

## Repository Structure

```
agent-skills-project/
├── src/
│   ├── agent-skills-upd/           # Python core library
│   │   ├── pyproject.toml         # Package config
│   │   └── agent_skills_upd/       # Source code
│   │       ├── cli/               # CLI implementations
│   │       ├── fetcher.py         # Git tarball fetching
│   │       ├── exceptions.py      # Custom exceptions
│   │       └── ...
│   └── agent-skills-upd-npm/       # npm core library (future)
├── command-packages/
│   ├── pypi/                      # PyPI wrapper packages
│   │   ├── upd-skill/             # Primary: `uvx upd-skill`
│   │   ├── upd-command/           # Primary: `uvx upd-command`
│   │   ├── upd-agent/             # Primary: `uvx upd-agent`
│   │   ├── create-agent-skill-repo/
│   │   ├── skill-upd/             # DEPRECATED (use upd-skill)
│   │   ├── command-upd/           # DEPRECATED (use upd-command)
│   │   ├── agent-upd/             # DEPRECATED (use upd-agent)
│   │   └── <placeholder packages>
│   └── npm/                       # npm wrapper packages (future)
├── AGENTS.md
└── README.md
```

**Primary usage pattern** is via uvx for one-off execution:

```bash
# Primary commands (recommended):
uvx upd-skill <username>/<skill-name>
uvx upd-command <username>/<command-name>
uvx upd-agent <username>/<agent-name>

# Deprecated (still work, but use primary instead):
uvx skill-upd <username>/<skill-name>
uvx command-upd <username>/<command-name>
uvx agent-upd <username>/<agent-name>
```

The wrapper packages in `command-packages/pypi/` exist to enable this clean uvx UX. They are thin wrappers that depend on `agent-resources`, which contains the shared core logic.

## Architecture

**Core Components** (in `src/agent-skills-upd/agent_skills_upd/`):

- `fetcher.py` - Generic resource fetcher that downloads from GitHub tarballs and extracts resources
- `cli/common.py` - Shared CLI utilities (argument parsing, destination resolution)
- `cli/skill.py`, `cli/command.py`, `cli/agent.py` - Typer CLI apps for each resource type
- `exceptions.py` - Custom exception hierarchy

**Resource Types**:

- Skills: Directories copied to `.claude/skills/<name>/`
- Commands: Single `.md` files copied to `.claude/commands/<name>.md`
- Agents: Single `.md` files copied to `.claude/agents/<name>.md`

**Fetching Pattern**: Resources are fetched from `https://github.com/<username>/agent-resources/` repositories by downloading the main branch tarball and extracting the specific resource.

## Dependencies

- `httpx` - HTTP client for downloading from GitHub
- `typer` - CLI framework
