"""加密工具模块

- AESCipher    ：对称加密（AES-GCM）, 可解密, 适合短文本 / JSON 等敏感数据（手机号、邮箱、身份证号等）。
- SHA256Cipher ：不可逆摘要（SHA-256）, 适合密码、敏感标识等"只需校验, 不需还原"的场景。
- MD5Cipher    ：不可逆摘要（MD5）, 主要用于兼容老系统或文件完整性校验, *不推荐用于安全场景*。
- ItsDCipher   ：itsdangerous 签名序列化, 适合生成带过期时间的 URL Token、一次性链接参数等。
"""

import base64
import hashlib
import json
import os
import pathlib
import secrets

from typing import Any, TypeVar

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

T = TypeVar('T')
# 可加密的原始数据类型：bytes、str、dict（自动序列化为 JSON）
Plaintext = bytes | str | dict


def _normalize_input(plaintext: Plaintext) -> bytes:
    """统一将输入转换为 bytes

    - bytes: 直接返回
    - str: UTF-8 编码
    - dict: JSON 序列化后 UTF-8 编码

    """
    if isinstance(plaintext, bytes):
        return plaintext
    if isinstance(plaintext, str):
        return plaintext.encode('utf-8')
    if isinstance(plaintext, dict):
        # 使用 ensure_ascii=False 保留中文等 Unicode 字符
        # separators 去除多余空格, 减小体积
        return json.dumps(plaintext, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    raise TypeError(f'不支持的输入类型: {type(plaintext).__name__}, 只支持 bytes | str | dict')


class AESCipher:
    """AES-GCM 对称加密器

    使用场景
    --------
    - 需要加密且后续能还原的敏感数据
    - 用户隐私信息：手机号、邮箱、身份证号、银行卡号等
    - API 响应中需要隐藏但客户端需要使用的字段
    - 数据库字段级加密

    技术特性
    --------
    - 算法：AES-256-GCM（Galois/Counter Mode）
    - 密钥长度：256 位（32 字节）
    - Nonce：96 位（12 字节）, 每次加密随机生成
    - 认证标签：128 位, 提供完整性校验
    - 输出格式：base64(nonce + ciphertext + tag)

    安全说明
    --------
    - GCM 模式同时提供加密和认证, 防止篡改
    - 每次加密使用随机 nonce, 相同明文产生不同密文
    - 密钥泄露将导致所有数据可被解密, 请妥善保管

    示例
    ----
    ```python
    cipher = AESCipher(key='my-secret-key-32-bytes-long!!!!!')
    encrypted = cipher.encrypt('13812345678')
    decrypted = cipher.decrypt(encrypted)  # -> "13812345678"

    # 加密 dict（自动 JSON 序列化）
    encrypted = cipher.encrypt({'phone': '13812345678', 'email': 'test@example.com'})
    data = cipher.decrypt(encrypted, return_type=dict)  # -> {"phone": "...", "email": "..."}
    ```
    """

    KEY_LENGTH = 32  # AES-256 密钥长度（字节）
    NONCE_LENGTH = 12  # GCM 推荐使用 12 字节 nonce

    def __init__(self, key: str | bytes) -> None:
        """初始化 AES 加密器

        Args:
            key: 加密密钥, 必须恰好为 32 字节（256 位）
                 - str: 必须是 32 个 ASCII 字符
                 - bytes: 必须恰好为 32 字节

        Raises:
            ValueError: 密钥长度不是 32 字节时抛出

        示例:
        ```
        cipher = AESCipher('12345678901234567890123456789012')  # 32 字符
        cipher = AESCipher(b'12345678901234567890123456789012')  # 32 字节
        ```
        """
        self._key = self._validate_key(key)
        self._aesgcm = AESGCM(self._key)

    def _validate_key(self, key: str | bytes) -> bytes:
        """验证秘钥并转换为 bytes"""
        if isinstance(key, str):
            key_bytes = key.encode('utf-8')
            if len(key_bytes) != self.KEY_LENGTH:
                raise ValueError(
                    f'字符串密钥编码后必须为 {self.KEY_LENGTH} 字节, '
                    f'当前: {len(key_bytes)} 字节（请使用 32 个 ASCII 字符）'
                )
            return key_bytes
        if isinstance(key, bytes):
            if len(key) != self.KEY_LENGTH:
                raise ValueError(f'bytes 密钥必须为 {self.KEY_LENGTH} 字节, 当前: {len(key)} 字节')
            return key
        raise TypeError(f'密钥类型必须为 str 或 bytes, 当前: {type(key).__name__}')

    def encrypt(self, plaintext: Plaintext) -> str:
        """加密数据

        使用随机 nonce 进行 AES-GCM 加密, 输出格式为 base64(nonce + ciphertext + tag)
        """
        data = _normalize_input(plaintext)
        # 每次加密生成新的随机 nonce, 确保相同明文产生不同密文
        nonce = os.urandom(self.NONCE_LENGTH)
        # AESGCM.encrypt 返回 ciphertext + tag
        ciphertext_with_tag = self._aesgcm.encrypt(nonce, data, associated_data=None)
        # 拼接 nonce 和密文, 便于解密时提取
        combined = nonce + ciphertext_with_tag
        return base64.urlsafe_b64encode(combined).decode('ascii')

    def decrypt(
        self,
        ciphertext: str,
        *,
        return_type: type[T] | None = None,
    ) -> str | bytes | T:
        """解密数据

        从 Base64 编码的密文中提取 nonce 和加密数据, 进行 AES-GCM 解密。

        Args:
            ciphertext: Base64 编码的加密字符串
            return_type: 期望的返回类型
                - None: 默认返回 str
                - bytes: 返回原始字节
                - dict: 自动进行 JSON 反序列化

        Returns:
            解密后的数据, 类型由 return_type 参数决定

        Raises:
            ValueError: 密文格式错误或解密失败（数据被篡改）
        """
        try:
            combined = base64.urlsafe_b64decode(ciphertext.encode('ascii'))
        except Exception as e:
            raise ValueError(f'密文 Base64 解码失败: {e}') from e

        if len(combined) < self.NONCE_LENGTH + 16:  # 至少需要 nonce + tag
            raise ValueError('密文长度不足, 格式错误')

        nonce = combined[: self.NONCE_LENGTH]
        ciphertext_with_tag = combined[self.NONCE_LENGTH :]

        try:
            decrypted = self._aesgcm.decrypt(nonce, ciphertext_with_tag, associated_data=None)
        except Exception as e:
            raise ValueError(f'解密失败, 可能密文已损坏或密钥错误: {e}') from e

        # 根据期望类型返回
        if return_type is bytes:
            return decrypted
        if return_type is dict:
            try:
                return json.loads(decrypted.decode('utf-8'))
            except json.JSONDecodeError as e:
                raise ValueError(f'JSON 反序列化失败: {e}') from e

        # 默认返回 str
        return decrypted.decode('utf-8')

    def encrypt_to_hex(self, plaintext: Plaintext) -> str:
        """加密数据并返回 hex 编码（替代 Base64）

        某些场景下 hex 编码更便于处理（如日志、URL 参数等）。
        """
        data = _normalize_input(plaintext)
        nonce = os.urandom(self.NONCE_LENGTH)
        ciphertext_with_tag = self._aesgcm.encrypt(nonce, data, associated_data=None)
        combined = nonce + ciphertext_with_tag
        return combined.hex()

    def decrypt_from_hex(
        self,
        ciphertext_hex: str,
        *,
        return_type: type[T] | None = None,
    ) -> str | bytes | T:
        """从 hex 编码的密文解密"""
        try:
            combined = bytes.fromhex(ciphertext_hex)
        except ValueError as e:
            raise ValueError(f'密文 Hex 解码失败: {e}') from e

        if len(combined) < self.NONCE_LENGTH + 16:
            raise ValueError('密文长度不足, 格式错误')

        nonce = combined[: self.NONCE_LENGTH]
        ciphertext_with_tag = combined[self.NONCE_LENGTH :]

        try:
            decrypted = self._aesgcm.decrypt(nonce, ciphertext_with_tag, associated_data=None)
        except Exception as e:
            raise ValueError(f'解密失败: {e}') from e

        if return_type is bytes:
            return decrypted
        if return_type is dict:
            return json.loads(decrypted.decode('utf-8'))
        return decrypted.decode('utf-8')


class SHA256Cipher:
    """SHA-256 摘要器（带盐值）

    使用场景
    --------
    - 敏感标识的脱敏存储（如设备指纹、API Key 等）
    - 需要校验但不需还原的数据

    技术特性
    --------
    - 算法：SHA-256（256 位摘要）
    - 盐值：16 字节随机生成, 每次 hash 不同
    - 迭代：支持多轮迭代增强安全性（默认 1 轮, 密码场景建议 100000+）
    - 输出格式：base64(salt + hash)

    安全说明
    --------
    - 单纯的 SHA-256 对密码存储来说偏弱
    - 本类增加了随机盐值, 可有效防止彩虹表攻击
    - iterations 哈希迭代次数, 可增加暴力破解难度

    示例
    ----
    ```python
    sha256_cipher = SHA256Cipher(iterations=100000)  # 密码场景建议高迭代
    hashed = sha256_cipher.encrypt('password123')
    sha256_cipher.verify('password123', hashed)  # -> True
    ```
    """

    SALT_LENGTH = 16  # 加密盐长度
    HASH_LENGTH = 32  # SHA-256 输出 32 字节

    def __init__(self, iterations: int = 1) -> None:
        """初始化 SHA256 摘要器

        Args:
            iterations: 哈希迭代次数, 密码存储建议 100000+, 普通校验用 1
        """
        if iterations < 1:
            iterations = 1
        self._iterations = iterations

    def encrypt(self, plaintext: Plaintext) -> str:
        """计算摘要

        生成随机盐值, 进行多轮 SHA-256 迭代, 返回 base64(salt + hash)。
        """
        data = _normalize_input(plaintext)
        salt = os.urandom(self.SALT_LENGTH)
        digest = self._compute_hash(data, salt)
        combined = salt + digest
        return base64.urlsafe_b64encode(combined).decode('ascii')

    def _compute_hash(self, data: bytes, salt: bytes) -> bytes:
        """执行带盐的迭代哈希

        Args:
            data: 原始数据
            salt: 盐值

        Returns:
            bytes: 哈希结果
        """
        # 首轮：data + salt
        digest = hashlib.sha256(data + salt).digest()
        # 后续迭代
        for _ in range(self._iterations - 1):
            digest = hashlib.sha256(digest + salt).digest()
        return digest

    def verify(self, plaintext: Plaintext, hashed: str) -> bool:
        """校验数据与摘要是否匹配

        从存储的摘要中提取盐值, 重新计算哈希并比对。
        """
        try:
            combined = base64.urlsafe_b64decode(hashed.encode('ascii'))
        except Exception:
            return False

        if len(combined) != self.SALT_LENGTH + self.HASH_LENGTH:
            return False

        salt = combined[: self.SALT_LENGTH]
        stored_hash = combined[self.SALT_LENGTH :]
        data = _normalize_input(plaintext)
        computed_hash = self._compute_hash(data, salt)

        # 使用 secrets.compare_digest 防止时序攻击
        return secrets.compare_digest(stored_hash, computed_hash)

    def hash_without_salt(self, plaintext: Plaintext) -> str:
        """计算不带盐的纯 SHA-256 摘要

        适用于需要确定性输出的场景（如文件校验、缓存键等）。

        警告：不带盐的哈希容易受彩虹表攻击, 不适合密码存储！

        Returns:
            str: Hex 编码的 SHA-256 摘要
        """
        data = _normalize_input(plaintext)
        return hashlib.sha256(data).hexdigest()


class MD5Cipher:
    """MD5 摘要器

    使用场景
    --------
    - 文件完整性校验（下载校验、缓存失效判断等）
    - 兼容老系统的接口签名
    - 生成非安全性要求的唯一标识（如缓存键）

    警告
    ----
    MD5 已被证明存在碰撞漏洞, **不应用于任何安全场景**！
    包括但不限于：密码存储、数字签名、证书校验等。
    安全场景请使用 SHA256Cipher 或更强的算法。

    技术特性
    --------
    - 算法：MD5（128 位摘要）
    - 输出：32 字符 hex 字符串

    示例
    ----
    ```python
    cipher = MD5Cipher()
    checksum = cipher.encrypt(file_content)
    cipher.verify(downloaded_content, checksum)  # -> True/False
    # 生成缓存键
    cache_key = cipher.encrypt({'user_id': 123, 'params': {...}})
    ```
    """

    def encrypt(self, plaintext: Plaintext) -> str:
        """计算 MD5 摘要"""
        data = _normalize_input(plaintext)
        return hashlib.md5(data).hexdigest()

    def verify(self, plaintext: Plaintext, checksum: str) -> bool:
        """校验数据与 MD5 摘要是否匹配"""
        computed = self.encrypt(plaintext)
        # 使用 secrets.compare_digest 防止时序攻击
        return secrets.compare_digest(computed.lower(), checksum.lower())

    def encrypt_file(self, file_path: str, chunk_size: int = 8192) -> str:
        """计算文件的 MD5 摘要"""
        md5_hash = hashlib.md5()
        with pathlib.Path(file_path).open('rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()

    def verify_file(self, file_path: str, checksum: str) -> bool:
        """校验文件的 MD5 摘要"""
        computed = self.encrypt_file(file_path)
        return secrets.compare_digest(computed.lower(), checksum.lower())


class ItsDCipher:
    """itsdangerous 签名序列化器

    使用场景
    --------
    - 邮箱验证 / 密码重置链接中的 Token
    - 一次性 URL 参数（分享链接、下载链接等）
    - 需要过期机制的临时凭证
    - Cookie 中的已登录用户标识（配合 session）

    技术特性
    --------
    - 基于 itsdangerous.URLSafeTimedSerializer
    - 支持任意 Python 对象序列化（dict、list、str、int 等）
    - 内置时间戳, 支持过期校验
    - URL 安全的 Base64 编码
    - HMAC-SHA1 签名（itsdangerous 默认）

    安全说明
    --------
    - 数据是签名的, 不是加密的！接收方可以解码看到内容
    - 签名确保数据未被篡改
    - 若数据本身敏感, 请先用 AESCipher 加密再传入

    示例
    ----
    ```python
    cipher = ItsDCipher(secret_key='your-secret-key', salt='email-verify')
    token = cipher.encrypt({'user_id': 123, 'action': 'verify_email'})
    # URL: /verify?token=xxx
    # 验证（1 小时内有效）, 过期则抛出 ValueError
    data = cipher.decrypt(token, max_age=3600)  # -> {"user_id": 123, ...}
    ```
    """

    def __init__(self, secret_key: str, salt: str | None = 'itsdangerous-default-salt') -> None:
        """初始化 ItsDangerous 签名器

        Args:
            secret_key: 签名密钥, 应保密且足够复杂
            salt: 命名空间隔离, 不同用途使用不同 salt
                  例如：'email-verify', 'password-reset', 'download-link'
        """
        self._secret_key = secret_key
        self._salt = salt
        self._serializer = URLSafeTimedSerializer(secret_key)

    def encrypt(self, plaintext: Plaintext, **kwargs: Any) -> str:
        """签名并序列化数据

        特殊处理：
        - bytes: 转为 base64 字符串存储
        - str: 直接序列化
        - dict: 直接序列化

        Args:
            plaintext: 待签名数据

        Returns:
            str: URL 安全的签名 Token
        """
        # itsdangerous 原生支持 dict/list/str/int 等, 但不直接支持 bytes
        if isinstance(plaintext, bytes):
            # bytes 转 base64 字符串, 添加标记便于解码时识别
            data: Any = {'__bytes__': base64.urlsafe_b64encode(plaintext).decode('ascii')}
        elif isinstance(plaintext, (str, dict)):
            data = plaintext
        else:
            raise TypeError(f'itsdangerous 不支持类型: {type(plaintext).__name__}')

        return self._serializer.dumps(data, salt=self._salt)

    def decrypt(
        self,
        token: str,
        *,
        max_age: int | None = None,
        return_type: type[T] | None = None,
    ) -> str | bytes | dict | T:
        """验证签名并反序列化数据

        Args:
            token: 签名 Token
            max_age: 最大有效期（秒）
                - None: 不校验过期, Token 永久有效（默认）
                - 0: 立即过期, Token 在创建后的同一秒内有效, 之后立即失效
                - 正整数 n: Token 在 n 秒内有效
            return_type: 强制返回类型

        Returns:
            反序列化后的原始数据

        Raises:
            ValueError: 签名无效或已过期
        """
        try:
            data = self._serializer.loads(token, salt=self._salt, max_age=max_age)
        except SignatureExpired as e:
            raise ValueError(f'Token 已过期: {e}') from e
        except BadSignature as e:
            raise ValueError(f'签名无效, 数据可能被篡改: {e}') from e

        # 处理 bytes 的还原
        if isinstance(data, dict) and '__bytes__' in data and len(data) == 1:
            return base64.urlsafe_b64decode(data['__bytes__'].encode('ascii'))

        if return_type is not None and not isinstance(data, return_type):
            raise ValueError(f'返回类型不匹配, 期望 {return_type.__name__}, 实际 {type(data).__name__}')
        return data

    def verify(self, token: str, *, max_age: int | None = None) -> bool:
        """验证 Token 是否有效（不返回数据）

        快速校验 Token 有效性, 适合只需知道是否有效的场景。

        Args:
            token: 签名 Token
            max_age: 最大有效期（秒）
                - None: 不校验过期, Token 永久有效（默认）
                - 0: 立即过期, Token 在创建后的同一秒内有效, 之后立即失效
                - 正整数 n: Token 在 n 秒内有效

        Returns:
            bool: 有效返回 True, 无效或过期返回 False
        """
        try:
            self._serializer.loads(token, salt=self._salt, max_age=max_age)
            return True
        except SignatureExpired, BadSignature:
            return False

    def get_token_age(self, token: str) -> int | None:
        """获取 Token 的已存活时间（秒）

        Returns:
            int: Token 已存活的秒数, 签名无效则返回 None
        """
        try:
            _, timestamp = self._serializer.loads(token, salt=self._salt, return_timestamp=True)
            from datetime import datetime, timezone

            now = datetime.now(timezone.utc)
            return int((now - timestamp).total_seconds())
        except SignatureExpired, BadSignature:
            return None
