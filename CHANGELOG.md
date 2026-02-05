## 0.23.0 (2026-02-05)

### ♻️ 代码重构

- 重构分页功能, 移除自定义分页逻辑

### ✨ 新功能

- 新增分页功能

## 0.22.0 (2026-02-03)

### ⬆️ 依赖升级

- 升级项目依赖

## 0.21.0 (2026-02-03)

### ✨ 新功能

- 新增初始化超级管理员(superadmin)及相关配置

### 🏗️ 构建相关

- **deploy**: 修改健康检查的启动延迟时间
- **deploy**: 新增项目 Dockerfile

### 👷 CI/CD

- **cnb**: 新增 CNB 构建 Docker 镜像任务

## 0.20.2 (2026-02-03)

### 🐛 问题修复

- **core**: 配置 OPERATION_LOG_PATH_EXCLUDE

## 0.20.1 (2026-01-30)

### 🐛 问题修复

- **app/admin/monitor**: 修复健康检查路由未注册

## 0.20.0 (2026-01-30)

### ✨ 新功能

- **app/admin/monitor**: 新增健康检查端点

## 0.19.0 (2026-01-30)

### ⬆️ 依赖升级

- 升级项目依赖

## 0.18.2 (2026-01-30)

### 🐛 问题修复

- 修复 JWT 权限

## 0.18.1 (2026-01-30)

### 🐛 问题修复

- **app/admin**: 补充权限标识

## 0.18.0 (2026-01-30)

### ✨ 新功能

- **rbac**: 新增 rbac 权限标识校验, 补充校验方法

## 0.17.2 (2026-01-29)

### 🐛 问题修复

- **app/admin/user**: 修复校验菜单和部门存在性功能
- **app/admin/dept**: 修复校验该部门下是否有用户的功能
- **app/admin/user**: 修复校验部门和角色存在性功能

## 0.17.1 (2026-01-29)

### 🐛 问题修复

- **app/admin/auth**: 修复用户登录功能, 优化返回信息
- **common/security**: 修复 expire_time 转换的问题

## 0.17.0 (2026-01-29)

### ✨ 新功能

- **utils/timezone**: 新增将 datetime 对象转换为 UTC 时区 datetime 对象 工具方法
- **app/admin/user**: 新增更新用户登录时间方法
- **app/admin/login_log**: 新增登录日志记录业务模块
- **app/admin/auth**: 新增 swagger login 快捷方法

### 🐛 问题修复

- **app/admin/operation-log**: 修复记录操作日志的用户信息

## 0.16.0 (2026-01-29)

### ✨ 新功能

- **app/admin/auth**: 新增登录授权业务模块
- **middleware**: 新增 JWT 中间件

### 🐛 问题修复

- **app/admin/user**: 修复用户业务模块的问题

### 🔧 日常维护

- **.vscode**: 修复 vscode 通用配置

## 0.15.0 (2026-01-26)

### ✨ 新功能

- **middleware**: 新增操作日志记录中间件
- **app/admin/operation-log**: 新增操作日志模块
- **common/queue**: 新增批量从异步队列获取任务的功能

## 0.14.0 (2026-01-23)

### ✨ 新功能

- **app/admin/menu**: 新增系统菜单业务模块

## 0.13.0 (2026-01-23)

### ✨ 新功能

- **app/admin/role**: 新增系统角色业务模块

### 🔥 remove

- **app/admin/user**: 移除特殊筛选接口

## 0.12.0 (2026-01-23)

### ♻️ 代码重构

- **app/admin/user**: 重构代码: 使用 sqlalchemy , 移除 CRUDPlus 依赖

### ⬆️ 依赖升级

- 升级项目依赖

## 0.11.1 (2026-01-23)

### ♻️ 代码重构

- **app/admin/dept**: 重构代码: 使用 sqlalchemy , 移除 CRUDPlus 依赖

## 0.11.0 (2026-01-22)

### ♻️ 代码重构

- **app/admin/dept**: 重构系统部门业务模块

### ✨ 新功能

- **utils/validator**: 新增 LocalDatetime 本地时间序列化 Pydantic 类型

### 🐛 问题修复

- **app/admin/model**: 优化 Model 关联关系
- **app/admin/user**: 修复命名
- **app/admin/dept**: 修复批量更新部门状态的返回类型错误

### 🔥 remove

- **common/schema**: 移除 json_encoders 配置

## 0.10.0 (2026-01-21)

### ✨ 新功能

- **app/admin/dept**: 新增系统部门业务模块

### ⬆️ 依赖升级

- 升级项目依赖

### 🔥 remove

- **app/admin/user**: 移除 user_type 字段

## 0.9.0 (2026-01-08)

### ✨ 新功能

- **app/admin/user**: 新增系统用户业务模块
- **common/security**: 新增密码哈希/验证
- **common/schema**: 新增解决跨模块前向引用问题

### 🏗️ 构建相关

- **deps**: bump filelock from 3.20.0 to 3.20.1

### 🐛 问题修复

- **common/exception**: 新增异常处理日志记录
- **database/postgresql**: 修复导入 AsyncGenerator 的方式
- **app/admin/schema**: 修复 schema 前向引用问题, 类型问题
- **app/admin**: 修复导出角色部门关联表

### 🔧 日常维护

- 新增 pwdlib[bcrypt]
- 新增 pwdlib
- **ruff**: 更新 ruff 配置: schema/model/service/... 忽略 TC001/TC002/... 规则
- **.gitignore**: 更新 .gitignore

## 0.8.0 (2025-12-21)

### ✨ 新功能

- **app/admin**: 新增 Schema 模型
- **utils/validator**: 新增验证工具
- **common/schema**: 新增 SchemaBase 基础模型配置

### 🔧 日常维护

- **ruff**: 更新 ruff 配置: schema TC001, TC002
- **ruff**: 更新 ruff 配置: __init__.py 支持 F401, F403 规则

## 0.7.0 (2025-12-19)

### ♻️ 代码重构

- **app/admin**: 更新 model 文件名

### ✨ 新功能

- **app/admin**: 新增 SysLoginLog 登录日志表
- **app/admin**: 新增 SysOperationLog 操作日志表
- **app/admin**: 新增角色部门关联关系, 角色的数据范围
- **app/admin**: 新增 SysDept 部门表, 用户关联部门信息
- **app/admin**: 新增 Sysmenu 菜单表, sys_role_menu 关联关系表
- **app/admin**: 新增 SysRole 角色表, sys_user_role 关联关系表

### 🐛 问题修复

- **app/admin**: 更新菜单表的类型字段的设计
- **app/admin**: 修复 SysRole 角色表 status 的 comment

### 👷 CI/CD

- **.github**: 更新当前版本发布说明内容

### 🔥 remove

- **alembic**: 移除 alembic 记录, 开发阶段改动过大, 不再记录

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
