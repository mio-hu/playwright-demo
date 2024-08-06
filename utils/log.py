# -*- coding: utf-8 -*-

import time
import os
from utils.path import LOG_DIR, get_path
from loguru import logger

class Log:
    def __new__(cls, log_name):
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)
        log_file = get_path("/log/{}_{}.log".format(log_name, time.strftime("%Y%m%d")))
        logger.add(log_file, encoding="utf-8", enqueue=True, retention='7 days')
        return logger

Log = Log('log')