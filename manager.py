# -*- coding:utf-8 -*-

# author: Cone
# datetime: 2020-03-16 08:55
# software: PyCharm
from cone.spider_ex import logger
from platforms import Platform

import os
import importlib


class PlatformManager(object):
    _platforms = {}   # [{'name': obj}]  每一个搜索有唯一的搜索名，根据搜索名来查找
    _platform_modules = set()

    searcher_path = 'platforms'

    def __init__(self):
        super().__init__()
        self.load_from_directory(self.searcher_path)
        logger.info('%s platforms loaded', len(self._platforms))

    def load_from_file(self, platform_file):
        try:
            module = platform_file.split('.')[0].replace('\\', '.').replace('/', '.')
            searcher_module = importlib.import_module(module)
        except Exception as e:
            logger.info("Load error from %s:%s", platform_file, str(e))
            return None
        for _, obj in searcher_module.__dict__.items():
            if type(obj).__name__ == 'type' and issubclass(obj, Platform) \
                    and obj.__name__ not in (Platform.__name__,
                                             ):
                name = getattr(obj, 'name')
                if not name:
                    logger.info("%s from %s must have a name", obj.__name__, platform_file)
                elif name not in self._platforms:
                    self._platforms[name] = obj
                    logger.info("Load %s<%s> from %s success", obj.__name__, obj.name, platform_file)
        # else:
        #     logger.info("Searcher subclass not found in %s" % searcher_file)

    def load_from_directory(self, directory):
        platform_list = os.listdir(directory)
        for searcher_path in platform_list:
            if searcher_path.startswith('_'):    # 以该字符开始的任意文件或文件夹都不考虑
                continue
            path = os.path.join(directory, searcher_path)
            if os.path.isdir(path):
                self.load_from_directory(path)
            elif not searcher_path.endswith('.py'):
                continue
            else:
                self.load_from_file(path)

    def find_platform(self, platform):
        return self._platforms[platform]

    def get_platforms(self):
        return self._platforms


PlatformManager = PlatformManager()
