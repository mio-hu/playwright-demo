# -*- coding: utf-8 -*-

import os
import yaml.scanner
import ruamel.yaml
from utils.path import get_path


class Yaml:
    """ 获取 yaml 文件中的数据 """
    @classmethod
    def get_data(cls, file_path) -> dict:
        """
        获取 yaml 中的数据
        :param: file_path:
        :return:
        """
        file_path = get_path(file_path)
        # 判断文件是否存在
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as data:
                res = yaml.safe_load(data)
        else:
            raise FileNotFoundError("文件路径不存在")
        return res

    @classmethod
    def update_data(cls, file_path, key, value):
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True  # 保留引号
        yaml.indent(mapping=2, sequence=4, offset=2)  # 设置缩进
        file_path = get_path(file_path)

        with open(file_path, 'r') as file:
            data = yaml.load(file)  # 加载 YAML 数据

        if data is None:
            data = {}  # 如果文件内容为空，则创建一个空字典

        # 更新键值对
        parts = key.split('.')
        if len(parts) == 1:
            data[key] = value
        else:
            nested_dict = data
            for part in parts[:-1]:
                nested_dict = nested_dict.setdefault(part, {})
            nested_dict[parts[-1]] = value

        with open(file_path, 'w') as file:
            yaml.dump(data, file)
