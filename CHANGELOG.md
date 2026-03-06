# Changelog

## [1.4.0](https://github.com/CodarZ/FastAPI-Service/compare/v1.3.0...v1.4.0) (2026-03-06)


### ✨ 新功能

* **middleware:** 新增请求访问信息中间件 `AccessMiddleware` ([2c6b627](https://github.com/CodarZ/FastAPI-Service/commit/2c6b627af687f1279735f337004587ee426c471a))
* **utils/timezone:** 增加时区处理工具类 ([3a73652](https://github.com/CodarZ/FastAPI-Service/commit/3a73652c16add47a1892b9bf279060dbf864097a))


### 📦 依赖更新

* 新增依赖 python-dateutil ([72818da](https://github.com/CodarZ/FastAPI-Service/commit/72818da9d584793eff4b41576c41219570edbb97))

## [1.3.0](https://github.com/CodarZ/FastAPI-Service/compare/v1.2.0...v1.3.0) (2026-03-06)


### ✨ 新功能

* **common/request:** 新增 User-Agent 解析 ([042ad51](https://github.com/CodarZ/FastAPI-Service/commit/042ad517978aaf08e010aa9946c24348d72532eb))
* **middleware:** 新增请求状态信息中间件 `StateMiddleware` ([faf0d4e](https://github.com/CodarZ/FastAPI-Service/commit/faf0d4eb5c722002ecd6a8f59db796a0737df94c))


### ♻️ 重构

* **common/request:** 提取 UserAgentInfo 数据类重构 User-Agent 上下文 ([93c2fd5](https://github.com/CodarZ/FastAPI-Service/commit/93c2fd5496c5db581537623d47bc785a964fe282))

## [1.2.0](https://github.com/CodarZ/FastAPI-Service/compare/v1.1.0...v1.2.0) (2026-03-05)


### ✨ 新功能

* **common/log:** 新增基于 loguru 的自定义日志系统并集成中间件 ([8218a91](https://github.com/CodarZ/FastAPI-Service/commit/8218a91958c038ff2b20de524b699913ca9fa309))
* **common/request:** 新增请求上下文信息 ([bfceeac](https://github.com/CodarZ/FastAPI-Service/commit/bfceeac559f5190daee8983ab250e648725d7cfd))


### 📦 依赖更新

* 升级依赖 ([cab75e6](https://github.com/CodarZ/FastAPI-Service/commit/cab75e6c3dc19c2bff82620a093c4f906c64d757))

## [1.1.0](https://github.com/CodarZ/FastAPI-Service/compare/v1.0.0...v1.1.0) (2026-02-28)


### ✨ 新功能

* 新增项目核心配置变量信息, 并注册 FastAPI 实例 ([1edf1e8](https://github.com/CodarZ/FastAPI-Service/commit/1edf1e8bd7b9036fb25814e2defc227f9b05ac14))


### 👷 CI/CD

* 根据提交信息，自动化发布 ([55a89f1](https://github.com/CodarZ/FastAPI-Service/commit/55a89f1159a05a43925e63db7cf99b76c2346e1b))


### 🛠 其他

* 新增 cz commit 提交信息规范 ([a923a13](https://github.com/CodarZ/FastAPI-Service/commit/a923a131c451bea8297655e8de2c4f609b71aa7f))
* 新增 docstring 格式检查 ([0e90a76](https://github.com/CodarZ/FastAPI-Service/commit/0e90a76bbf9d12362ea8de6a100e001acf1e8f7d))
* 新增 ruff 配置 ([7a5cd14](https://github.com/CodarZ/FastAPI-Service/commit/7a5cd1480e2a27ea98aae782e54572168aab65b4))
* 更新 release-please 配置 ([9dc75e0](https://github.com/CodarZ/FastAPI-Service/commit/9dc75e003758ad47914e57445eec8bd310ffe479))
