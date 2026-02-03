# FastAPI-Service

## 快速开始

```bash
# 安装依赖
uv sync

# 安装 Git 钩子
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
```

### 🔐 初始超级管理员

应用首次启动时会自动创建初始超级管理员账户：

- **默认用户名**: `admin`
- **默认密码**: `123456` (⚠️ 请在 `.env` 文件中修改)

**安全提醒**：生产环境部署，请务必修改默认密码！

## 分支管理策略

本项目采用 **双分支工作流**：

- **`master`**: 生产分支，每次合并自动触发版本发布和部署
- **`develop`**: 开发分支，日常开发的基准分支
- **功能分支**: 命名规范 `feature/`、`bugfix/`、`hotfix/`、`refactor`等

## 日常开发流程

### 1. 从 develop 创建功能分支

```bash
# 切换并更新 develop 分支
git checkout develop
git pull origin develop

# 创建功能分支（命名规范：feature/bugfix/hotfix/refactor）
git checkout -b feature/user-login

# 开发代码...
```

### 2. 提交代码

```bash
# 使用 Commitizen 交互式提交（自动验证格式）
uv run cz commit

# 提交格式示例：
# ✨ feat(system/user): 新增用户登录接口
# 🐛 fix(core/auth): 修复 Token 验证逻辑
# ♻️ refactor(common): 重构响应处理模块
```

### 3. 推送并创建 PR

```bash
# 推送功能分支
git push origin feature/user-login

# 在 GitHub 创建 Pull Request
# Base: develop ← Compare: feature/user-login
# 等待代码审查通过后合并
```

### 4. 准备发布到 master

```bash
# 当 develop 积累了足够的功能，准备发布时
# 在 GitHub 创建 Pull Request
# Base: master ← Compare: develop

# PR 标题建议：🔖 Release: X.X.X 版本发布
# 审查通过后合并到 master
```

### 5. 自动版本发布（GitHub Action）

合并到 `master` 后，GitHub Action 自动执行：

1. 分析 `develop → master` 的提交记录
2. 根据提交类型自动升级版本号（MAJOR/MINOR/PATCH）
3. 更新 `pyproject.toml` 版本号
4. 生成 `CHANGELOG.md`
5. 创建 Git Tag（如 `0.1.0`）
6. 推送版本标签到仓库
7. 触发后续部署流程

## 常用命令

### 依赖管理

#### 安全升级所有依赖

```bash
# 1. 升级所有依赖到最新兼容版本（更新 uv.lock）
uv lock --upgrade

# 2. 同步安装升级后的依赖
uv sync

# 3. 查看已安装的依赖版本
uv pip list

# 4. 查看过时的依赖
uv pip list --outdated

# 5. 同步版本号到 requirements.txt（可选，项目已配置自动同步）
uv pip compile pyproject.toml -o requirements.txt
```

#### 升级特定依赖

```bash
# 升级单个包到最新版本
uv lock --upgrade-package fastapi
uv sync

# 升级多个包
uv lock --upgrade-package fastapi --upgrade-package pydantic
uv sync

# 或者使用简写形式
uv lock -P fastapi -P pydantic
uv sync
```

#### 依赖安全检查

```bash
# 查看依赖树
uv tree

# 查看过时的依赖
uv pip list --outdated

# 检查依赖的安全漏洞（需要额外工具）
uv run pip-audit
```

#### 完整升级流程（推荐）

```bash
# 步骤 1: 创建功能分支
git checkout develop
git pull origin develop
git checkout -b chore/upgrade-dependencies

# 步骤 2: 备份当前锁定文件（可选）
cp uv.lock uv.lock.backup

# 步骤 3: 升级所有依赖
uv lock --upgrade
uv sync

# 步骤 4: 运行测试确保兼容性
uv run pytest

# 步骤 5: 运行代码检查
uv run pre-commit run --all-files

# 步骤 6: 如果测试失败，回滚
# mv uv.lock.backup uv.lock
# uv sync

# 步骤 7: 提交变更（使用 Commitizen）
git add uv.lock pyproject.toml requirements.txt
uv run cz commit
# 选择: ⬆️ upgrade: 升级项目依赖到最新兼容版本

# 步骤 8: 推送并创建 PR
git push origin chore/upgrade-dependencies
# 在 GitHub 创建 PR，等待审查后合并到 develop
```

**注意事项：**

- `uv lock --upgrade` 或 `uv lock -U` 会升级所有依赖到符合 `pyproject.toml` 版本约束的最新版本
- `uv sync` 会根据锁定文件同步安装依赖到虚拟环境
- 升级后务必运行完整测试套件，确保所有功能正常
- **必须**在功能分支中进行依赖升级，通过 PR 审查后再合并
- Pre-commit 钩子会自动同步 `requirements.txt`，无需手动维护
- 大版本升级建议查看 CHANGELOG，可能需要代码适配

### 代码检查与格式化

```bash
# 运行所有 pre-commit 检查（自动）
uv run pre-commit run --all-files

# Python 代码检查与格式化
uv run ruff check .              # 检查代码质量
uv run ruff format .             # 格式化代码
uv run ruff check . --fix        # 自动修复问题

# JSON/YAML/Markdown 格式化（手动）
bunx prettier --check "**/*.{json,yaml,md}"  # 仅检查
bunx prettier --write "**/*.{json,yaml,md}"
```

### 测试

```bash
# 运行测试
uv run pytest

# 查看覆盖率
uv run pytest --cov=app --cov-report=html
```

### 数据库迁移（Alembic）

完整的数据库迁移文档请查看：[**backend/alembic/README.md**](backend/alembic/README.md)

快速开始：

```bash
# 1. 自动生成迁移脚本
uv run alembic revision --autogenerate -m "添加用户表"

# 2. 应用迁移
uv run alembic upgrade head

# 3. 查看当前版本
uv run alembic current
```

### 手动版本发布（本地调试用）

不推荐，应使用 `GitHub Action`

```bash
# 预览版本变更
uv run cz bump --dry-run

# 手动升级版本
uv run cz bump

# 推送版本标签
git push origin master --follow-tags
```

## 提交规范

使用 `uv run cz commit` 交互式提交

## 工具链

### 自动检查（Pre-commit 集成）

- **uv**: Python 包管理器
- **Commitizen**: 规范化提交和自动版本管理
- **Pre-commit**: 代码提交前自动检查
  - **Ruff**: Python 代码检查和格式化（支持 .py/.pyi/.ipynb）
  - **Bandit**: Python 安全漏洞扫描
  - **YAML/JSON/TOML 验证**: 语法校验（pre-commit-hooks）
  - **UV 依赖同步**: 自动更新 requirements.txt

### 手动检查工具

- **Prettier**: JSON/YAML/Markdown 格式化

### 其他工具

- **Alembic**: 数据库迁移
- **Pytest**: 单元测试
- **GitHub Actions**: CI/CD 自动化

### 工具职责划分

| 文件类型               | 格式化工具       | Lint 工具        | 配置文件                             | Pre-commit |
| ---------------------- | ---------------- | ---------------- | ------------------------------------ | ---------- |
| Python (`.py`, `.pyi`) | Ruff             | Ruff + Bandit    | [ruff.toml](ruff.toml)               | ✅ 自动    |
| Jupyter (`.ipynb`)     | Ruff             | Ruff             | [ruff.toml](ruff.toml)               | ✅ 自动    |
| JSON/YAML/Markdown     | Prettier         | pre-commit hooks | [.prettierrc.yaml](.prettierrc.yaml) | ⚠️ 手动    |
| TOML                   | Even Better TOML | pre-commit check | [.editorconfig](.editorconfig)       | ✅ 自动    |

## 相关配置

- [Commitizen 配置](cz.toml) - 提交规范和版本管理
- [Pre-commit 配置](.pre-commit-config.yaml) - Git 钩子
- [Ruff 配置](ruff.toml) - 代码检查规则
- [项目依赖](pyproject.toml) - Python 包管理

## 许可证

MIT
