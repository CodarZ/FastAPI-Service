# ========= 构建 ==============
FROM python:3.14-slim AS builder

# 环境变量配置
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# 安装 uv 包管理器
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

# 复制依赖描述文件
COPY pyproject.toml uv.lock ./

# 安装依赖并清理缓存
RUN uv sync --frozen --no-dev --no-install-project && \
    rm -rf /root/.cache/uv

# 复制源码和资源
COPY backend ./backend
COPY alembic.ini ./
COPY static ./static
COPY env ./env

# 安装项目本身并清理
RUN uv sync --frozen --no-dev && \
    find /app/.venv -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /app/.venv -type f -name "*.pyc" -delete 2>/dev/null || true

# ========= 运行 ==============
FROM python:3.14-slim AS runtime

WORKDIR /app

# 安装必要的系统工具
RUN apt-get update && apt-get install -y --no-install-recommends \
    adduser \
    && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN addgroup --gid 1000 appgroup && \
    adduser --uid 1000 --gid 1000 --shell /bin/bash --disabled-password --gecos "" appuser

# ========= 从构建阶段复制虚拟环境、源代码、静态资源 ==============
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app/backend /app/backend
COPY --from=builder --chown=appuser:appgroup /app/alembic.ini /app/alembic.ini
COPY --from=builder --chown=appuser:appgroup /app/static /app/static
COPY --from=builder --chown=appuser:appgroup /app/env /app/env

# 配置环境变量
ENV PATH="/app/.venv/bin:$PATH" ENV_DIR="/app/env" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 创建目录并清理
RUN mkdir -p /app/log && \
    chown -R appuser:appgroup /app && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/monitor/health')" || exit 1

# 启动命令
CMD ["granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8000", "backend.main:app"]
