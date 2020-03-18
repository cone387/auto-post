# -*- coding:utf-8 -*-

# author: Cone
# datetime: 2020-03-16 09:22
# software: PyCharm
import argparse
from config import CONFIGS


PLATFORM = None
PRIVATE = None
TAG = None
CATEGORY = None
CONTENT = None
TITLE = None
AUTHOR = None
FILENAME = None


def load_settings():
    parser = argparse.ArgumentParser(description='auto-post client')
    parser.add_argument("-P", help="进程数量", dest='PROCESS_NUM', default=1, type=int, required=False)
    parser.add_argument('--title', '-t', help='标题', dest="TITLE", default=None, required=False)
    parser.add_argument('--content', '-c', help='内容', dest="TITLE", default=None, required=False)
    parser.add_argument('--author', '-a', help='作者', dest="AUTHOR", default='Cone', required=False)
    parser.add_argument('--category', help='类别', dest="CATEGORY", required=False)
    parser.add_argument('--tag', help='标签', dest="TAG", required=False)
    parser.add_argument('--private', help='仅自己可见', dest="PRIVATE", required=False)
    parser.add_argument('--filename', '-f', dest='FILENAME', default=None, required=False)
    # parser.add_argument('--priva', help='仅自己可见', dest="PRIVATE", required=False)
    parser.add_argument('--platform', help='p', dest="PLATFORM", default='enables', required=False)
    args = parser.parse_args()
    return args.__dict__.copy()


for k, v in load_settings().items():
    if v is not None:
        locals()[k] = v

if PLATFORM == 'all':
    ENABLE_CONFIGS = CONFIGS
elif PLATFORM == 'enables':
    ENABLE_CONFIGS = [x for x in CONFIGS if x.get('enable', False)]
else:
    platforms = PLATFORM.split(',')
    exists_platforms = [x['platform'] for x in CONFIGS]
    ENABLE_CONFIGS = [x for x in CONFIGS if x['platform'] in platforms]
    for platform in platforms:
        if platform not in exists_platforms:
            print(platform, 'not found')
            exit(1)


