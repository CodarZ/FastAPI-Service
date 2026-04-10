---
name: create-model-schema
description: 'Creates, refactors, and validates SQLAlchemy 2.0 Models and Pydantic V2 Schemas with strict Zero Physical Foreign Key enforcement and 15-tier schema stratification. Use when building or modifying domain models, request/response schemas, API contracts, M:N mapping tables, or common/schema/type definitions. Automatically blocks relationship/ForeignKey insertions.'
user-invocable: true
allowed-tools: 'Read, Write, Edit, Bash, Glob, Grep, MCP (sequential-th_sequentialthinking, memory, mcp_context7, mcp_git, mcp_exa, mcp_fetch, mcp_time)'
hooks:
  PostToolUse:
    - matcher: 'Write|Edit|Bash'
      hooks:
        - type: command
          command: 'if ls backend/app/*/model/*.py 1> /dev/null 2>&1; then export SD="${CLAUDE_PLUGIN_ROOT:-$(pwd)/.agents/skills/create-model-schema}/scripts"; $(command -v python3 || command -v python) "$SD/check-model-fk.py" $(find backend/app/*/model -name ''*.py'' -not -name ''__init__.py''); fi'
metadata:
  version: '1.2.0'
---

# FastAPI Model & Schema Generator

Architectural tool for generating fully typed SQLAlchemy 2.0 Models and heavily stratified 16-tier Pydantic V2 Schemas.

## FIRST: Read the Baseline

**Before doing anything else**, load the authoritative logic configuration:

1. `reference.md` — The unbreakable conventions (Zero Physical FKs, 16 Suffix classes)
2. `examples.md` — Verified code templates for schemas and types

## Important: Workspace Rules

- **Templates** are in `${CLAUDE_PLUGIN_ROOT}/templates/`
- **Output files** go into `backend/app/<domain>/{api,crud,model,schema}/`

## Quick Start (The Standard Workflow)

1. **Context Scoping**: Read adjacent entities in the desired domain `model` and `schema` to grasp context.
2. **Scaffolding Model**: Copy `templates/model_template.py` and modify.
3. **Scaffolding Schema**: Copy `templates/schema_template.py`, pruning unused classes based on API scope.
4. **Validation Check**: Run `scripts/check-model-fk.py` locally before completing to ensure compliance.

## Core Directives

### 0. Language Requirement (Non-negotiable)

All generated project code comments, docstrings, and log messages MUST be written in **Simplified Chinese (简体中文)**.

### 1. The Zero Physical FK Rule (Non-negotiable)

You must **never** write `ForeignKey`, `relationship`, or `back_populates` inside `model/`. Keep only logical IDs (e.g. `dept_id: Mapped[int]`). The hook script actively prevents this and will fail the transaction if violated.

### 2. The 16-Schema Suffix Stratification

Schema class names must be exact (e.g. `UserCreate`, `UserDetail`, `UserOptionTree`). No "loose" arbitrary Schemas. See `reference.md` for definitions.

### 3. Smart Pydantic Configuration (`extra` routing)

- General Input (`Create`, `Update`): Defaults to `extra='ignore'` (inherited).
- Output & Views (`Info`, `Detail`, `ListItem`): Must be `ConfigDict(from_attributes=True)`.
- Option Maps (`Option`, `OptionTree`): Must be `ConfigDict(from_attributes=True, populate_by_name=True)`.
- Secure/Risk inputs: Only selectively declare `extra='forbid'` for risk endpoints (e.g. webhook payload).

### 4. Custom Types Go Global

If a validator or specific format type (`phone`, `code`, `id_list`) is used across 2+ schemas, extract it to `backend/common/schema/type/__init__.py` using `Annotated[..., AfterValidator(...)]`.

### 5. Multi-to-Multi Strategy

All M:N bridging tables live exclusively in `backend/app/admin/model/m2m.py` (or the equivalent domain's `m2m.py`), subclassing `DataClassBase`.

## Read vs Write Decision Matrix

| Situation                   | Action                          | Reason                            |
| --------------------------- | ------------------------------- | --------------------------------- |
| New domain                  | Read `m2m.py` & basic model     | Verify global base patterns       |
| Custom string format        | Read `common/schema/type/`      | Reuse existing `Annotated` types  |
| Multi-level tree output     | Check `OptionTree` & `TreeNode` | Enforce self-referential children |
| Modifying an existing Model | Run AST Validator Script        | Prevent FK regression via editing |

## Anti-Patterns

| Don't                               | Do Instead                                               |
| ----------------------------------- | -------------------------------------------------------- |
| Use `relationship(lazy='joined')`   | Use `select().join()` inside `crud/` layer               |
| Append `extra='forbid'` dynamically | Stick to default `SchemaBase` ignoring unused properties |
| Put all validation in `Schema`      | Extract to `backend/common/schema/type/func.py`          |
| Create `SysAdminResponse`           | Use semantic `SysAdminInfo` or `SysAdminDetail`          |

## MCP Tool Integration

This skill benefits heavily from specific MCP servers. Use them proactively when executing complex refactors:

- **`mcp_sequential-th_sequentialthinking`**: Trigger this _before_ writing code to map out exactly which of the 16 schema tiers are needed for the current domain. This prevents generating unused "ghost" schemas.
- **`memory`**: Read `/memories/repo/` before scaffolding to check if there are specific domain conventions, customized common types, or previously resolved edge-cases.
- **`mcp_context7`**: Query context7's `sqlalchemy` or `pydantic` documentation if you hit an edge case with SQLAlchemy 2.0 syntax (like advanced JSONB arrays) or Pydantic V2 runtime validations.- **`mcp_git`**: When refactoring an existing core model, use `git log` or `git diff` to understand the historical context of why certain fields were added, ensuring you don't accidentally break dependent schemas.
- **`mcp_exa` / `mcp_fetch`**: If asked to build models/schemas for a third-party integration (e.g., Stripe webhooks, OAuth payloads), use these to search and fetch the exact latest official JSON contracts from the web to map them accurately.
- **`mcp_time`**: Call this if you need to generate time-sensitive default fields, precise timestamp comments, or migration version notes in UTC/Local time.

## Scripts

- `scripts/check-model-fk.py`: Checks AST to ensure zero physical FKs. Automatically runs after edits.

## Templates

- `templates/model_template.py`: Starter boilerplate for `Base`.
- `templates/schema_template.py`: Full 16-tier schema layout.
