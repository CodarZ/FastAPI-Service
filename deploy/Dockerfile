# 使用带有基础环境的自构建镜像
FROM fs-image:base

# 复制代码
COPY . /app

# 使用 uv 安装项目依赖
RUN uv pip install --system --no-cache -r requirements.txt

# 启动 FastAPI 应用
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
