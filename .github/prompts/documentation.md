# 文档注释规范

## 函数文档字符串格式

### 有参数的函数

```python
def example_function(param1: str, param2: int) -> dict[str, Any]:
    """
    这是函数的描述

    :param param1: 参数1的说明
    :param param2: 参数2的说明
    :return: 不添加返回说明
    """
```

### 无参数的函数

```python
def example_function() -> str:
    """这是函数的描述"""
```

### 被装饰器修饰的函数（如 model_validator, field_validator）

```python
@model_validator(mode='before')
def validate_data(cls, data: Any) -> Any:
    """验证数据格式"""
```

## 规范要点

- 不要在文件开头添加注释
- 跳过第一行编写文档
- 函数描述要简洁明了
- 不需要举例说明
- 中英文之间要有空格
- 参数说明要具体和清晰
