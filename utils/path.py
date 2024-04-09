# -*- coding: utf-8 -*-


import os
from typing import Text

# 项目的跟路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 日志目录
LOG_DIR = os.path.join(ROOT_DIR, "logs")
# 配置文件目录
CONF_DIR = os.path.join(ROOT_DIR, "conf")
# 测试数据目录
CASE_DATA_DIR = os.path.join(ROOT_DIR, "data")
# 测试用例目录
TESTCASES_DIR = os.path.join(ROOT_DIR, "testcases")
# 测试报告目录
REPORT_DIR = os.path.join(ROOT_DIR, "reports")
# pytest测试报告目录
TEMP_REPORT_DIR = os.path.join(REPORT_DIR, "temp")
# HTML测试报告目录
HTML_REPORT_DIR = os.path.join(REPORT_DIR, "html")

def format_path(path: Text) -> Text:
    """兼容 windows 和 linux 不同环境的操作系统路径 """
    if "/" in path:
        path = os.sep.join(path.split("/"))
    if "\\" in path:
        path = os.sep.join(path.split("\\"))
    if ROOT_DIR in path:
        return path
    else:
        return ROOT_DIR + path



