from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

password_hash = PasswordHash((BcryptHasher(),))


def get_hashed_password(password: str, salt: bytes | None) -> str:
    """使用哈希算法加密密码"""
    return password_hash.hash(password, salt=salt)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """密码验证"""
    return password_hash.verify(plain_password, hashed_password)
