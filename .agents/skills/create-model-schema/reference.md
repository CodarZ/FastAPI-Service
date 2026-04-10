# Model & Schema Reference Specification

This document serves as the **authoritative rulebook** for the `./SKILL.md` skill. All generations and refactoring MUST strictly adhere to the rules defined here, overriding any conflicting LLM presumptions.

## 1. Project Baseline

- **Python**: >= 3.14
- **FastAPI**: 0.135.3
- **Pydantic**: >= 2.12.5
- **SQLAlchemy**: >= 2.0.48

**Key Base Classes**:

- **Model Base Branches** (`backend/common/model.py`):
  - `Base`: For standard business domain tables (includes standard timestamps).
  - `DataClassBase`: For minimal junction tables (M:N) or configuration tables.
  - `id_key` / `uuid_key`: Standard types for primary IDs and UUIDs.
- **Schema Base** (`backend/common/schema/__init__.py`):
  - `SchemaBase` uses: `model_config = ConfigDict(use_enum_values=True, extra='ignore', str_strip_whitespace=True)`

## 2. Directory Structure & Naming Conventions

- **Domain Isolation**: `backend/app/<domain>/<api|crud|model|schema>`
- **File Naming**: `snake_case`, e.g., `sys_admin.py`, `sys_dept.py`.
- **Junction Tables (M:N)**: Placed centrally in `model/m2m.py` within the respective domain.
- **Class Naming**: `<EntityPrefix><SemanticSuffix>`, e.g., `SysAdminDetail`, `SysDeptCreate`.

## 3. SQLAlchemy 2.0 Model Specification

1. **Type Annotations**: You MUST use `Mapped[...]` combined with `mapped_column(...)`.
2. **Column Constraints**:
   - String fields MUST declare a length (e.g., `String(64)`).
   - DateTime fields MUST use timezone-aware types.
   - EVERY column MUST have a `comment='...'` argument (in Chinese).
   - Commonly queried fields SHOULD have `index=True`.
   - Distinct semantic fields SHOULD use `unique=True`.
3. **The ZERO Physical Foreign Key Rule (Red Line Requirement)**:
   - Prohibited: `ForeignKey`, `relationship`, `back_populates`.
   - Permitted: ONLY logical relational IDs (e.g., `dept_id: Mapped[int]`, `role_id: Mapped[int]`).
4. **Tree Structures**:
   - Must use `parent_id` (Integer).
   - Optionally use a `tree` attribute (String) to store recursive paths.

## 4. The 16-Tier Pydantic Schema Stratification

All generated Pydantic definitions MUST map to one of these exact suffixes based on their operational purpose. Do NOT create arbitrary schemas.

| Category       | Exact Suffix   | Purpose & Rules                                                                                                                      | Example                    |
| :------------- | :------------- | :----------------------------------------------------------------------------------------------------------------------------------- | :------------------------- |
| **Foundation** | `Base`         | Core reusable fields. Parent for other schema tiers.                                                                                 | `SysAdminBase`             |
| **Input**      | `Create`       | Full payload validation for `POST` (Creation).                                                                                       | `SysAdminCreate`           |
| **Input**      | `Update`       | Full payload & strict validation for `PUT` (Total Replacement).                                                                      | `SysAdminUpdate`           |
| **Input**      | `Patch<Field>` | Fine-grained partial update mapping to `PATCH` logic. Include specfic actions like `PatchPassword`, `ResetPassword`, `PatchProfile`. | `SysAdminPatchStatus`      |
| **Input**      | `Map`          | Maintenance mapping schema (M:N).                                                                                                    | `SysAdminRoleMap`          |
| **Operation**  | `BatchDelete`  | Array payload for bulk deletion routing.                                                                                             | `SysAdminBatchDelete`      |
| **Operation**  | `BatchPatch`   | Array payload combined with state for bulk updates.                                                                                  | `SysAdminBatchPatchStatus` |
| **Output**     | `InfoBase`     | Base for output schemas injecting system IDs and statuses.                                                                           | `SysAdminInfoBase`         |
| **Output**     | `Info`         | Standard overview payload (Cards/Previews).                                                                                          | `SysAdminInfo`             |
| **Output**     | `Detail`       | Deep data output. May include calculated M:N or 1:N relations.                                                                       | `SysAdminDetail`           |
| **Output**     | `ListItem`     | Flattened struct optimized for paginated tables/lists.                                                                               | `SysAdminListItem`         |
| **Output**     | `TreeNode`     | Recursive structure holding nested `children`.                                                                                       | `SysDeptTreeNode`          |
| **Compact**    | `Simple`       | Extremely minimal attribute set for nested representations.                                                                          | `SysAdminSimple`           |
| **Compact**    | `Option`       | Dropdown dictionary mapping standard values using aliases.                                                                           | `SysAdminOption`           |
| **Compact**    | `OptionTree`   | Dropdown mapping optimized for recursive tree pickers.                                                                               | `SysDeptOptionTree`        |
| **Query**      | `Filter`       | GET request parameter mapping encapsulating advanced filters.                                                                        | `SysAdminFilter`           |

## 5. Schema Config & Field Semantics

1. **Universal Field Requirement**: Every field MUST utilize `Field(..., description='...')` with constraints like `max_length`, `ge` where applicable. Descriptions must be in Chinese.
2. **Schema Separation and Documentation**:
   - MUST use `# ==================== 输入 Schema ====================` (and equivalent headers like `输出 Schema`, `分类 Config/Option`) to logically separate the file into sections.
   - EVERY Schema class MUST have a Python docstring (e.g., `"""实体更新请求实体."""`) explaining its specific operation.
3. **`ConfigDict` Routing**:
   - **Outputs** (`InfoBase`, `Info`, `Detail`, `ListItem`, `TreeNode`, `Simple`): MUST use `ConfigDict(from_attributes=True)`.
   - **Dropdowns** (`Option`, `OptionTree`): MUST use `ConfigDict(from_attributes=True, populate_by_name=True)` combined with aliases (`value = Field(alias='id')`, `label = Field(alias='name')`).
   - **Standard Inputs** (`Create`, `Update`, `Patch`, `Map`): Inherit default `SchemaBase` via `extra='ignore'`, blocking noisy `422 extra_forbidden` errors from overloaded frontends.
   - **Strict Inputs**: Use `extra='forbid'` ONLY for high-risk, rigid contract endpoints (e.g., webhook signatures, strict gateways). Document why in a docstring.
4. **Relational Expansion (Type-Safe)**: When `Detail`, `Info` or `ListItem` schemas need logical relational data, utilize `@computed_field` to flatten properties (e.g., extracting `role_names`, `dept_name`) alongside excluded internal fields. The injected internal fields **MUST** use the corresponding entity's `Simple` Schema as their precise type annotation — **NEVER** use bare `list`, `object`, or `Any`. For example: `_roles: list[SysRoleSimple]`, `_dept: SysDeptSimple | None`. See `examples.md §5` for the canonical pattern.
5. **UUID Field Safety**: When a schema needs a UUID field, ALWAYS import from the standard library: `from uuid import UUID`. NEVER import UUID from `sqlalchemy`.
6. **Global Custom Types (`backend/common/schema/type`)**:
   - Types reused across 2+ schemas MUST be extracted as an `Annotated` global alias.
   - Examples: `CodeStr`, `PhoneMaskedStr`, `IdsListInt`.
   - Naming: `<SemanticPrefix><TypeSuffix>` (e.g., `RateFloat`, `CNMobileStr`).

## 6. Junction Tables (M:N) Specifications

- Located strictly in `model/m2m.py` (not domain payload spaces).
- MUST inherit from `DataClassBase`.
- MUST include at least: `id` and the two logical foreign keys mapping the ends.
- MUST employ `UniqueConstraint` over the mapping IDs.
- MUST maintain the Zero Physical FK rule.

## 7. Anti-Patterns (Strictly Forbidden)

- DO NOT write `ForeignKey` / `relationship()` / `back_populates` in `model/*.py`.
- DO NOT generate exhaustive "shell" Schemas across all 15 tiers blindly; generate ONLY what the domain APIs truly consume.
- DO NOT skip the `value/label` alias system inside `Option` schema tiers.
- DO NOT leave `description` attributes blank or written in English.
- DO NOT use bare `list`, `object`, or `Any` for CRUD injected relational fields; ALWAYS use the precise `Simple` Schema type (e.g., `list[SysRoleSimple]`, `SysDeptSimple | None`).

## 8. Definition of Done (DoD)

1. The exact 15-tier suffix system is used correctly based on intent.
2. The SQLAlchemy model has 0 physical relational constraints.
3. `ConfigDict(from_attributes=True)` is mapped exactly where strictly required.
4. Docstrings, comments, and field descriptions are uniformly written in Chinese.
