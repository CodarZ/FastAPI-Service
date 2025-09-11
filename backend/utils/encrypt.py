#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib

from os import urandom
from typing import Any

from cryptography.hazmat.backends.openssl import backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from itsdangerous import URLSafeSerializer

from backend.common.log import log


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
            plaintext = plaintext.encode('utf-8')

        iv = urandom(16)

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend)

        # 加密器对象
        encryptor = cipher.encryptor()

        # 使用 PKCS7 对明文进行填充
        padder = padding.PKCS7(cipher.algorithm.key_size).padder()
        # 填充后数据
        padded_plaintext = padder.update(plaintext) + padder.finalize()
        # 加密, 得到密文
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        # 返回 IV + 密文, 方便解密时使用
        return iv + ciphertext

    def decrypt(self, cipher_iv_text: bytes | str):
        """解密"""

        if isinstance(cipher_iv_text, bytes):
            ciphertext = cipher_iv_text

        if isinstance(cipher_iv_text, str):
            ciphertext = bytes.fromhex(cipher_iv_text)
        else:
            raise TypeError('AES 密文 ciphertext 必须为 bytes 或 str 类型')

        iv = ciphertext[:16]
        # 提取密文
        ciphertext = ciphertext[16:]

        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend)
        # 解密器对象
        decryptor = cipher.decryptor()
        # 填充器
        unpadder = padding.PKCS7(cipher.algorithm.key_size).unpadder()
        # 去除填充
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        # 解密, 得到明文
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext.decode('utf-8')


class SHA256Cipher:
    """SHA256 哈希器（安全级别）"""

    @staticmethod
    def encrypt(plaintext: bytes | str):
        sha256 = hashlib.sha256()

        if not isinstance(plaintext, bytes):
            plaintext = str(plaintext).encode('utf-8')

        sha256.update(plaintext)
        return sha256.hexdigest()


class MD5Cipher:
    """MD5 加密器（不安全级别）"""

    @staticmethod
    def encrypt(plaintext: bytes | str):
        md5 = hashlib.md5(usedforsecurity=False)

        if not isinstance(plaintext, bytes):
            plaintext = str(plaintext).encode('utf-8')

        md5.update(plaintext)
        return md5.hexdigest()


class ItsDCipher:
    """ItsDangerous 加密器, 备用 SHA256 加密"""

    def __init__(self, key: bytes | str):
        """初始化 ItsDangerous 加密器

        :param key: 密钥, 16/24/32 bytes 或 16 进制字符串
        :return:
        """
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
            return ciphertext
        except Exception as e:
            log.warning(f'ItsDangerous 加密失败，使用 SHA256 加密: {e}')
            ciphertext = SHA256Cipher.encrypt(plaintext)
        return ciphertext

    def decrypt(self, ciphertext: str):
        """解密"""

        serializer = URLSafeSerializer(self.key)
        try:
            plaintext = serializer.loads(ciphertext)
            return plaintext
        except Exception as e:
            log.error(f'ItsDangerous 解密失败, 返回可能是 SHA256 加密的数据: {e}')
            plaintext = ciphertext
        return plaintext
