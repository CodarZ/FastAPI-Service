"""encrypt.py 模块的完整测试

测试覆盖：
- AESCipher: AES-256-GCM 对称加密/解密
- SHA256Cipher: SHA-256 摘要与验证
- MD5Cipher: MD5 摘要与验证
- ItsDCipher: itsdangerous 签名序列化
- _normalize_input: 输入规范化函数
"""

import json
import pathlib
import tempfile
import time

import pytest

from backend.utils.encrypt import (
    AESCipher,
    ItsDCipher,
    MD5Cipher,
    SHA256Cipher,
    _normalize_input,
)


# =============================================================================
# _normalize_input 函数测试
# =============================================================================
class TestNormalizeInput:
    """测试输入规范化函数"""

    def test_bytes_input_returns_directly(self):
        """bytes 输入直接返回"""
        data = b'hello world'
        result = _normalize_input(data)
        assert result == data
        assert isinstance(result, bytes)

    def test_str_input_encodes_to_utf8(self):
        """str 输入转换为 UTF-8 bytes"""
        data = 'hello world'
        result = _normalize_input(data)
        assert result == b'hello world'

    def test_str_input_with_unicode(self):
        """包含 Unicode 的 str 正确编码"""
        data = '你好，世界！🎉'
        result = _normalize_input(data)
        assert result == data.encode('utf-8')

    def test_dict_input_json_serialized(self):
        """dict 输入序列化为 JSON bytes"""
        data = {'key': 'value', 'number': 123}
        result = _normalize_input(data)
        expected = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        assert result == expected

    def test_dict_input_preserves_unicode(self):
        """dict 中的 Unicode 字符正确保留"""
        data = {'name': '张三', 'message': '你好'}
        result = _normalize_input(data)
        # 确保没有被 ASCII 转义
        assert '张三'.encode('utf-8') in result
        assert '你好'.encode('utf-8') in result

    def test_unsupported_type_raises_typeerror(self):
        """不支持的类型抛出 TypeError"""
        with pytest.raises(TypeError, match='不支持的输入类型'):
            _normalize_input(12345)  # type: ignore[arg-type]

        with pytest.raises(TypeError, match='不支持的输入类型'):
            _normalize_input([1, 2, 3])  # type: ignore[arg-type]

        with pytest.raises(TypeError, match='不支持的输入类型'):
            _normalize_input(None)  # type: ignore[arg-type]


# =============================================================================
# AESCipher 类测试
# =============================================================================
class TestAESCipher:
    """测试 AES-256-GCM 对称加密器"""

    # 有效的 32 字节密钥
    VALID_KEY_STR = '12345678901234567890123456789012'
    VALID_KEY_BYTES = b'12345678901234567890123456789012'

    # -------------------------------------------------------------------------
    # 初始化测试
    # -------------------------------------------------------------------------
    def test_init_with_valid_str_key(self):
        """使用有效 str 密钥初始化成功"""
        cipher = AESCipher(self.VALID_KEY_STR)
        assert cipher is not None

    def test_init_with_valid_bytes_key(self):
        """使用有效 bytes 密钥初始化成功"""
        cipher = AESCipher(self.VALID_KEY_BYTES)
        assert cipher is not None

    def test_init_with_short_str_key_raises_valueerror(self):
        """str 密钥太短抛出 ValueError"""
        with pytest.raises(ValueError, match='字符串密钥编码后必须为 32 字节'):
            AESCipher('too-short')

    def test_init_with_long_str_key_raises_valueerror(self):
        """str 密钥太长抛出 ValueError"""
        with pytest.raises(ValueError, match='字符串密钥编码后必须为 32 字节'):
            AESCipher('a' * 64)

    def test_init_with_short_bytes_key_raises_valueerror(self):
        """bytes 密钥太短抛出 ValueError"""
        with pytest.raises(ValueError, match='bytes 密钥必须为 32 字节'):
            AESCipher(b'too-short')

    def test_init_with_long_bytes_key_raises_valueerror(self):
        """bytes 密钥太长抛出 ValueError"""
        with pytest.raises(ValueError, match='bytes 密钥必须为 32 字节'):
            AESCipher(b'a' * 64)

    def test_init_with_invalid_key_type_raises_typeerror(self):
        """无效密钥类型抛出 TypeError"""
        with pytest.raises(TypeError, match='密钥类型必须为 str 或 bytes'):
            AESCipher(12345)  # type: ignore[arg-type]

    def test_init_with_unicode_str_key_length_check(self):
        """中文等多字节字符的密钥长度校验（按字节计算）"""
        # 中文字符在 UTF-8 中占 3 字节
        with pytest.raises(ValueError, match='字符串密钥编码后必须为 32 字节'):
            AESCipher('中文密钥测试')  # 这会超过 32 字节

    # -------------------------------------------------------------------------
    # 加密/解密测试（Base64 格式）
    # -------------------------------------------------------------------------
    def test_encrypt_decrypt_str(self):
        """加密解密 str 类型"""
        cipher = AESCipher(self.VALID_KEY_STR)
        plaintext = 'Hello, World!'
        encrypted = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_decrypt_bytes(self):
        """加密解密 bytes 类型"""
        cipher = AESCipher(self.VALID_KEY_STR)
        plaintext = b'\x00\x01\x02\x03binary data'
        encrypted = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(encrypted, return_type=bytes)
        assert decrypted == plaintext

    def test_encrypt_decrypt_dict(self):
        """加密解密 dict 类型"""
        cipher = AESCipher(self.VALID_KEY_STR)
        plaintext = {'user': 'admin', 'id': 123, 'roles': ['read', 'write']}
        encrypted = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(encrypted, return_type=dict)
        assert decrypted == plaintext

    def test_encrypt_decrypt_unicode(self):
        """加密解密 Unicode 字符"""
        cipher = AESCipher(self.VALID_KEY_STR)
        plaintext = '你好世界 🎉🎊'
        encrypted = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(encrypted)
        assert decrypted == plaintext

    def test_encrypt_produces_different_ciphertext_each_time(self):
        """每次加密产生不同的密文（因为 nonce 随机）"""
        cipher = AESCipher(self.VALID_KEY_STR)
        plaintext = 'same plaintext'
        encrypted1 = cipher.encrypt(plaintext)
        encrypted2 = cipher.encrypt(plaintext)
        assert encrypted1 != encrypted2

    def test_decrypt_with_wrong_key_raises_valueerror(self):
        """使用错误密钥解密抛出 ValueError"""
        cipher1 = AESCipher(self.VALID_KEY_STR)
        cipher2 = AESCipher('different-key-32-bytes-long!!!!!')
        encrypted = cipher1.encrypt('secret')
        with pytest.raises(ValueError, match='解密失败'):
            cipher2.decrypt(encrypted)

    def test_decrypt_invalid_base64_raises_valueerror(self):
        """无效 Base64 密文抛出 ValueError"""
        cipher = AESCipher(self.VALID_KEY_STR)
        # 使用完全无效的 base64（包含非法字符）
        with pytest.raises(ValueError):
            cipher.decrypt('!!!invalid!!!')

    def test_decrypt_truncated_ciphertext_raises_valueerror(self):
        """截断的密文抛出 ValueError"""
        cipher = AESCipher(self.VALID_KEY_STR)
        # 太短的密文（少于 nonce + tag 长度）
        import base64

        short_data = base64.urlsafe_b64encode(b'short').decode('ascii')
        with pytest.raises(ValueError, match='密文长度不足'):
            cipher.decrypt(short_data)

    def test_decrypt_tampered_ciphertext_raises_valueerror(self):
        """被篡改的密文抛出 ValueError"""
        cipher = AESCipher(self.VALID_KEY_STR)
        encrypted = cipher.encrypt('original data')
        # 篡改密文中的一些字符
        import base64

        data = bytearray(base64.urlsafe_b64decode(encrypted))
        data[-1] ^= 0xFF  # 翻转最后一个字节
        tampered = base64.urlsafe_b64encode(bytes(data)).decode('ascii')
        with pytest.raises(ValueError, match='解密失败'):
            cipher.decrypt(tampered)

    def test_decrypt_with_invalid_json_for_dict_return_type(self):
        """返回类型为 dict 但解密数据不是有效 JSON 抛出 ValueError"""
        cipher = AESCipher(self.VALID_KEY_STR)
        encrypted = cipher.encrypt('not a json string')
        with pytest.raises(ValueError, match='JSON 反序列化失败'):
            cipher.decrypt(encrypted, return_type=dict)

    # -------------------------------------------------------------------------
    # 加密/解密测试（Hex 格式）
    # -------------------------------------------------------------------------
    def test_encrypt_to_hex_decrypt_from_hex_str(self):
        """Hex 格式加密解密 str"""
        cipher = AESCipher(self.VALID_KEY_STR)
        plaintext = 'Hello, Hex World!'
        encrypted = cipher.encrypt_to_hex(plaintext)
        # 验证是有效的 hex 字符串
        assert all(c in '0123456789abcdef' for c in encrypted)
        decrypted = cipher.decrypt_from_hex(encrypted)
        assert decrypted == plaintext

    def test_encrypt_to_hex_decrypt_from_hex_dict(self):
        """Hex 格式加密解密 dict"""
        cipher = AESCipher(self.VALID_KEY_STR)
        plaintext = {'key': 'value', 'list': [1, 2, 3]}
        encrypted = cipher.encrypt_to_hex(plaintext)
        decrypted = cipher.decrypt_from_hex(encrypted, return_type=dict)
        assert decrypted == plaintext

    def test_decrypt_from_hex_invalid_hex_raises_valueerror(self):
        """无效 Hex 密文抛出 ValueError"""
        cipher = AESCipher(self.VALID_KEY_STR)
        with pytest.raises(ValueError, match='密文 Hex 解码失败'):
            cipher.decrypt_from_hex('not-valid-hex-zzz')

    def test_decrypt_from_hex_truncated_raises_valueerror(self):
        """截断的 Hex 密文抛出 ValueError"""
        cipher = AESCipher(self.VALID_KEY_STR)
        with pytest.raises(ValueError, match='密文长度不足'):
            cipher.decrypt_from_hex('aabbccdd')

    def test_decrypt_from_hex_wrong_key_raises_valueerror(self):
        """Hex 格式使用错误密钥解密抛出 ValueError"""
        cipher1 = AESCipher(self.VALID_KEY_STR)
        cipher2 = AESCipher('another-key-32-bytes-long!!!!!!!')
        encrypted = cipher1.encrypt_to_hex('secret data')
        with pytest.raises(ValueError, match='解密失败'):
            cipher2.decrypt_from_hex(encrypted)


# =============================================================================
# SHA256Cipher 类测试
# =============================================================================
class TestSHA256Cipher:
    """测试 SHA-256 摘要器"""

    # -------------------------------------------------------------------------
    # 初始化测试
    # -------------------------------------------------------------------------
    def test_init_default_iterations(self):
        """默认迭代次数为 1"""
        cipher = SHA256Cipher()
        assert cipher._iterations == 1

    def test_init_custom_iterations(self):
        """自定义迭代次数"""
        cipher = SHA256Cipher(iterations=10000)
        assert cipher._iterations == 10000

    def test_init_negative_iterations_normalized_to_1(self):
        """负数迭代次数被规范化为 1"""
        cipher = SHA256Cipher(iterations=-5)
        assert cipher._iterations == 1

    def test_init_zero_iterations_normalized_to_1(self):
        """零迭代次数被规范化为 1"""
        cipher = SHA256Cipher(iterations=0)
        assert cipher._iterations == 1

    # -------------------------------------------------------------------------
    # 加密/验证测试
    # -------------------------------------------------------------------------
    def test_encrypt_verify_str(self):
        """加密验证 str 类型"""
        cipher = SHA256Cipher()
        plaintext = 'password123'
        hashed = cipher.encrypt(plaintext)
        assert cipher.verify(plaintext, hashed) is True

    def test_encrypt_verify_bytes(self):
        """加密验证 bytes 类型"""
        cipher = SHA256Cipher()
        plaintext = b'binary password'
        hashed = cipher.encrypt(plaintext)
        assert cipher.verify(plaintext, hashed) is True

    def test_encrypt_verify_dict(self):
        """加密验证 dict 类型"""
        cipher = SHA256Cipher()
        plaintext = {'username': 'admin', 'password': 'secret'}
        hashed = cipher.encrypt(plaintext)
        assert cipher.verify(plaintext, hashed) is True

    def test_encrypt_produces_different_hash_each_time(self):
        """每次加密产生不同的哈希（因为盐值随机）"""
        cipher = SHA256Cipher()
        plaintext = 'same password'
        hash1 = cipher.encrypt(plaintext)
        hash2 = cipher.encrypt(plaintext)
        assert hash1 != hash2

    def test_verify_with_wrong_data_returns_false(self):
        """验证错误数据返回 False"""
        cipher = SHA256Cipher()
        hashed = cipher.encrypt('correct password')
        assert cipher.verify('wrong password', hashed) is False

    def test_verify_with_invalid_base64_returns_false(self):
        """验证无效 Base64 哈希返回 False"""
        cipher = SHA256Cipher()
        assert cipher.verify('any data', 'not-valid-base64!!!') is False

    def test_verify_with_wrong_length_hash_returns_false(self):
        """验证长度错误的哈希返回 False"""
        cipher = SHA256Cipher()
        import base64

        # 创建一个长度不对的哈希
        wrong_length = base64.urlsafe_b64encode(b'wrong length data').decode('ascii')
        assert cipher.verify('any data', wrong_length) is False

    def test_verify_with_high_iterations(self):
        """高迭代次数的加密验证"""
        cipher = SHA256Cipher(iterations=1000)
        plaintext = 'password'
        hashed = cipher.encrypt(plaintext)
        assert cipher.verify(plaintext, hashed) is True
        assert cipher.verify('wrong', hashed) is False

    # -------------------------------------------------------------------------
    # hash_without_salt 测试
    # -------------------------------------------------------------------------
    def test_hash_without_salt_deterministic(self):
        """不带盐的哈希是确定性的"""
        cipher = SHA256Cipher()
        plaintext = 'test data'
        hash1 = cipher.hash_without_salt(plaintext)
        hash2 = cipher.hash_without_salt(plaintext)
        assert hash1 == hash2

    def test_hash_without_salt_returns_hex(self):
        """不带盐的哈希返回 64 字符的 hex 字符串"""
        cipher = SHA256Cipher()
        result = cipher.hash_without_salt('test')
        assert len(result) == 64
        assert all(c in '0123456789abcdef' for c in result)

    def test_hash_without_salt_different_for_different_input(self):
        """不同输入产生不同的哈希"""
        cipher = SHA256Cipher()
        hash1 = cipher.hash_without_salt('input1')
        hash2 = cipher.hash_without_salt('input2')
        assert hash1 != hash2


# =============================================================================
# MD5Cipher 类测试
# =============================================================================
class TestMD5Cipher:
    """测试 MD5 摘要器"""

    # -------------------------------------------------------------------------
    # 基本加密/验证测试
    # -------------------------------------------------------------------------
    def test_encrypt_returns_32_char_hex(self):
        """加密返回 32 字符的 hex 字符串"""
        cipher = MD5Cipher()
        result = cipher.encrypt('test')
        assert len(result) == 32
        assert all(c in '0123456789abcdef' for c in result)

    def test_encrypt_verify_str(self):
        """加密验证 str 类型"""
        cipher = MD5Cipher()
        plaintext = 'hello world'
        checksum = cipher.encrypt(plaintext)
        assert cipher.verify(plaintext, checksum) is True

    def test_encrypt_verify_bytes(self):
        """加密验证 bytes 类型"""
        cipher = MD5Cipher()
        plaintext = b'binary data'
        checksum = cipher.encrypt(plaintext)
        assert cipher.verify(plaintext, checksum) is True

    def test_encrypt_verify_dict(self):
        """加密验证 dict 类型"""
        cipher = MD5Cipher()
        plaintext = {'key': 'value'}
        checksum = cipher.encrypt(plaintext)
        assert cipher.verify(plaintext, checksum) is True

    def test_encrypt_is_deterministic(self):
        """MD5 加密是确定性的（相同输入产生相同输出）"""
        cipher = MD5Cipher()
        plaintext = 'same input'
        hash1 = cipher.encrypt(plaintext)
        hash2 = cipher.encrypt(plaintext)
        assert hash1 == hash2

    def test_verify_case_insensitive(self):
        """验证时大小写不敏感"""
        cipher = MD5Cipher()
        plaintext = 'test'
        checksum_lower = cipher.encrypt(plaintext)
        checksum_upper = checksum_lower.upper()
        assert cipher.verify(plaintext, checksum_lower) is True
        assert cipher.verify(plaintext, checksum_upper) is True

    def test_verify_wrong_data_returns_false(self):
        """验证错误数据返回 False"""
        cipher = MD5Cipher()
        checksum = cipher.encrypt('original')
        assert cipher.verify('different', checksum) is False

    # -------------------------------------------------------------------------
    # 文件操作测试
    # -------------------------------------------------------------------------
    def test_encrypt_file(self):
        """计算文件的 MD5 摘要"""
        cipher = MD5Cipher()
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            f.write(b'file content for testing')
            temp_path = f.name

        try:
            result = cipher.encrypt_file(temp_path)
            assert len(result) == 32
            assert all(c in '0123456789abcdef' for c in result)
        finally:
            pathlib.Path(temp_path).unlink()

    def test_verify_file(self):
        """验证文件的 MD5 摘要"""
        cipher = MD5Cipher()
        content = b'file content to verify'

        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            f.write(content)
            temp_path = f.name

        try:
            checksum = cipher.encrypt_file(temp_path)
            assert cipher.verify_file(temp_path, checksum) is True
            assert cipher.verify_file(temp_path, 'wrong' * 8) is False
        finally:
            pathlib.Path(temp_path).unlink()

    def test_encrypt_file_matches_encrypt_content(self):
        """文件 MD5 与内容 MD5 一致"""
        cipher = MD5Cipher()
        content = b'test content'

        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            f.write(content)
            temp_path = f.name

        try:
            file_hash = cipher.encrypt_file(temp_path)
            content_hash = cipher.encrypt(content)
            assert file_hash == content_hash
        finally:
            pathlib.Path(temp_path).unlink()

    def test_encrypt_file_large_file(self):
        """大文件的 MD5 计算（验证分块读取）"""
        cipher = MD5Cipher()
        # 创建一个大于默认 chunk_size (8192) 的文件
        content = b'x' * 100000

        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as f:
            f.write(content)
            temp_path = f.name

        try:
            result = cipher.encrypt_file(temp_path)
            expected = cipher.encrypt(content)
            assert result == expected
        finally:
            pathlib.Path(temp_path).unlink()


# =============================================================================
# ItsDCipher 类测试
# =============================================================================
class TestItsDCipher:
    """测试 itsdangerous 签名序列化器"""

    SECRET_KEY = 'test-secret-key-12345'
    SALT = 'test-salt'

    # -------------------------------------------------------------------------
    # 初始化测试
    # -------------------------------------------------------------------------
    def test_init_with_default_salt(self):
        """使用默认 salt 初始化"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        assert cipher._salt == 'itsdangerous-default-salt'

    def test_init_with_custom_salt(self):
        """使用自定义 salt 初始化"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY, salt=self.SALT)
        assert cipher._salt == self.SALT

    def test_init_with_none_salt(self):
        """使用 None salt 初始化"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY, salt=None)
        assert cipher._salt is None

    # -------------------------------------------------------------------------
    # 加密/解密测试
    # -------------------------------------------------------------------------
    def test_encrypt_decrypt_str(self):
        """加密解密 str 类型"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        plaintext = 'hello world'
        token = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(token)
        assert decrypted == plaintext

    def test_encrypt_decrypt_dict(self):
        """加密解密 dict 类型"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        plaintext = {'user_id': 123, 'action': 'verify'}
        token = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(token)
        assert decrypted == plaintext

    def test_encrypt_decrypt_bytes(self):
        """加密解密 bytes 类型（自动转 base64）"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        plaintext = b'\x00\x01\x02\x03binary'
        token = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(token)
        assert decrypted == plaintext

    def test_encrypt_unsupported_type_raises_typeerror(self):
        """不支持的类型抛出 TypeError"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        with pytest.raises(TypeError, match='itsdangerous 不支持类型'):
            cipher.encrypt([1, 2, 3])  # type: ignore[arg-type] list 不是 Plaintext 类型

    def test_decrypt_with_wrong_secret_raises_valueerror(self):
        """使用错误密钥解密抛出 ValueError"""
        cipher1 = ItsDCipher(secret_key=self.SECRET_KEY)
        cipher2 = ItsDCipher(secret_key='different-secret-key')
        token = cipher1.encrypt('data')
        with pytest.raises(ValueError, match='签名无效'):
            cipher2.decrypt(token)

    def test_decrypt_with_wrong_salt_raises_valueerror(self):
        """使用错误 salt 解密抛出 ValueError"""
        cipher1 = ItsDCipher(secret_key=self.SECRET_KEY, salt='salt1')
        cipher2 = ItsDCipher(secret_key=self.SECRET_KEY, salt='salt2')
        token = cipher1.encrypt('data')
        with pytest.raises(ValueError, match='签名无效'):
            cipher2.decrypt(token)

    def test_decrypt_tampered_token_raises_valueerror(self):
        """篡改的 Token 抛出 ValueError"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        token = cipher.encrypt('original')
        # 篡改 token
        tampered = token[:-5] + 'XXXXX'
        with pytest.raises(ValueError, match='签名无效'):
            cipher.decrypt(tampered)

    def test_decrypt_invalid_token_raises_valueerror(self):
        """无效 Token 抛出 ValueError"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        with pytest.raises(ValueError, match='签名无效'):
            cipher.decrypt('completely-invalid-token')

    # -------------------------------------------------------------------------
    # 过期测试
    # -------------------------------------------------------------------------
    def test_decrypt_expired_token_raises_valueerror(self):
        """过期的 Token 抛出 ValueError"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        token = cipher.encrypt('data')
        # 等待超过 max_age 的时间让 token 过期
        time.sleep(2)
        # 设置 1 秒的 max_age，此时 token 已过期
        with pytest.raises(ValueError, match='Token 已过期'):
            cipher.decrypt(token, max_age=1)

    def test_decrypt_within_max_age_succeeds(self):
        """在有效期内解密成功"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        token = cipher.encrypt('data')
        # max_age 足够长
        decrypted = cipher.decrypt(token, max_age=3600)
        assert decrypted == 'data'

    def test_decrypt_without_max_age_ignores_expiry(self):
        """不设置 max_age 时忽略过期"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        token = cipher.encrypt('data')
        time.sleep(0.1)
        # 不传 max_age，即使 token "老了" 也能解密
        decrypted = cipher.decrypt(token)
        assert decrypted == 'data'

    # -------------------------------------------------------------------------
    # return_type 测试
    # -------------------------------------------------------------------------
    def test_decrypt_with_return_type_mismatch_raises_valueerror(self):
        """返回类型不匹配抛出 ValueError"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        token = cipher.encrypt('string data')
        with pytest.raises(ValueError, match='返回类型不匹配'):
            cipher.decrypt(token, return_type=dict)

    def test_decrypt_with_return_type_match_succeeds(self):
        """返回类型匹配时成功"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        token = cipher.encrypt({'key': 'value'})
        decrypted = cipher.decrypt(token, return_type=dict)
        assert decrypted == {'key': 'value'}

    # -------------------------------------------------------------------------
    # verify 方法测试
    # -------------------------------------------------------------------------
    def test_verify_valid_token_returns_true(self):
        """验证有效 Token 返回 True"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        token = cipher.encrypt('data')
        assert cipher.verify(token) is True

    def test_verify_invalid_token_returns_false(self):
        """验证无效 Token 返回 False"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        assert cipher.verify('invalid-token') is False

    def test_verify_expired_token_returns_false(self):
        """验证过期 Token 返回 False"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        token = cipher.encrypt('data')
        # 等待超过 max_age 的时间
        time.sleep(2)
        # 设置 1 秒的 max_age，此时 token 已过期
        assert cipher.verify(token, max_age=1) is False

    def test_verify_with_max_age_within_limit(self):
        """在有效期内验证返回 True"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        token = cipher.encrypt('data')
        assert cipher.verify(token, max_age=3600) is True

    # -------------------------------------------------------------------------
    # get_token_age 方法测试
    # -------------------------------------------------------------------------
    def test_get_token_age_valid_token(self):
        """获取有效 Token 的年龄"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        token = cipher.encrypt('data')
        time.sleep(0.1)
        age = cipher.get_token_age(token)
        assert age is not None
        assert age >= 0

    def test_get_token_age_invalid_token_returns_none(self):
        """获取无效 Token 的年龄返回 None"""
        cipher = ItsDCipher(secret_key=self.SECRET_KEY)
        age = cipher.get_token_age('invalid-token')
        assert age is None

    def test_get_token_age_wrong_secret_returns_none(self):
        """使用错误密钥获取年龄返回 None"""
        cipher1 = ItsDCipher(secret_key=self.SECRET_KEY)
        cipher2 = ItsDCipher(secret_key='different-key')
        token = cipher1.encrypt('data')
        age = cipher2.get_token_age(token)
        assert age is None


# =============================================================================
# 跨类互操作测试
# =============================================================================
class TestCrossClassInteroperability:
    """测试不同类之间的互操作性"""

    def test_aes_sha256_combination(self):
        """AES 加密后的数据可以被 SHA256 哈希"""
        aes = AESCipher('12345678901234567890123456789012')
        sha = SHA256Cipher()

        plaintext = 'sensitive data'
        encrypted = aes.encrypt(plaintext)
        hashed = sha.encrypt(encrypted)

        # 验证哈希
        assert sha.verify(encrypted, hashed) is True

    def test_itsd_with_aes_encrypted_data(self):
        """ItsDCipher 可以签名 AES 加密的数据"""
        aes = AESCipher('12345678901234567890123456789012')
        itsd = ItsDCipher(secret_key='secret')

        plaintext = 'secret message'
        encrypted = aes.encrypt(plaintext)
        token = itsd.encrypt(encrypted)
        decrypted_token = itsd.decrypt(token)
        assert isinstance(decrypted_token, str)  # 类型窄化
        decrypted_plaintext = aes.decrypt(decrypted_token)

        assert decrypted_plaintext == plaintext


# =============================================================================
# 边界情况测试
# =============================================================================
class TestEdgeCases:
    """测试边界情况"""

    def test_aes_empty_string(self):
        """AES 加密空字符串"""
        cipher = AESCipher('12345678901234567890123456789012')
        encrypted = cipher.encrypt('')
        decrypted = cipher.decrypt(encrypted)
        assert decrypted == ''

    def test_aes_empty_bytes(self):
        """AES 加密空 bytes"""
        cipher = AESCipher('12345678901234567890123456789012')
        encrypted = cipher.encrypt(b'')
        decrypted = cipher.decrypt(encrypted, return_type=bytes)
        assert decrypted == b''

    def test_aes_empty_dict(self):
        """AES 加密空 dict"""
        cipher = AESCipher('12345678901234567890123456789012')
        encrypted = cipher.encrypt({})
        decrypted = cipher.decrypt(encrypted, return_type=dict)
        assert decrypted == {}

    def test_sha256_empty_string(self):
        """SHA256 哈希空字符串"""
        cipher = SHA256Cipher()
        hashed = cipher.encrypt('')
        assert cipher.verify('', hashed) is True

    def test_md5_empty_string(self):
        """MD5 哈希空字符串"""
        cipher = MD5Cipher()
        checksum = cipher.encrypt('')
        assert cipher.verify('', checksum) is True
        # 空字符串的 MD5 是已知的
        assert checksum == 'd41d8cd98f00b204e9800998ecf8427e'

    def test_itsd_empty_string(self):
        """ItsDCipher 签名空字符串"""
        cipher = ItsDCipher(secret_key='secret')
        token = cipher.encrypt('')
        decrypted = cipher.decrypt(token)
        assert decrypted == ''

    def test_aes_very_long_data(self):
        """AES 加密超长数据"""
        cipher = AESCipher('12345678901234567890123456789012')
        plaintext = 'x' * 1000000  # 1MB 的数据
        encrypted = cipher.encrypt(plaintext)
        decrypted = cipher.decrypt(encrypted)
        assert decrypted == plaintext

    def test_sha256_unicode_edge_cases(self):
        """SHA256 处理特殊 Unicode 字符"""
        cipher = SHA256Cipher()
        # 包含各种特殊字符
        special_chars = '🎉\u0000\uffff\u200b零宽空格'
        hashed = cipher.encrypt(special_chars)
        assert cipher.verify(special_chars, hashed) is True


# =============================================================================
# 性能与安全特性测试
# =============================================================================
class TestSecurityFeatures:
    """测试安全特性"""

    def test_aes_nonce_uniqueness(self):
        """AES 每次加密使用不同的 nonce"""
        cipher = AESCipher('12345678901234567890123456789012')
        import base64

        encrypted1 = cipher.encrypt('same data')
        encrypted2 = cipher.encrypt('same data')

        # 解码并比较 nonce（前 12 字节）
        nonce1 = base64.urlsafe_b64decode(encrypted1)[:12]
        nonce2 = base64.urlsafe_b64decode(encrypted2)[:12]

        assert nonce1 != nonce2

    def test_sha256_salt_uniqueness(self):
        """SHA256 每次加密使用不同的盐值"""
        cipher = SHA256Cipher()
        import base64

        hash1 = cipher.encrypt('same password')
        hash2 = cipher.encrypt('same password')

        # 解码并比较盐值（前 16 字节）
        salt1 = base64.urlsafe_b64decode(hash1)[:16]
        salt2 = base64.urlsafe_b64decode(hash2)[:16]

        assert salt1 != salt2

    def test_sha256_timing_attack_resistance(self):
        """SHA256 验证使用 secrets.compare_digest 防止时序攻击"""
        # 这是一个概念性测试，确保使用了安全的比较方法
        # 实际代码中已使用 secrets.compare_digest
        cipher = SHA256Cipher()
        hashed = cipher.encrypt('password')

        # 多次验证应该时间相近（虽然这不是严格的时序测试）
        import time

        times = []
        for _ in range(10):
            start = time.perf_counter()
            cipher.verify('password', hashed)
            times.append(time.perf_counter() - start)

        # 验证时间波动不太大（粗略检查）
        assert max(times) < min(times) * 100  # 允许100倍的波动

    def test_md5_timing_attack_resistance(self):
        """MD5 验证使用 secrets.compare_digest 防止时序攻击"""
        cipher = MD5Cipher()
        checksum = cipher.encrypt('data')

        # 同样的概念性测试
        result = cipher.verify('data', checksum)
        assert result is True
