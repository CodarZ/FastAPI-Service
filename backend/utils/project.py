"""项目信息工具"""

import tomllib

from pathlib import Path

from backend.core.path import ROOT_PATH


def get_project_version() -> str:
    """从 pyproject.toml 读取项目版本号"""
    pyproject_toml_path = ROOT_PATH / 'pyproject.toml'
    if pyproject_toml_path.exists():
        with Path.open(pyproject_toml_path, 'rb') as f:
            data = tomllib.load(f)
            version = data.get('project', {}).get('version')

            print('version', version)
            if version:
                return version
    return '0.0.0'
