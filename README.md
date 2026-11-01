<p align="center">
  <a href="#">
    <img src="./assets/logo.png" alt="FastAPI Service Logo" width="160" height="160" />
  </a>
</p>
<h1 align="center">FastAPI Service</h1>
<p align="center">基于 FastAPI 的高性能现代化异步后端服务模版</p>
<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-0.162-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/SQLAlchemy-2.1-D71F00?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy" />
  <img src="https://img.shields.io/badge/Pydantic-2.14-E92063?logo=pydantic&logoColor=white" alt="Pydantic" />
  <img src="https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Redis-8.1-DC382D?logo=redis&logoColor=white" alt="Redis" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/uv-F69220?logo=uv&logoColor=white" alt="uv" />
  <img src="https://img.shields.io/badge/Ruff-0.17-E5E5E5?logo=ruff&logoColor=black" alt="Ruff" />
  <img src="https://img.shields.io/badge/pre--commit-Hook-EA4435?logo=precommit&logoColor=white" alt="pre-commit" />
  <img src="https://img.shields.io/badge/Commitizen-4.18-007A88" alt="Commitizen" />
  <img src="https://img.shields.io/badge/prek-0.5-FF6B35" alt="prek" />
</p>

## ✨ 技术栈 & 特性

- ⚡ **FastAPI** - 高性能异步 Web 框架，自动生成 OpenAPI 文档
- 🐍 **Python 3.14** - Python 版本
- 🗄️ **PostgreSQL** - 异步驱动 asyncpg + SQLAlchemy 2.0 async
- 📦 **Redis** - 缓存 / 消息队列
- 📋 **Pydantic** - 数据校验
- 📝 **Loguru** - 结构化日志
- 🔧 **uv** - Python 包管理
- ✅ **Ruff** - 代码检查 + 格式化
- 🚫 **Commitizen** - 规范化 Git 提交
- 🪝 **prek** - Rust 编写的极速 Git Hook 管理器，替代 pre-commit
- 🤖 **AI Agent Skills** - AI 技能规范

## 🚀 快速开始

### 依赖安装

```bash
uv sync --all-groups
```

### 启动服务

- 开发模式（热重载）

  ```bash
  fastapi dev
  ```

- 生产模式

  ```bash
  fastapi run
  ```

## 📝 开发规范

- 初始化 `Git Hooks`

  ```bash
  uv run prek install -t pre-commit -t commit-msg -t pre-push
  ```

  > 临时跳过钩子：`git commit --no-verify` / `git push --no-verify`

- 检查与格式化

  ```bash
  uv run ruff check . --fix
  uv run ruff format .
  ```

- 运行测试

  ```bash
  uv run pytest
  ```

- 规范化 Git 提交

  ```bash
  uv run cz c
  ```

- 自动化版本管理

  ```bash
  uv run cz bump --dry-run                        # 预览下一个版本号（不执行）
  uv run cz bump                                  # 按提交历史自动发版（feat→次版本，fix→修订版本，!/BREAKING CHANGE→主版本）
  uv run cz bump --increment <patch|minor|major>  # 指定版本升级级别
  ```

  - 预发布版本（PEP 440 格式：`0.1.1a0` = alpha，`0.1.1b0` = beta，`0.1.1rc0` = rc）

    ```bash
    # 以 `beta` 为例
    uv run cz bump --prerelease beta --increment patch   # 1. 发预发布：0.1.0 → 0.1.1b0（alpha/rc 同理）
    uv run cz bump --prerelease beta --increment patch   # 2. 再次执行：0.1.1b0 → 0.1.1b1
    uv run cz bump --increment patch                     # 3. 转正式版：0.1.1b1 → 0.1.1
    ```

- 推送提交与版本 tag

  ```bash
  git push --follow-tags
  ```

## 🤖 AI Agent Skills

本项目通过 [skills.sh](https://skills.sh/) 集成技能，并由 `skills-lock.json` 进行依赖版本锁定。

### 常用命令

- **还原项目技能**：

  ```bash
  npx skills experimental_install
  ```

- **更新项目技能至最新版本**：

  ```bash
  npx skills update -p
  ```

<p align="center">
  <sub>Built with ❤️ using modern backend service technologies</sub>
</p>
