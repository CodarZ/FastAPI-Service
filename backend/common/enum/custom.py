#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from backend.common.enum.base import IntEnum, StrEnum


class LoginLogStatusEnum(IntEnum):
    """登陆日志状态"""

    FAIL = 0
    SUCCESS = 1


class StatusEnum(IntEnum):
    """状态类型枚举"""

    DISABLE = 0
    ENABLE = 1


class OperationLogCipherEnum(IntEnum):
    """
    操作日志加密类型枚举

    AES:          0 - 使用 AES 对称加密（安全性高，性能损耗较大）
    MD5:          1 - 使用 MD5 摘要加密（不可逆，适合简单脱敏）
    ITS_DANGEROUS: 2 - 使用 ItsDangerous 加密（常用于签名和加密，适合 Web 场景）
    PLAN:         3 - 不加密（明文存储）
    """

    AES = 0
    MD5 = 1
    ITS_DANGEROUS = 2
    PLAN = 3


class MenuEnum(IntEnum):
    """
    菜单类型枚举

    + DIRECTORY:  0 - 目录/文件夹，用于组织和分组菜单项
    + MENU:       1 - 菜单页面，可点击跳转的功能页面
    + BUTTON:     2 - 按钮，页面内的操作按钮（如新增、删除等）
    + EMBEDDED:   3 - 嵌入式组件，内嵌在页面中的功能模块
    + LINK:       4 - 外部链接，跳转到外部网站或资源
    """

    DIRECTORY = 0
    MENU = 1
    BUTTON = 2
    EMBEDDED = 3
    LINK = 4


class RoleDataRuleOperatorEnum(IntEnum):
    """数据权限规则运算符"""

    AND = 0
    OR = 1


class UserPermissionEnum(StrEnum):
    """
    用户权限类型

    + SUPER_USER:    超级管理员 - 拥有系统最高权限，可管理所有功能和用户
    + STAFF:        员工/管理员 - 具有后台管理权限，可执行管理操作
    + USER:         用户 - 用户
    + MULTI_LOGIN:  多设备登录权限 - 允许用户在多个设备上同时登录
    """

    SUPER_USER = 'superuser'
    STAFF = 'staff'
    USER = 'user'
    MULTI_LOGIN = 'multi_login'


class RoleDataRuleExpressionEnum(IntEnum):
    """数据权限规则表达式"""

    EQ = 0  # ==
    NE = 1  # !=
    GT = 2  # >
    GE = 3  # >=
    LT = 4  # <
    LE = 5  # <=
    IN_ = 6  # in
    NOT_IN = 7  # not in


class MethodEnum(StrEnum):
    """请求方法"""

    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    OPTIONS = 'OPTIONS'


class BuildTreeEnum(StrEnum):
    """
    构建树形结构类型枚举
    + TRAVERSAL: 遍历
    + RECURSIVE: 递归
    """

    TRAVERSAL = 'traversal'
    RECURSIVE = 'recursive'


class FileTypeEnum(StrEnum):
    """文件类型"""

    IMAGE = 'image'
    VIDEO = 'video'


class UserSocialEnum(StrEnum):
    """用户社交类型枚举"""

    WECHAT = '微信'
    QQ = 'QQ'
    WEIBO = '微博'
    DOUYIN = '抖音'
    XIAOHONGSHU = '小红书'
    TAOBAO = '淘宝'
    JD = '京东'
    PINDUODUO = '拼多多'
    ALIPAY = '支付宝'
    ZHIHU = '知乎'
    BILIBILI = '哔哩哔哩'
    KUWO = '酷我'
    KUKE = '酷客'
    MEITUAN = '美团'
    ELEME = '饿了么'
    TIEBA = '百度贴吧'
    YOUKU = '优酷'
    TOUTIAO = '今日头条'
    GITHUB = 'GitHub'
    GOOGLE = 'Google'
    EMAIL = '邮箱'
    PHONE = '手机号'
    OTHER = '其他平台'


class UserSourceEnum(StrEnum):
    """用户来源枚举"""

    ORGANIC_SEARCH = 'organic_search'  # 自然搜索
    PAID_SEARCH = 'paid_search'  # 付费搜索（如百度推广、360竞价）
    SOCIAL_MEDIA = 'social_media'  # 社交媒体引流
    DIRECT_ACCESS = 'direct_access'  # 直接访问
    REFERRAL = 'referral'  # 外部链接跳转
    APP_STORE = 'app_store'  # 应用商店
    QR_CODE = 'qr_code'  # 扫描二维码
    OFFLINE_EVENT = 'offline_event'  # 线下活动
    FRIEND_RECOMMENDATION = 'friend_recommendation'  # 好友推荐
    CONTENT_MARKETING = 'content_marketing'  # 内容营销（如软文、视频）
    ECOMMERCE_PARTNER = 'ecommerce_partner'  # 电商合作伙伴（如京东、天猫）
    BANNER_AD = 'banner_ad'  # 横幅广告
    PUSH_NOTIFICATION = 'push_notification'  # 推送通知
    SMS_PROMOTION = 'sms_promotion'  # 短信营销
    EMAIL_MARKETING = 'email_marketing'  # 邮件营销
    KOL_PROMOTION = 'kol_promotion'  # KOL（关键意见领袖）推广
    LIVE_STREAMING = 'live_streaming'  # 直播推广（如抖音直播、快手直播）
    OFFICIAL_WEBSITE = 'official_website'  # 官方网站
    CUSTOMER_SERVICE = 'customer_service'  # 客服推荐
    OTHER = 'other'  # 其他来源
