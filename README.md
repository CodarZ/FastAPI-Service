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
