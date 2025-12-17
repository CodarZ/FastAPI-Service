## 0.6.0 (2025-12-17)

### ✨ 新功能

- **app/admin/user**: 新增 SysUser 用户信息表
- **alembic**: 新增 alembic 配置、指南、最佳实践

### 🐛 问题修复

- **common/model**: 修复 SQLAlchemy 在运行时解析注解错误

## 0.5.0 (2025-12-17)

### ✨ 新功能

- **middleware**: 新增请求状态中间件
- **common**: 新增解析请求的用户代理信息、IP 地址
- **static**: 新增 ip2region 的离线文件
- 新增 FastAPI Limiter 限制请求

### 🐛 问题修复

- **database**: 修复 Redis 使用 execute_command 替代 ping 方法避免类型检查错误

### 🔧 日常维护

- 新增 IP 地址归属地查询依赖库 py-ip2region

## 0.4.0 (2025-12-16)

### ✅ test

- **utils**: 测试加密工具套件

### ✨ 新功能

- **database**: 新增 Redis 支持
- **database**: 新增 PostgreSQL 数据库支持
- **common/model**: 新增 SQLAlchemy ORM 基础模型和主键
- **utils**: 新增加密工具套件

### ⬆️ 依赖升级

- 升级项目依赖到最新兼容版本

### 🎉 init

- **tests**: 初始化 pytest

### 👷 CI/CD

- **.github**: 简化 release 环境
- **.github**: 跳过同步依赖和 release 类型

## 0.3.0 (2025-12-14)

### ✨ 新功能

- **middleware/assess**: 新增访问日志中间件
- **common/log**: 新增基于 loguru 的日志拦截处理器
- **utils**:  新增路由工具

### 👷 CI/CD

- **.github**: 修复 release 环境

## 0.2.0 (2025-12-12)

### ✨ 新功能

- **common/exception**: 新增统一捕获异常处理

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
