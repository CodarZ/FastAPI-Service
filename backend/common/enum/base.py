from enum import Enum, IntEnum as SourceIntEnum, StrEnum as SourceStrEnum


class _EnumBase(Enum):
    """枚举辅助基类，用于扩展枚举类的功能

    `cls.__members__` 是枚举类的特殊属性，包含所有成员的键值对。
    """

    @classmethod
    def get_member_keys(cls):
        return list(cls.__members__.keys())

    @classmethod
    def get_member_values(cls):
        return [member.value for member in cls]

    @classmethod
    def has_key(cls, key: str) -> bool:
        return key in cls.__members__

    @classmethod
    def has_value(cls, value) -> bool:
        return value in cls.get_member_values()

    @classmethod
    def value_of(cls, key: str):
        """通过 key 获取枚举成员，找不到则返回 None"""
        return cls.__members__.get(key)


class IntEnum(_EnumBase, SourceIntEnum):
    """自定义整数枚举类"""


class StrEnum(_EnumBase, SourceStrEnum):
    """自定义字符串枚举类"""


class DictEnum(Enum):
    """自定义键值对枚举类"""

    @property
    def label(self) -> str:
        return self.value[0]

    @property
    def code(self) -> str:
        return self.value[1]

    @classmethod
    def get_member_keys(cls):
        """枚举成员 key 列表"""
        return list(cls.__members__.keys())

    @classmethod
    def get_member_values(cls):
        """枚举成员 value 列表"""
        return [member.value for member in cls]

    @classmethod
    def get_member_codes(cls):
        """枚举成员的 code 列表"""
        return [member.code for member in cls]

    @classmethod
    def get_member_labels(cls):
        """枚举成员的 label 列表"""
        return [member.label for member in cls]

    @classmethod
    def has_key(cls, key: str) -> bool:
        """检查是否存在指定的键名"""
        return key in cls.__members__

    @classmethod
    def has_code(cls, code: str) -> bool:
        """检查是否存在指定的 code"""
        return code in cls.get_member_codes()

    @classmethod
    def has_label(cls, label: str) -> bool:
        """检查是否存在指定的 label"""
        return label in cls.get_member_labels()

    @classmethod
    def value_of(cls, key: str):
        """通过 key 获取枚举成员"""
        return cls.__members__.get(key)

    @classmethod
    def get_by_code(cls, code: str):
        """通过 code 获取枚举成员"""
        for member in cls:
            if member.code == code:
                return member
        return None

    @classmethod
    def get_by_label(cls, label: str):
        """通过 label 获取枚举成员"""
        for member in cls:
            if member.label == label:
                return member
        return None


class ResponseStatusEnum(Enum):
    """自定义状态码基类

    枚举成员应为 `(code, msg)` 的元组

    示例：
    ```python
      class StatusCode(BaseResponseStatus):
          SUCCESS = (200, "请求成功")
          ERROR = (500, "服务器内部错误")

      StatusCode.SUCCESS.code  # 输出: 200
      StatusCode.SUCCESS.msg   # 输出: "请求成功"
    ```
    """

    @property
    def code(self) -> int:
        """获取状态码"""
        return self.value[0]

    @property
    def msg(self) -> str:
        """获取状态码信息"""
        return self.value[1]
