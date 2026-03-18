import re

# 中国大陆手机号: 1开头的11位数字
MOBILE_PATTERN = re.compile(r'^1[3-9]\d{9}$')
