## 0.1.1 (2025-12-12)

### 🎨 style

- 更新开发环境配置与代码规范

### 🐛 问题修复

- **common/response**: 修复 HTTP_400 状态的返回信息
- **common/request**: 修复上下文管理获取错误的问题

### 🔧 日常维护

- **.vscode**: 移除 copilot,chat,gitlens 非统一的配置项

## 0.1.0 (2025-12-10)

### ✨ 新功能

- **common/request**: 新增获取请求头 TRACE ID 工具方法
- **common/request**: 新增全局可用的请求上下文管理实例对象
- **core**: 新增上下文中间件
- **common/response**: 新增通用响应状态
- **utils**: 新增 datetime 转换工具
- **utils**: 新增 SQLAlchemy 查询结果序列化工具
- **common/enum**: 新增通用枚举模块与常用枚举
- **utils**: 新增工具: 从 pyproject.toml 读取项目版本号

### 🎉 init

- 初始化 FastAPI 服务启动
- 初始化项目目录结构
- 初始化项目标准化配置

### 👷 CI/CD

- **.github**: 新增 GitHub Actions 自动发版工作流

### 🔧 日常维护

- **.vscode**: VSCode 编辑器配置
- 新增项目基础配置信息、环境变量
- 添加项目核心依赖
- **.vscode**: VSCode 编辑器配置
