# Alembic 数据库迁移指南

本目录包含项目的数据库迁移配置和脚本。

## 目录结构

```text
root/
├── backend/alembic/
├   ├── README.md                # 本文档
├   ├── env.py                   # 异步迁移环境配置
├   ├── script.py.mako           # 迁移脚本模板
├   └── versions/                # 迁移脚本存放目录
└── alembic.ini                  # Alembic 主配置文件
```

## 初始化配置（已完成）

项目已完成 Alembic 配置，包含以下文件：

- [`alembic.ini`](../../alembic.ini) - Alembic 主配置文件
- [`backend/alembic/env.py`](env.py) - 异步数据库迁移环境
- [`backend/alembic/script.py.mako`](script.py.mako) - 迁移脚本模板
- `backend/alembic/versions/` - 迁移脚本存放目录

## 添加新模型

### 推荐方式：使用 `__init__.py` 集中管理（当前项目采用）

1. 在模块的 `__init__.py` 中导入所有模型：

   ```python
   # backend/app/admin/model/__init__.py
   from backend.app.admin.model.user import SysUser
   from backend.app.admin.model.role import SysRole  # 新增模型时添加
   # ... 其他模型
   ```

2. 在 [`env.py`](env.py#L24) 中只需导入模块包：

   ```python
   # backend/alembic/env.py
   import backend.app.admin.model  # ✅ 自动加载 __init__.py 中的所有模型
   ```

**优点**：

- ✅ 集中管理：所有模型在 `__init__.py` 统一维护
- ✅ 简化配置：`env.py` 保持简洁
- ✅ 易于扩展：新增模型只需修改 `__init__.py`

### 备选方式：直接导入具体模型

如果不使用 `__init__.py` 集中管理，也可以直接导入：

```python
# backend/alembic/env.py
from backend.app.admin.model.user import SysUser
from backend.app.admin.model.role import SysRole
# ... 逐个导入
```

⚠️ **重要**：所有需要自动生成迁移的模型都必须在 [`env.py`](env.py) 中导入，否则 `--autogenerate` 将检测不到变更。

### 自定义类型支持

项目已在 [`script.py.mako`](script.py.mako#L12) 中预导入了 `backend.common.model`，这样迁移脚本可以正确识别项目中定义的自定义类型（如 `id_key` 等 Annotated 类型）。

如果你的模型使用了自定义类型或 Mixin，生成的迁移脚本将自动包含必要的导入，无需手动修改。

## 常用迁移命令

### 1. 自动生成迁移脚本（推荐）

```bash
uv run alembic revision --autogenerate -m "添加用户表"
```

### 2. 查看生成的迁移文件

文件位于: `backend/alembic/versions/YYYY-MM-DD-HH_MM_SS-<revision>_<描述>.py`

示例: `20251217-14_30_45-abc123def456_添加用户表.py`

⚠️ 检查生成的 `upgrade()` 和 `downgrade()` 函数是否正确

### 3. 应用迁移到数据库

```bash
uv run alembic upgrade head
```

### 4. 查看当前数据库版本

```bash
uv run alembic current
```

### 5. 查看迁移历史

```bash
uv run alembic history
```

### 6. 回滚到上一个版本

```bash
uv run alembic downgrade -1
```

### 7. 回滚到指定版本

```bash
uv run alembic downgrade <revision_id>
```

### 8. 查看未应用的迁移

```bash
uv run alembic heads
```

### 9. 手动创建空迁移文件（用于数据迁移等）

```bash
uv run alembic revision -m "数据迁移脚本"
```

## 迁移最佳实践

### 完整工作流程

```bash
# 步骤 1: 创建或修改模型

# 步骤 2: 确保模型已在 env.py 中导入
# 编辑: backend/alembic/env.py

# 步骤 3: 生成迁移脚本
uv run alembic revision --autogenerate -m "添加用户表的 is_active 字段"

# 步骤 4: 检查生成的迁移文件
# 查看: backend/alembic/versions/20251217-12_34_56-xxx_添加用户表的_is_active_字段.py
# ⚠️ 务必检查 upgrade() 和 downgrade() 是否符合预期

# 步骤 5: 应用这次迁移
uv run alembic upgrade head

# 步骤 6: 验证迁移结果
# 连接数据库，检查表结构是否正确

# 步骤 7: 提交代码
git add backend/alembic/versions/ backend/app/
uv run cz commit
# 选择: ✨ feat(database): 新增用户表的 is_active 字段
```

## 注意事项

### ⚠️ 重要提醒

- **自动生成并非完美**：`--autogenerate` 可能无法检测所有变更（如重命名列、修改约束等），请务必审查生成的迁移脚本
- **不可修改已应用的迁移**：已经执行过的迁移文件不应修改，如需调整，创建新的迁移文件
- **测试迁移**：在生产环境应用前，务必在测试环境验证迁移的正确性
- **回滚方案**：确保 `downgrade()` 函数正确实现，以便紧急回滚
- **数据迁移**：涉及数据迁移时，建议手动编写迁移脚本，避免使用 `--autogenerate`
- **环境隔离**：开发环境和生产环境的数据库版本应保持一致

### autogenerate 的局限性

`--autogenerate` 可以检测到：

- ✅ 新增/删除表
- ✅ 新增/删除列
- ✅ 修改列类型（部分）
- ✅ 修改列的 nullable 属性

`--autogenerate` 无法检测：

- ❌ 重命名表或列（会被识别为删除+新增）
- ❌ 修改约束名称
- ❌ 修改索引配置
- ❌ 修改数据库触发器、存储过程等

## 常见问题

### Q: 迁移脚本检测不到模型变更？

```bash
# 1. 确认模型已在 env.py 中导入
# 2. 检查模型是否继承自 Base 或 MappedBase
# 3. 尝试清理缓存：rm -rf backend/**/__pycache__
```

### Q: 如何处理多人开发的迁移冲突？

```bash
# 1. 拉取最新代码
git pull origin develop

# 2. 查看冲突的迁移文件
uv run alembic history

# 3. 使用 alembic merge 合并分支
uv run alembic merge -m "合并迁移分支" <revision1> <revision2>
```

### Q: 如何重置数据库（开发环境）？

```bash
# ⚠️ 危险操作，仅用于开发环境
# 1. 回滚所有迁移
uv run alembic downgrade base

# 2. 删除所有迁移文件
rm backend/alembic/versions/*.py

# 3. 重新生成初始迁移
uv run alembic revision --autogenerate -m "初始化数据库"

# 4. 应用迁移
uv run alembic upgrade head
```

### Q: 如何查看迁移 SQL 而不执行？

```bash
# 查看从当前版本到 head 的所有 SQL
uv run alembic upgrade head --sql

# 查看回滚的 SQL
uv run alembic downgrade -1 --sql
```

### Q: 如何处理线上紧急回滚？

```bash
# 1. 查看当前版本
uv run alembic current

# 2. 查看迁移历史，找到目标版本
uv run alembic history

# 3. 回滚到指定版本
uv run alembic downgrade <target_revision>

# 4. 验证数据库状态
uv run alembic current
```

## 配置说明

### alembic.ini

主配置文件位于项目根目录 [`alembic.ini`](../../alembic.ini)，主要配置项：

```ini
[alembic]
# 迁移脚本目录
script_location = backend/alembic

# 数据库 URL（从环境变量读取）
sqlalchemy.url =

# 迁移文件名格式（包含秒数，确保唯一性）
file_template = %%(year)d-%%(month).2d-%%(day).2d-%%(hour).2d_%%(minute).2d_%%(second).2d-%%(rev)s_%%(slug)s
```

### script.py.mako

迁移脚本模板 [`script.py.mako`](script.py.mako)，主要配置：

```python
# 预导入项目自定义类型模块，支持 Annotated 类型和 Mixin
import backend.common.model

# 模板会自动生成以下函数
def upgrade() -> None:
    """应用迁移（升级数据库结构）"""

def downgrade() -> None:
    """回滚迁移（降级数据库结构）"""
```

**为什么需要 `import backend.common.model`？**

- 项目使用了自定义的 `id_key` 等 Annotated 类型
- 使用了 `DateTimeMixin`、`UserMixin` 等 Mixin
- Alembic 生成迁移时需要能够解析这些自定义类型
- 预导入可以避免生成的迁移脚本出现类型识别错误

### env.py

异步迁移环境配置 [`env.py`](env.py)，主要功能：

- 导入所有数据库模型
- 配置异步数据库连接
- 定义 `run_migrations_offline()` 和 `run_migrations_online()` 函数

## 相关资源

- [Alembic 官方文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 2.0 文档](https://docs.sqlalchemy.org/en/20/)
- [项目主 README](../../README.md)
