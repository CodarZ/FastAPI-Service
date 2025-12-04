from backend.common.enum.base import DictEnum


class SocialEnum(DictEnum):
    """用户社交类型枚举"""

    WECHAT = ('微信', 'we_chat')
    QQ = ('QQ', 'qq')
    WEIBO = ('微博', 'wei_bo')
    DOUYIN = ('抖音', 'dou_yin')
    XIAOHONGSHU = ('小红书', 'xiao_hong_shu')
    TAOBAO = ('淘宝', 'tao_bao')
    JD = ('京东', 'jd')
    PINDUODUO = ('拼多多', 'pin_duo_duo')
    ALIPAY = ('支付宝', 'ali_pay')
    ZHIHU = ('知乎', 'zhi_hu')
    BILIBILI = ('哔哩哔哩', 'bili_bili')
    KUWO = ('酷我', 'ku_wo')
    KUKE = ('酷客', 'ku_ke')
    MEITUAN = ('美团', 'mei_tuan')
    ELEME = ('饿了么', 'ele_me')
    TIEBA = ('百度贴吧', 'tie_ba')
    YOUKU = ('优酷', 'you_ku')
    TOUTIAO = ('今日头条', 'tou_tiao')
    EMAIL = ('邮箱', 'email')
    PHONE = ('手机号', 'phone')
    GITHUB = ('GitHub', 'github')
    APPLE = ('Apple', 'apple')
    GOOGLE = ('Google', 'google')
    OTHER = ('其他平台', 'other')
