#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

password_hash = PasswordHash((BcryptHasher(),))


def get_hash_password(password: str, salt: bytes | None):
    """获取加密盐 加密后密码"""
    return password_hash.hash(password, salt=salt)
