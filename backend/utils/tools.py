#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tomllib


def get_project_version(pyproject_path: str = 'pyproject.toml') -> str:
    with open(pyproject_path, 'rb') as f:
        return tomllib.load(f)['project']['version']
