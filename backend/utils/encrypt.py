#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import hashlib

from os import urandom
from typing import Any

from cryptography.hazmat.backends.openssl import backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from itsdangerous import URLSafeSerializer

from backend.common.logger import log


class AESCipher:
    """AES 加密器"""

    def __init__(self, key: bytes | str):
        if isinstance(key, bytes):
            self.key = key
        elif isinstance(key, str):
            self.key = bytes.fromhex(key)
        else:
            raise TypeError('AES 加密 key 必须为 bytes 或 str 类型')

    def encrypt(self, plaintext: bytes | str):
        """加密"""
        if not isinstance(plaintext, (bytes, str)):
            raise TypeError('AES 加密明文必须为 bytes 或 str 类型')
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')  # 将字符串转换为字节数据

        iv = urandom(16)
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend,
        )
        encryptor = cipher.encryptor()  # 加密器对象

        padder = padding.PKCS7(128).padder()  # 使用 PKCS7 对明文进行填充（AES 块大小为 128 bit）
        padded_plaintext = padder.update(plaintext) + padder.finalize()  # 填充
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()  # 密文
        return iv + ciphertext  # 返回 IV + 密文，方便解密时使用

    def decrypt(self, cipher_iv_text: bytes | str):
        """解密"""
        if isinstance(cipher_iv_text, bytes):
            ciphertext = cipher_iv_text
        elif isinstance(cipher_iv_text, str):
            ciphertext = bytes.fromhex(cipher_iv_text)
        else:
            raise TypeError('AES 密文 ciphertext 必须为 bytes 或 str 类型')

        iv = ciphertext[:16]
        ciphertext = ciphertext[16:]  # 提取 密文
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=backend,
        )

        decryptor = cipher.decryptor()  # 解密器对象

        unpadder = padding.PKCS7(128).unpadder()  # 填充器
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()  # 解密数据
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()  # 去除填充并还原明文

        return plaintext.decode('utf-8')


class MD5Cipher:
    """MD5 加密器"""

    @staticmethod
    def encrypt(plaintext: bytes | str):
        """加密"""
        md5 = hashlib.md5()

        if not isinstance(plaintext, (bytes, str)):
            raise TypeError('MD5 加密明文必须为 bytes 或 str 类型')

        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')

        md5.update(plaintext)
        return md5.hexdigest()


class ItsmCipher:
    """Itsdangerous 加密"""

    def __init__(self, key: bytes | str):
        if isinstance(key, bytes):
            self.key = key
        elif isinstance(key, str):
            self.key = bytes.fromhex(key)
        else:
            raise TypeError('Itsdangerous 加密 key 必须为 bytes 或 str 类型')

    def encrypt(self, plaintext: Any):
        """加密"""
        serializer = URLSafeSerializer(self.key)
        try:
            ciphertext = serializer.dumps(plaintext)
        except Exception as e:
            log.warning(f'Itsdangerous 加密失败, 使用 MD5 加密: {e}')
            ciphertext = MD5Cipher.encrypt(plaintext)
        return ciphertext

    def decrypt(self, ciphertext: str):
        """解密"""
        serializer = URLSafeSerializer(self.key)
        try:
            plaintext = serializer.loads(ciphertext)
        except Exception as e:
            log.warning(f'ItsDangerous 解密失败，返回可能是 MD5 加密的数据: {e}')
            plaintext = ciphertext
        return plaintext
