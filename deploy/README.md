# Docker 部署指南

本项目提供了基于 Docker 的部署方案，使用 uv 包管理器和 Granian ASGI 服务器。

## 📁 文件说明

```text
deploy/
├── Dockerfile             # Dockerfile（多阶段构建 + 非 root 用户）
├── Jenkinsfile            # Jenkins CI/CD 配置文件
└── README.md              # 本文档
```

## 🚀 部署方式

### 方式一：Jenkins 自动化部署（推荐）

使用 Jenkins Pipeline 实现自动化构建和部署。

#### 1. 环境变量配置

修改 `Jenkinsfile` 中的 `WORKSPACE_PATH`：

```groovy
environment {
    WORKSPACE_PATH = "/home/ubuntu/docker/fs-service"  // 根据实际路径修改
}
```

#### 2. 环境准备

在宿主机上创建项目目录：

```bash
# 根据 WORKSPACE_PATH 在宿主机创建项目目录结构
sudo mkdir -p /home/ubuntu/docker/fs-service/{log,static/upload,env}

# 复制环境配置文件、或者手动创建 env 文件
sudo cp env/.env* /home/ubuntu/docker/fs-service/env/

# 设置权限
sudo chown -R $USER:$USER /home/ubuntu/docker/fs-service
sudo chmod -R 755 /home/ubuntu/docker/fs-service
```

#### 3. 配置 Jenkins

1. **创建 Multibranch Pipeline**：
   - Repository URL: `https://github.com/CodarZ/fastapi-service.git`
   - Script Path: `deploy/Jenkinsfile`

2. **配置分支策略**：
   - `master` 分支 → 生产环境（端口 9091）
   - `test` 分支 → 测试环境（端口 9092）
   - `develop` 分支 → 开发环境（端口 9093）

#### 4. 触发构建

推送代码到对应分支，Jenkins 会自动：

1. 检出代码
2. 构建 Docker 镜像
3. 停止旧容器
4. 启动新容器
5. 执行健康检查
6. 清理旧镜像（仅保留最近 3 个构建版本）

#### 5. 访问服务

| 环境 | 端口 | API 文档地址 |
|------|------|-------------|
| 生产环境 | 9091 | `http://[your-url]:9091/[FASTAPI_DOCS_URL]` |
| 测试环境 | 9092 | `http://[your-url]:9092/[FASTAPI_DOCS_URL]` |
| 开发环境 | 9093 | `http://[your-url]:9093/[FASTAPI_DOCS_URL]` |

### 方式二：手动构建并运行

#### 1. 构建镜像

```bash
docker build -f deploy/Dockerfile -t fastapi-service:latest .
```

#### 2. 运行容器

```bash
docker run -d \
  --name fastapi-service \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  -e DB_USER=fastapi \
  -e DB_PASSWORD=your-password \
  -e DB_DATABASE=fastapi-services \
  -e REDIS_HOST=host.docker.internal \
  -e REDIS_PORT=6379 \
  -e REDIS_PASSWORD=your-password \
  -v $(pwd)/log:/app/log \
  -v $(pwd)/static/upload:/app/static/upload \
  -v $(pwd)/env:/app/env \
  fastapi-service:latest
```

> **注意**：如果数据库和 Redis 在宿主机上运行，使用 `host.docker.internal` 作为主机名（macOS/Windows）。Linux 系统需要添加 `--add-host=host.docker.internal:host-gateway` 参数。

#### 3. 访问服务

- API 文档：<http://[your-url]:8000/[FASTAPI_DOCS_URL]>

### 方式二：使用外部数据库和 Redis

如果你的数据库和 Redis 运行在独立的容器或服务器上：

```bash
docker run -d \
  --name fastapi-service \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e DB_HOST=your-postgres-host \
  -e DB_PORT=5432 \
  -e DB_USER=fastapi \
  -e DB_PASSWORD=your-db-password \
  -e DB_DATABASE=fastapi-services \
  -e REDIS_HOST=your-redis-host \
  -e REDIS_PORT=6379 \
  -e REDIS_PASSWORD=your-redis-password \
  -e TOKEN_SECRET_KEY=your-secret-key \
  -v $(pwd)/log:/app/log \
  -v $(pwd)/static/upload:/app/static/upload \
  fastapi-service:latest
```

## 📋 环境变量配置

环境变量可以通过两种方式配置：

1. **挂载 `env/` 目录**：将项目的 `env/` 目录挂载到容器的 `/app/env`，应用会自动读取 `.env.production` 等配置文件（`.env.*.local` 文件仅用于本地开发）
2. **Docker 命令传递**：使用 `-e` 参数传递环境变量，会覆盖配置文件中的同名变量

> **优先级**：`docker run -e` > `env/.env.*.local` > `env/.env.*` > `env/.env` > 默认值

### 必需环境变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `ENVIRONMENT` | 运行环境 | `production` |
| `DB_HOST` | PostgreSQL 主机 | `host.docker.internal` |
| `DB_PORT` | PostgreSQL 端口 | `5432` |
| `DB_USER` | 数据库用户名 | `fastapi` |
| `DB_PASSWORD` | 数据库密码 | `your-password` |
| `DB_DATABASE` | 数据库名称 | `fastapi-services` |
| `REDIS_HOST` | Redis 主机 | `host.docker.internal` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `REDIS_PASSWORD` | Redis 密码 | `your-password` |

### 可选环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `TOKEN_SECRET_KEY` | JWT 密钥 | 自动生成 |
| `OPERATION_LOG_ENCRYPT_SECRET_KEY` | 操作日志加密密钥 | 自动生成 |
| `GRANIAN_WORKERS` | Worker 进程数量，详见下文 | `4` |

## 🔧 技术特性

### 使用 uv 包管理器

本项目使用 [uv](https://github.com/astral-sh/uv) 作为包管理器，具有以下优势：

- ⚡ **极速安装**：比 pip 快 10-100 倍
- 📦 **依赖锁定**：通过 `pyproject.toml` 和 `uv.lock` 确保一致性
- 🎯 **精确构建**：多阶段构建减小镜像体积
- 💾 **缓存优化**：使用 Docker 缓存加速重复构建

### Dockerfile 特性

- **多阶段构建**：构建阶段安装依赖，运行阶段只保留必需文件，镜像更小
- **只包含生产依赖**：使用 `uv sync --frozen --no-dev`，不安装开发和测试依赖
- **非 root 用户运行**：使用 `appuser` 用户运行应用，提升安全性
- **预编译字节码**：`UV_COMPILE_BYTECODE=1` 提升启动性能
- **国内镜像加速**：使用中科大镜像源加速构建

### Granian 服务器

使用 [Granian](https://github.com/emmett-framework/granian) 作为 ASGI 服务器：

- 🚀 基于 Rust 实现，性能优异
- 🔄 支持热重载（开发环境）
- 🔀 内置负载均衡
- 📊 默认配置 4 个 worker 进程

## 📊 性能优化

### Worker 配置

默认使用 4 个 worker 进程。可以通过环境变量根据 CPU 核心数调整：

**推荐配置**：`worker数 = CPU核心数 × 2 + 1`

#### 使用示例

```bash
# 高性能配置（16 workers）
docker run -d \
  --name fastapi-service \
  -p 8000:8000 \
  -e GRANIAN_WORKERS=16 \
  --memory="4g" \
  --cpus="8" \
  fastapi-service:latest
```

#### 不同场景推荐值

| CPU 核心数 | 推荐 Worker 数 | 内存需求 |
|-----------|--------------|---------|
| 1 核 | 2-3 | ~400MB |
| 2 核 | 4-5 | ~800MB |
| 4 核 | 8-9 | ~1.6GB |
| 8 核 | 16-17 | ~3.2GB |

### 镜像大小

- **最终镜像**: ~180MB（仅包含运行时依赖，不含开发工具）

## �️ 常用命令

### Docker 相关

```bash
# 查看运行中的容器（按环境）
docker ps -f name=fs-container-production
docker ps -f name=fs-container-test
docker ps -f name=fs-container-development

# 查看容器日志
docker logs fs-container-production
docker logs -f --tail 100 fs-container-test  # 实时查看最后 100 行

# 停止容器
docker stop fs-container-production

# 删除容器
docker rm fs-container-production

# 查看镜像
docker images fastapi-service

# 查看特定环境的所有镜像版本
docker images fastapi-service --format "{{.Tag}}" | grep production

# 手动清理旧镜像（保留最近 3 个）
docker images fastapi-service --format "{{.Tag}}" | \
  grep "production-" | \
  sort -t'-' -k2 -n -r | \
  tail -n +4 | \
  xargs -r -I {} docker rmi fastapi-service:{}

# 回滚到指定构建版本
docker stop fs-container-production
docker rm fs-container-production
docker run -d \
  --name fs-container-production \
  --restart unless-stopped \
  -p 9091:8000 \
  -v /home/ubuntu/docker/fs-service/log:/app/log \
  -v /home/ubuntu/docker/fs-service/static/upload:/app/static/upload \
  -v /home/ubuntu/docker/fs-service/env:/app/env \
  -e ENVIRONMENT=production \
  -e GRANIAN_WORKERS=4 \
  fastapi-service:production-123  # 指定构建号
```

### 查看日志

```bash
# 实时日志
docker logs -f fastapi-service

# 最近 100 行日志
docker logs --tail 100 fastapi-service
```

### 进入容器

```bash
docker exec -it fastapi-service bash
```

### 查看资源使用

```bash
docker stats fastapi-service
```

### 重启容器

```bash
docker restart fastapi-service
```

### 停止并删除容器

```bash
docker stop fastapi-service
docker rm fastapi-service
```

## 🔐 安全建议

### 生产环境检查清单

- [ ] 修改所有默认密码和密钥
- [ ] 设置环境变量 `TOKEN_SECRET_KEY`
- [ ] 设置环境变量 `OPERATION_LOG_ENCRYPT_SECRET_KEY`
- [ ] 使用 HTTPS（配置 Nginx SSL）
- [ ] 限制容器资源使用（CPU、内存）
- [ ] 配置日志轮转
- [ ] 设置自动备份
- [ ] 配置监控和告警

## 🐛 故障排查

### Jenkins 部署故障

#### 构建失败

```bash
# 查看 Jenkins 构建日志
# 在 Jenkins 界面查看具体的错误信息

# 检查 Docker 环境
docker --version
docker ps
docker images

# 检查磁盘空间
df -h

# 手动清理 Docker 资源
docker system prune -a -f
```

#### 容器无法启动

```bash
# 查看容器状态
docker ps -a -f name=fs-container-production

# 查看容器日志
docker logs fs-container-production

# 检查环境变量文件
ls -la /home/ubuntu/docker/fs-service/env/
cat /home/ubuntu/docker/fs-service/env/.env.production

# 检查目录权限
ls -la /home/ubuntu/docker/fs-service/
```

#### 健康检查失败

```bash
# 检查容器是否运行
docker ps -f name=fs-container-production

# 查看容器日志
docker logs --tail 50 fs-container-production

# 手动测试 API
curl -f http://[your-url]:9091/[FASTAPI_DOCS_URL]

# 进入容器检查
docker exec -it fs-container-production bash
# 在容器内
curl http://[your-url]:8000/[FASTAPI_DOCS_URL]
```

#### 端口冲突

```bash
# 检查端口占用
sudo lsof -i :9091
sudo netstat -tulpn | grep 9091

# 停止占用端口的进程
sudo kill -9 <PID>
```

#### 回滚到旧版本

```bash
# 查看可用的镜像版本
docker images fastapi-service

# 停止当前容器
docker stop fs-container-production
docker rm fs-container-production

# 启动旧版本容器
docker run -d \
  --name fs-container-production \
  --restart unless-stopped \
  -p 9091:8000 \
  -v /home/ubuntu/docker/fs-service/log:/app/log \
  -v /home/ubuntu/docker/fs-service/static/upload:/app/static/upload \
  -v /home/ubuntu/docker/fs-service/env:/app/env \
  -e ENVIRONMENT=production \
  -e GRANIAN_WORKERS=4 \
  fastapi-service:production-122  # 使用旧的构建号
```

### 手动部署故障

#### 应用启动问题

1. 检查环境变量配置
2. 查看容器日志：`docker logs fastapi-service`
3. 确认数据库和 Redis 服务可访问

### 数据库连接失败

```bash
# 测试数据库连接
docker exec fastapi-service python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect(
        host='your-host',
        port=5432,
        user='fastapi',
        password='your-password',
        database='fastapi-services'
    )
    print('Database connected successfully')
    await conn.close()
asyncio.run(test())
"
```

### Redis 连接失败

```bash
# 测试 Redis 连接（如果 Redis 在容器中）
docker exec your-redis-container redis-cli -a your-password ping
```

#### API 健康检查问题

```bash
# 检查健康状态
docker inspect --format='{{.State.Health.Status}}' fastapi-service

# 查看健康检查日志
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' fastapi-service
```

## 📚 相关资源

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [uv 文档](https://docs.astral.sh/uv/)
- [Granian 文档](https://github.com/emmett-framework/granian)
- [Docker 官方文档](https://docs.docker.com/)
- [Jenkins Pipeline 语法](https://www.jenkins.io/doc/book/pipeline/syntax/)

## 🆘 获取帮助

如遇到问题，请：

1. 查看容器日志
2. 检查环境变量配置
3. 确认网络连接
4. 参考故障排查部分
