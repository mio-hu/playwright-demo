# coding:utf-8
"""
数据库操作模块
"""
import os

import pymysql
import yaml
from common.path import DB_CONF_PATH


class DbUtils(object):
    def __init__(self, db_name):
        self.conn = self.create_connection(db_name)
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    @staticmethod
    def create_connection(db_name):
        with open(DB_CONF_PATH) as f:
            db_info = yaml.safe_load(f)
            return pymysql.connect(**db_info[db_name], autocommit=True)

    def execute_query(self, sql, parameter=None, fetchone=False):
        if parameter:
            self.cur.execute(sql, parameter)
        else:
            self.cur.execute(sql)

        if fetchone:
            return self.cur.fetchone()
        else:
            return self.cur.fetchall()

    def execute_commit(self, sql, parameter=None):
        if parameter:
            self.cur.execute(sql, parameter)
        else:
            self.cur.execute(sql)

    def execute_many_commit(self, sql, parameter):
        self.cur.executemany(sql, parameter)
