import datetime
from typing import Optional, Literal


def get_datetime(delta: int, time_format: Optional[Literal["使用斜杠分隔符", "使用中划线风格", "使用datatime格式", "使用年月日格式"]] = "使用中划线风格"):
    if time_format == "使用斜杠分隔符":
        return (datetime.datetime.now() + datetime.timedelta(days=delta)).strftime("%Y/%m/%d")
    elif time_format == "使用中划线风格":
        return (datetime.datetime.now() + datetime.timedelta(days=delta)).strftime("%Y-%m-%d")
    elif time_format == "使用datatime格式":
        return datetime.datetime.now() + datetime.timedelta(days=delta)
    elif time_format == "使用年月日格式":
        return (datetime.datetime.now() + datetime.timedelta(days=delta)).strftime("%Y年%m月%d日")
    else:
        return (datetime.datetime.now() + datetime.timedelta(days=delta)).strftime(str(time_format))

def get_current_timestamp():
    return datetime.datetime.now().timestamp()
