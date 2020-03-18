# -*- coding:utf-8 -*-

# author: Cone
# datetime: 2020-03-15 19:34
# software: PyCharm
from manager import PlatformManager
from cone.spider_ex import logger
import json
from settings import ENABLE_CONFIGS, AUTHOR, CATEGORY, TAG, FILENAME
import settings
from selenium import webdriver


def get_title_content_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        title, content = lines[0].strip('#').strip(), ''.join(lines[1:])
    return title, content


class PostBot:

    def __init__(self):
        self._driver = webdriver.Chrome()

    def post(self):
        platforms = []
        if FILENAME is not None:
            settings.TITLE, settings.CONTENT = get_title_content_from_file(FILENAME)
        logger.info("目标平台: %s", [x['platform'] for x in ENABLE_CONFIGS])
        logger.info("目标文章: %s", json.dumps({
            'title': settings.TITLE,
            'content': settings.CONTENT,
            'tag': TAG,
            'category': CATEGORY,
            'author': AUTHOR
        }, indent=4, ensure_ascii=False))
        for config in ENABLE_CONFIGS:
            platforms.append(PlatformManager.find_platform(config['platform']).
                             instance(driver=self._driver,
                                      title=settings.TITLE,
                                      content=settings.CONTENT,
                                      category=CATEGORY,
                                      tag=TAG,
                                      author=AUTHOR,
                                      auth=config['auth']
                                      ))
        for platform in platforms:
            platform.post()
            platform.print_logs()
        self._driver.close()
        self._driver.quit()


if __name__ == '__main__':
    settings.TITLE, settings.CONTENT = get_title_content_from_file('/Users/cone/cone/me/projects/auto-post/post_uploads/test.md')
    postbot = PostBot()
    postbot.post()




