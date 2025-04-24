#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import string
import time

from uuid import uuid4


def generate_random_str(prefix: str):
    """生成不易重复的随机字符串"""

    timestamp = str(int(time.time() * 1000))[-1:]

    uuid_chars = uuid4().hex[:6]

    random_chars = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    return f'{prefix}{random_chars}{timestamp}{uuid_chars}'
