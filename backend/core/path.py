from pathlib import Path

# 根目录
ROOT_PATH = Path(__file__).resolve().parent.parent.parent

# 项目目录
BASE_PATH = ROOT_PATH / 'backend'

# 日志文件目录
LOG_DIR = ROOT_PATH / 'log'

# 静态资源目录
STATIC_DIR = ROOT_PATH / 'static'
IP2REGION_DIR = STATIC_DIR / 'ip2region'

# env 环境变量目录
ENV_DIR = ROOT_PATH / 'env'

# Alembic 版本文件目录
ALEMBIC_VERSION_DIR = BASE_PATH / 'alembic' / 'versions'

# 确保目录存在
for directory in [LOG_DIR, STATIC_DIR, ENV_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
