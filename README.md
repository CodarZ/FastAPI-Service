# FastAPI Service

## 提交规范

本项目使用 Commitizen 来规范化提交消息格式。

### 快速使用

```bash
# 交互式提交（推荐）
chmod +x ./commit.sh # 第一次需要执行该命令, 授予权限
./commit.sh

# 直接使用 Commitizen
uv run cz --config .cz.toml commit

# 快速提交
uv run cz --config .cz.toml c
```

### 支持的提交类型

- ✨ feat: 新功能
- 🐛 fix: 修复 Bug
- 📝 docs: 文档更新
- 🎨 style: 代码格式化
- ♻️ refactor: 代码重构
- ⚡️ perf: 性能优化
- ✅ test: 增加或修改测试
- 🔧 chore: 更改依赖、修改配置等
- 🏗️ build: 影响构建系统或外部依赖的更改
- 👷 ci: CI/CD 相关更改
- ⏪ revert: 回退之前的提交
- ⬆️ upgrade: 升级依赖
- 🔥 remove: 移除代码或文件
- 🎉 init: 初始提交
- 🔒 security: 安全性修复

## 版本管理

本项目使用 Commitizen 自动化版本管理，基于符合规范的提交消息自动生成版本号和变更日志。

### 版本发布

```bash
# 预览即将发布的版本（不实际更新）
uv run cz --config .cz.toml bump --dry-run

# 自动分析提交记录并更新版本号
uv run cz --config .cz.toml bump

# 手动指定版本类型
uv run cz --config .cz.toml bump --increment MAJOR    # 主版本 (1.0.0 -> 2.0.0)
uv run cz --config .cz.toml bump --increment MINOR    # 次版本 (1.0.0 -> 1.1.0)
uv run cz --config .cz.toml bump --increment PATCH    # 补丁版本 (1.0.0 -> 1.0.1)
```

### 版本规则

Commitizen 会根据提交类型自动决定版本更新方式：

- **BREAKING CHANGE** 或包含 `!` 的提交 → 主版本更新 (MAJOR)
- **feat** 类型的提交 → 次版本更新 (MINOR)
- **fix** 类型的提交 → 补丁版本更新 (PATCH)
- 其他类型的提交 → 不更新版本
