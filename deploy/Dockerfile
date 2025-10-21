# 多阶段构建 - 使用 uv 优化生产镜像
# === 构建阶段 ===
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# 安装构建依赖
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

WORKDIR /app

# 配置 uv 环境变量
ENV UV_COMPILE_BYTECODE=1 \
    UV_NO_CACHE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/usr/local

# 使用缓存安装依赖
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# === 运行时镜像 ===
FROM python:3.13-slim

# 更换为国内镜像源并安装运行时依赖
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources \
    && apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制项目文件和依赖
COPY --from=builder /app /app
COPY --from=builder /usr/local /usr/local

WORKDIR /app/backend

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=development \
    GRANIAN_WORKERS=4

# 创建必要的目录并设置权限
RUN mkdir -p /app/log /app/env /app/static/upload && \
    chmod -R 755 /app

# 创建非 root 用户
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1001 appuser && \
    chown -R appuser:appuser /app

# 切换到非 root 用户
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令（使用 shell 形式以支持环境变量）
CMD /usr/local/bin/granian main:app --interface asgi --host 0.0.0.0 --port 8000 --workers ${GRANIAN_WORKERS}
