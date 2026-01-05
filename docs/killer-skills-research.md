# Top 5 Killer Skills for Viral Growth

## Research Methodology

To find skills that go viral, I analyzed:
- **Frequency**: How often developers do this task
- **Pain level**: How much they hate doing it
- **Visibility**: Who sees the output
- **Shareability**: Built-in viral mechanism
- **"Holy Shit" factor**: Does it create an instant WOW moment

---

## The Viral Output Matrix

Skills with **public-facing output** have the highest viral potential:

| Output Type | Visibility | Viral Potential |
|-------------|------------|-----------------|
| README.md | Public (world) | 🔥🔥🔥🔥🔥 |
| Release Notes | Public (users) | 🔥🔥🔥🔥 |
| PR Description | Team (reviewers) | 🔥🔥🔥🔥 |
| Changelog | Public (repo) | 🔥🔥🔥 |
| Commit Messages | Team | 🔥🔥🔥 |
| Code Review | Author only | 🔥🔥 |

**Key insight**: Output that others SEE creates organic spread. When a reviewer sees a great PR description, they ask "how did you do that?"

---

# The Top 5 Killer Skills

## 1. `pr` — PR Description Generator

### The Pain
- Every PR needs a description
- Writing them is tedious
- Most developers write lazy descriptions
- Reviewers suffer from bad context

### The Solution
A skill that analyzes the diff + codebase context and generates a comprehensive PR description.

### What Makes It Viral
```
┌────────────────────────────────────────────────────────────────┐
│  Developer uses skill → Great PR description                   │
│                              ↓                                 │
│  Reviewer sees it → "Wow, this is thorough"                   │
│                              ↓                                 │
│  Reviewer asks → "How did you write this?"                    │
│                              ↓                                 │
│  Developer shares → "uvx add-skill kasperjunge/pr"            │
│                              ↓                                 │
│  Reviewer installs → FLYWHEEL SPINS                           │
└────────────────────────────────────────────────────────────────┘
```

### Output Format
```markdown
## Summary
Brief explanation of what this PR does and WHY.

## Changes
- `src/auth.ts`: Refactored token validation logic
- `src/middleware.ts`: Added rate limiting
- `tests/auth.test.ts`: Added edge case coverage

## Test Plan
- [ ] Unit tests pass
- [ ] Manual testing of login flow
- [ ] Verified rate limiting works

## Breaking Changes
None

---
📋 *Generated with [agent-resources](https://github.com/kasperjunge/agent-resources)*
```

### Built-in Viral Hook
The footer attribution is seen by EVERY reviewer. Each PR becomes an ad.

### Impact Score: 10/10

---

## 2. `readme` — README Generator

### The Pain
- Most READMEs are outdated or incomplete
- Writing good docs is tedious
- Developers would rather code than document
- Bad READMEs hurt adoption

### The Solution
Analyze the entire codebase and generate a beautiful, comprehensive README.

### What Makes It Viral
- **Public output**: Every repo visitor sees it
- **Quality gap**: Most READMEs are bad, so a good one stands out
- **Attribution**: Footer links back to agent-resources
- **Shareable**: "Look at this README I generated in 30 seconds"

### Output Format
```markdown
<div align="center">

# 🚀 Project Name

**One-line description of what this does.**

[![npm](https://img.shields.io/npm/v/package)](link)
[![License](https://img.shields.io/badge/license-MIT-blue)](link)

[Installation](#installation) • [Usage](#usage) • [API](#api) • [Contributing](#contributing)

</div>

## Installation

\`\`\`bash
npm install package-name
\`\`\`

## Quick Start

\`\`\`javascript
// Example code showing basic usage
\`\`\`

## API Reference

### `functionName(params)`

Description of what it does...

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT © [Author](link)

---

<sub>📖 README generated with [agent-resources](https://github.com/kasperjunge/agent-resources)</sub>
```

### The "Holy Shit" Moment
Developer runs the skill, gets a README that's BETTER than they would have written manually. Instantly shareable.

### Impact Score: 10/10

---

## 3. `release` — Release Notes Generator

### The Pain
- Writing release notes is tedious
- Requires going through commits manually
- Often forgotten or half-assed
- Users need to know what changed

### The Solution
Analyze commits since last tag, categorize changes, generate human-readable release notes.

### What Makes It Viral
- **Public output**: Release notes are seen by ALL users
- **Open source gold**: Every maintainer needs this
- **Time saved**: Hours → seconds
- **Attribution**: Visible in every release

### Output Format
```markdown
# v2.1.0 (2025-01-05)

## ✨ New Features
- Add dark mode support (#123)
- New export to PDF functionality (#145)

## 🐛 Bug Fixes
- Fix memory leak in data processing (#134)
- Resolve race condition in auth flow (#156)

## 🔧 Improvements
- 40% faster startup time
- Reduced bundle size by 15%

## 💥 Breaking Changes
- `oldMethod()` renamed to `newMethod()`
- Minimum Node version is now 18

## 📦 Dependencies
- Upgraded React from 18.2 to 19.0
- Added new dependency: zod

---
*Release notes generated with [agent-resources](https://github.com/kasperjunge/agent-resources)*
```

### Why Maintainers Will LOVE This
1. Run one command before release
2. Get perfect release notes
3. Never manually categorize commits again
4. Users actually know what changed

### Impact Score: 9/10

---

## 4. `onboard` — Codebase Onboarding Guide

### The Pain
- Joining a new codebase is overwhelming
- Documentation is outdated or missing
- Takes weeks to feel productive
- Senior devs waste time explaining

### The Solution
Generate a comprehensive onboarding guide for ANY codebase. Architecture, key files, patterns, gotchas.

### What Makes It Viral
- **Mind-blowing capability**: "It understood our entire codebase"
- **Team sharing**: Onboarding doc shared with all new hires
- **Wow factor**: Instant understanding of complex systems
- **Saves senior time**: No more repeated explanations

### Output Format
```markdown
# Onboarding Guide: project-name

## Architecture Overview

This is a [Next.js/Express/etc] application that [does X].

\`\`\`
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   API       │────▶│  Database   │
│  (React)    │     │  (Express)  │     │  (Postgres) │
└─────────────┘     └─────────────┘     └─────────────┘
\`\`\`

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `src/api/` | REST API endpoints |
| `src/services/` | Business logic |
| `src/models/` | Database models |
| `src/utils/` | Shared utilities |

## Entry Points

- **Web app**: `src/app/page.tsx`
- **API server**: `src/server/index.ts`
- **CLI**: `src/cli/main.ts`

## Core Patterns

### Authentication
Auth is handled by `src/services/auth.ts`. We use JWT tokens stored in...

### Data Flow
1. Request comes in at `src/api/routes/`
2. Validated by middleware in `src/middleware/`
3. Processed by service in `src/services/`
4. Persisted via model in `src/models/`

## Common Tasks

### Adding a new API endpoint
1. Create route in `src/api/routes/`
2. Add service logic in `src/services/`
3. Write tests in `tests/api/`

### Running locally
\`\`\`bash
npm install
npm run dev
\`\`\`

## Gotchas & Tribal Knowledge

- The `legacy/` folder is deprecated, don't add code there
- Always use `utils/logger` instead of console.log
- Database migrations must be backwards compatible

---
*Generated with [agent-resources](https://github.com/kasperjunge/agent-resources)*
```

### The "Holy Shit" Moment
New hire runs this on day 1, understands the codebase in 10 minutes instead of 2 weeks.

### Impact Score: 9/10

---

## 5. `changelog` — CHANGELOG.md Generator

### The Pain
- Maintaining CHANGELOG.md manually is tedious
- Often forgotten or inconsistent
- Users want to see history at a glance
- Follows specific format (Keep a Changelog)

### The Solution
Generate and maintain a proper CHANGELOG.md following the [Keep a Changelog](https://keepachangelog.com/) format.

### What Makes It Viral
- **Public output**: Visible in every repo
- **Standard format**: Follows established convention
- **Always current**: Never outdated
- **Attribution**: Footer in changelog

### Output Format
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added
- New search functionality

### Changed
- Improved error messages

## [2.0.0] - 2025-01-05

### Added
- Dark mode support
- Export to PDF

### Changed
- Redesigned settings page

### Fixed
- Memory leak in data processing

### Removed
- Deprecated `oldApi()` method

## [1.5.0] - 2024-12-01

...

---
*Maintained with [agent-resources](https://github.com/kasperjunge/agent-resources)*
```

### Why It Spreads
1. Every repo needs a changelog
2. Manual maintenance sucks
3. Standard format = universal appeal
4. Attribution in every repo

### Impact Score: 8/10

---

# Viral Mechanics Summary

## Built-in Attribution Strategy

Each skill outputs a small footer:
```
*Generated with [agent-resources](https://github.com/kasperjunge/agent-resources)*
```

This creates **passive marketing**:
- Every PR description → marketing to reviewers
- Every README → marketing to repo visitors
- Every release note → marketing to users
- Every changelog → marketing to contributors

## The Network Effect

```
1 developer uses `pr` skill
        ↓
5 reviewers see the great PR description
        ↓
2 reviewers install the skill
        ↓
10 more reviewers see great PRs
        ↓
4 more install
        ↓
EXPONENTIAL GROWTH
```

## Priority Order for Building

| Priority | Skill | Why First |
|----------|-------|-----------|
| 1 | `pr` | Highest frequency, team-wide visibility |
| 2 | `readme` | Public visibility, massive wow factor |
| 3 | `release` | Open source community, high value |
| 4 | `onboard` | Unique capability, mind-blowing |
| 5 | `changelog` | Standard need, easy win |

---

# Implementation Notes

## Key Success Factors

1. **Quality over features**: The output must be BETTER than manual
2. **Sensible defaults**: Work great out of the box
3. **Customizable**: Allow users to tweak the format
4. **Fast**: Results in seconds, not minutes
5. **Attribution**: Every output links back

## The "Holy Shit" Test

Before shipping, verify:
- [ ] Would I share this with my team?
- [ ] Is the output better than what I'd write manually?
- [ ] Did I have a "wow" moment when I first used it?
- [ ] Would I tell a friend about this?

If all yes → Ship it. 🚀
