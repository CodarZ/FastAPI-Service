# 代码注释规范

## 文件头注释

每个 Python 文件都必须以以下内容开头：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
```

## 注释编写原则

- 合理的注释，避免不必要的注释
- 中英文之间应包加空格
- 注释文字描述应具体和清晰
- 注释要让人视觉上更清晰

## 注释类型

### 行内注释

```python
result = calculate_total(items)  # 计算总价
```

### 块注释

```python
# 处理用户输入数据
# 验证必要字段并进行格式化
user_data = process_input(raw_data)
```

### 类注释

```python
class UserService:
    """用户服务类，处理用户相关的业务逻辑"""
```

## 注释位置

- 注释应该解释"为什么"而不是"是什么"
- 复杂逻辑前应添加说明注释
- 重要的业务逻辑应有清晰的注释说明
