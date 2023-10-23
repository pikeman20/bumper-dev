"""LogHelper module."""
import logging
import re
from datetime import datetime

import coloredlogs
import verboselogs


class LogHelper:
    """LogHelper."""

    def __init__(self, logging_verbose: int = 2, logging_level: str = "INFO") -> None:
        """Log Helper init."""
        # configure logger for requested verbosity
        log_format: str = "%(message)s"
        if logging_verbose >= 5:
            log_format = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)d :: %(message)s"
        elif logging_verbose == 4:
            log_format = (
                "[%(asctime)s,%(msecs)03d] :: %(levelname)-7s ::"
                " %(name)s[%(process)d] {%(lineno)-6d: (%(funcName)-30s)} - %(message)s"
            )
        elif logging_verbose == 3:
            log_format = (
                "[%(asctime)s] :: %(levelname)-5s ::"
                " [%(filename)-18s/%(module)-10s - %(lineno)-6d: (%(funcName)-30s)] - %(message)s"
            )
        elif logging_verbose == 2:
            log_format = "[%(asctime)s] %(levelname)-5s :: %(name)-22s - %(message)s"
        elif logging_verbose == 1:
            log_format = "[%(asctime)s] - %(message)s"

        # create a log object from verboselogs
        verboselogs.install()

        for logger_name in [logging.getLogger()] + [logging.getLogger(name) for name in logging.getLogger().manager.loggerDict]:
            for handler in logger_name.handlers:
                logger_name.removeHandler(handler)
            # define log level default
            logger_name.setLevel(logging.getLevelName(logging_level))
            # add colered logs
            coloredlogs.install(
                level=logging.getLevelName(logging_level),
                fmt=log_format,
                logger=logger_name,
            )

            # logger_name.addHandler(logging.StreamHandler(sys.stdout))

            if logging_level == "INFO" and logger_name.name.startswith("aiohttp.access"):
                logger_name.setLevel(logging.DEBUG)
                logger_name.addFilter(AioHttpFilter())

            if logging_level == "INFO" and logger_name.name.startswith("httpx"):
                logger_name.setLevel(logging.WARNING)
            if logging_level == "INFO" and logger_name.name.startswith("amqtt"):
                logger_name.setLevel(logging.WARNING)


class AioHttpFilter(logging.Filter):
    """AioHttpFilter."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Aio Http Filter filter."""
        if record.name == "aiohttp.access" and record.levelno == 20:  # Filters aiohttp.access log to switch it from INFO to DEBUG
            record.levelno = 10
            record.levelname = "DEBUG"
        return bool(record.levelno == 10 and logging.getLogger("confserver").getEffectiveLevel() == 10)


def default_exception_str_builder(e: Exception, info: str | None = None) -> str:
    """Build default exception message."""
    if info is None:
        return f"Unexpected exception occurred :: {e}"
    return f"Unexpected exception occurred :: {info} :: {e}"


def convert_to_millis(seconds: int | float) -> int:
    """Convert seconds to milliseconds."""
    return int(round(seconds * 1000))


def get_current_time_as_millis() -> int:
    """Get current time in millis."""
    return convert_to_millis(datetime.utcnow().timestamp())


def strtobool(strbool: str | int | bool | None) -> bool:
    """Convert str to bool."""
    return str(strbool).lower() in ["true", "1", "t", "y", "on", "yes"]


def check_url_not_used(url: str) -> bool:
    """Check if a url is not in the know api list, used in the middleware for debug."""
    for pattern in _FIND_NOT_USED_API_REQUEST:
        if re.search(pattern, url):
            return True
    return False


def get_dc_code(area_code: str) -> str:
    """Return to a area code the corresponding dc code."""
    return area_code_mapping.get(area_code, "na")


area_code_mapping = {
    "00": "dc",
    "cn": "ap",
    "tw": "ap",
    "my": "ap",
    "jp": "ap",
    "sg": "ap",
    "de": "eu",
    "at": "eu",
    "li": "eu",
    "fr": "eu",
    "th": "ap",
    "us": "na",
    "es": "eu",
    "uk": "eu",
    "no": "na",
    "mx": "na",
    "in": "na",
    "ch": "na",
    "hk": "na",
    "it": "na",
    "nl": "na",
    "se": "na",
    "lu": "na",
    "be": "na",
    "ae": "na",
    "br": "na",
    "ca": "na",
    "ua": "na",
    "cz": "na",
    "pl": "na",
    "dk": "na",
    "pt": "na",
    "kr": "na",
    "tr": "na",
    "au": "na",
    "lv": "na",
    "lt": "na",
    "kw": "na",
    "ee": "na",
    "hu": "na",
    "om": "na",
    "ru": "na",
    "sk": "na",
    "bh": "na",
    "ma": "na",
    "qa": "na",
    "ir": "na",
    "il": "na",
    "bz": "na",
    "cr": "na",
    "sv": "na",
    "gt": "na",
    "hn": "na",
    "ni": "na",
    "pa": "na",
    "ai": "na",
    "ag": "na",
    "aw": "na",
    "bs": "na",
    "bb": "na",
    "bm": "na",
    "vg": "na",
    "ky": "na",
    "cu": "na",
    "dm": "na",
    "do": "na",
    "gd": "na",
    "gp": "na",
    "ht": "na",
    "jm": "na",
    "mq": "na",
    "ms": "na",
    "an": "na",
    "pr": "na",
    "kn": "na",
    "lc": "na",
    "vc": "na",
    "tt": "na",
    "tc": "na",
    "vi": "na",
    "ar": "na",
    "bo": "na",
    "cl": "na",
    "co": "na",
    "ec": "na",
    "fk": "na",
    "gf": "na",
    "gy": "na",
    "py": "na",
    "pe": "na",
    "sr": "na",
    "uy": "na",
    "ve": "na",
    "mo": "na",
    "kp": "na",
    "mn": "na",
    "ph": "na",
    "bn": "na",
    "kh": "na",
    "tp": "na",
    "id": "na",
    "la": "na",
    "mm": "na",
    "vn": "na",
    "pk": "na",
    "bd": "na",
    "bt": "na",
    "mv": "na",
    "np": "na",
    "lk": "na",
    "kz": "na",
    "kg": "na",
    "tj": "na",
    "uz": "na",
    "tm": "na",
    "af": "na",
    "am": "na",
    "az": "na",
    "cy": "na",
    "ge": "na",
    "iq": "na",
    "jo": "na",
    "lb": "na",
    "ps": "na",
    "sa": "na",
    "sy": "na",
    "ye": "na",
    "is": "na",
    "gl": "na",
    "fo": "na",
    "fi": "na",
    "by": "na",
    "md": "na",
    "ie": "na",
    "mc": "na",
    "al": "na",
    "ad": "na",
    "ba": "na",
    "bg": "na",
    "hr": "na",
    "gi": "na",
    "gr": "na",
    "mk": "na",
    "mt": "na",
    "ro": "na",
    "sm": "na",
    "rs": "na",
    "si": "na",
    "va": "na",
    "dz": "na",
    "eg": "na",
    "ly": "na",
    "sd": "na",
    "tn": "na",
    "bi": "na",
    "dj": "na",
    "er": "na",
    "et": "na",
    "ke": "na",
    "rw": "na",
    "sc": "na",
    "so": "na",
    "tz": "na",
    "ug": "na",
    "td": "na",
    "cm": "na",
    "cf": "na",
    "cg": "na",
    "dr": "na",
    "cq": "na",
    "ga": "na",
    "st": "na",
    "bj": "na",
    "bf": "na",
    "ic": "na",
    "cv": "na",
    "gm": "na",
    "gh": "na",
    "gw": "na",
    "gn": "na",
    "ci": "na",
    "lr": "na",
    "ml": "na",
    "mr": "na",
    "ne": "na",
    "ng": "na",
    "sn": "na",
    "sl": "na",
    "tg": "na",
    "eh": "na",
    "ao": "na",
    "bw": "na",
    "km": "na",
    "ls": "na",
    "mg": "na",
    "mw": "na",
    "mu": "na",
    "mz": "na",
    "na": "na",
    "re": "na",
    "za": "na",
    "sh": "na",
    "sz": "na",
    "zm": "na",
    "zw": "na",
    "cx": "na",
    "cc": "na",
    "ck": "na",
    "fj": "na",
    "pf": "na",
    "gu": "na",
    "ki": "na",
    "mh": "na",
    "fm": "na",
    "nr": "na",
    "nc": "na",
    "nz": "na",
    "nu": "na",
    "nf": "ap",
    "pw": "ap",
    "pg": "ap",
    "pn": "ap",
    "ws": "ap",
    "sb": "ap",
    "mp": "ap",
    "tk": "ap",
    "to": "ap",
    "tv": "ap",
    "vu": "ap",
    "wf": "ap",
}

_FIND_NOT_USED_API_REQUEST = [
    r"/api/appsvr/app.do",
    r"/api/appsvr/app/config",
    r"/api/appsvr/device/blacklist/check",
    r"/api/appsvr/improve",
    r"/api/appsvr/improve/accept",
    r"/api/appsvr/notice/home",
    r"/api/appsvr/oauth_callback",
    r"/api/appsvr/ota/firmware",
    r"/api/appsvr/service/list",
    r"/api/basis/dc/get-by-area",
    r"/api/dim/devmanager.do",
    r"/api/ecms/app/ad/res",
    r"/api/ecms/app/ad/res/v2",
    r"/api/ecms/app/element/hint",
    r"/api/ecms/app/resources",
    r"/api/ecms/file/get/",
    r"/api/homed/device/move",
    r"/api/homed/home/create",
    r"/api/homed/home/delete",
    r"/api/homed/home/list",
    r"/api/homed/member/list",
    r"/api/iot/devmanager.do",
    r"/api/lg/log.do",
    r"/api/neng/message/getlist",
    r"/api/neng/message/getShareMsgs",
    r"/api/neng/message/hasUnreadMsg",
    r"/api/neng/message/read",
    r"/api/neng/v2/message/push",
    r"/api/neng/v3/message/latest_by_did",
    r"/api/neng/v3/message/list",
    r"/api/neng/v3/product/msg/tabs",
    r"/api/neng/v3/shareMsg/hasUnreadMsg",
    r"/api/pim/dictionary/getErrDetail",
    r"/api/pim/file/get/",
    r"/api/pim/product/getConfigGroups",
    r"/api/pim/product/getConfignetAll",
    r"/api/pim/product/getProductIotMap",
    r"/api/pim/product/software/config/batch",
    r"/api/pim/voice/get",
    r"/api/rapp/sds/user/data/del",
    r"/api/rapp/sds/user/data/map/get",
    r"/api/sds/baidu/audio/getcred",
    r"/api/users/user.do",
    r"/bot/remove/",
    r"/client/remove/",
    r"/config/Android.conf",
    r"/list_routes",
    r"/lookup.do",
    r"/newauth.do",
    r"/restart_",
    r"/sa",
    r"/upload/global/",
    r"/v1/global/auth/getAuthCode",
    r"/v1/private/(.*?)//user/getMyUserMenuInfo",
    r"/v1/private/(.*?)/ad/getAdByPositionType",
    r"/v1/private/(.*?)/ad/getBootScreen",
    r"/v1/private/(.*?)/agreement/getUserAcceptInfo",
    r"/v1/private/(.*?)/campaign/homePageAlert",
    r"/v1/private/(.*?)/common/checkAPPVersion",
    r"/v1/private/(.*?)/common/checkVersion",
    r"/v1/private/(.*?)/common/getAboutBriefItem",
    r"/v1/private/(.*?)/common/getAgreementURLBatch",
    r"/v1/private/(.*?)/common/getAreas",
    r"/v1/private/(.*?)/common/getBottomNavigateInfoList",
    r"/v1/private/(.*?)/common/getConfig",
    r"/v1/private/(.*?)/common/getSystemReminder",
    r"/v1/private/(.*?)/common/getTimestamp",
    r"/v1/private/(.*?)/common/getUserConfig",
    r"/v1/private/(.*?)/common/uploadDeviceInfo",
    r"/v1/private/(.*?)/intl/member/basicInfo",
    r"/v1/private/(.*?)/intl/member/signStatus",
    r"/v1/private/(.*?)/message/getMsgList",
    r"/v1/private/(.*?)/message/hasUnreadMsg",
    r"/v1/private/(.*?)/osmall/getCountryConfig",
    r"/v1/private/(.*?)/osmall/index/getLayout",
    r"/v1/private/(.*?)/osmall/proxy/cart/get-count",
    r"/v1/private/(.*?)/osmall/proxy/my/get-user-center-coupon-list",
    r"/v1/private/(.*?)/osmall/proxy/order/list",
    r"/v1/private/(.*?)/osmall/proxy/v2/web/benefit/get-benefits",
    r"/v1/private/(.*?)/shop/getCnWapShopConfig",
    r"/v1/private/(.*?)/user/acceptAgreementBatch",
    r"/v1/private/(.*?)/user/changeArea",
    r"/v1/private/(.*?)/user/checkAgreement",
    r"/v1/private/(.*?)/user/checkAgreementBatch",
    r"/v1/private/(.*?)/user/checkLogin",
    r"/v1/private/(.*?)/user/getAuthCode",
    r"/v1/private/(.*?)/user/getMyUserMenuInfo",
    r"/v1/private/(.*?)/user/getUserAccountInfo",
    r"/v1/private/(.*?)/user/getUserMenuInfo",
    r"/v1/private/(.*?)/user/login",
    r"/v1/private/(.*?)/user/logout",
    r"/v1/private/(.*?)/user/queryChangeArea",
    r"/v1/private/(.*?)/userSetting/getMsgReceiveSetting",
    r"/v1/private/(.*?)/userSetting/getSuggestionSetting",
    r"/v1/private/(.*?)/userSetting/saveUserSetting",
    r"/v2/private/(.*?)/common/getBottomNavigateInfoList",
    r"/v2/private/(.*?)/member/getExpByScene",
    r"/v2/private/(.*?)/message/hasMoreUnReadMsg",
    r"/v2/private/(.*?)/message/moduleConfiguration",
    r"/v2/private/(.*?)/message/waterfallFlow",
    r"/v2/private/(.*?)/user/checkAgreementBatch",
    r"/v2/private/(.*?)/user/checkLogin",
    r"/v3/private/(.*?)/common/getBottomNavigateInfoList",
]
