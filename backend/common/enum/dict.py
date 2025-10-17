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
    GITHUB = ('GitHub', 'github')
    Apple = ('Apple', 'apple')
    GOOGLE = ('Google', 'google')
    EMAIL = ('邮箱', 'email')
    PHONE = ('手机号', 'phone')
    OTHER = ('其他平台', 'other')


class SourceEnum(DictEnum):
    """用户来源枚举"""

    ORGANIC_SEARCH = ('自然搜索', 'organic_search')
    PAID_SEARCH = ('付费搜索', 'paid_search')
    SOCIAL_MEDIA = ('社交媒体引流', 'social_media')
    DIRECT_ACCESS = ('直接访问', 'direct_access')
    REFERRAL = ('外部链接跳转', 'referral')
    APP_STORE = ('应用商店', 'app_store')
    QR_CODE = ('扫描二维码', 'qr_code')
    OFFLINE_EVENT = ('线下活动', 'offline_event')
    FRIEND_RECOMMENDATION = ('好友推荐', 'friend_recommendation')
    CONTENT_MARKETING = ('内容营销', 'content_marketing')
    ECOMMERCE_PARTNER = ('电商合作伙伴', 'ecommerce_partner')
    BANNER_AD = ('横幅广告', 'banner_ad')
    PUSH_NOTIFICATION = ('推送通知', 'push_notification')
    SMS_PROMOTION = ('短信营销', 'sms_promotion')
    EMAIL_MARKETING = ('邮件营销', 'email_marketing')
    KOL_PROMOTION = ('KOL推广', 'kol_promotion')
    LIVE_STREAMING = ('直播推广', 'live_streaming')
    OFFICIAL_WEBSITE = ('官方网站', 'official_website')
    CUSTOMER_SERVICE = ('客服推荐', 'customer_service')
    OTHER = ('其他来源', 'other')
