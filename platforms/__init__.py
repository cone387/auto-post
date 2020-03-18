# -*- coding:utf-8 -*-

# author: Cone
# datetime: 2020-03-15 19:22
# software: PyCharm
import json
import time
import traceback

from cone.spider_ex import logger
from selenium.webdriver import Chrome


def post_step(method):
    def step_wrapper(platform):
        return method(platform)
    step_wrapper.wrapped_name = method.__name__
    return step_wrapper


class Step(dict):

    def __init__(self, name=None, method=None, succeed=None, failed=None, max_invoke_times=3, sleep=0, selector={}):
        assert name and method and succeed
        self['name'] = name
        self['method'] = method
        self['succeed'] = succeed
        self['failed'] = failed or 'failed'
        self['max_invoke_times'] = max_invoke_times
        self['selector'] = selector
        self['sleep'] = sleep


class StepGroup:
    def __init__(self, *steps):
        self._steps: list[Step] = list(steps)

    def insert(self, index, step: Step):
        self._steps.insert(index, step)

    def add(self, step: Step):
        self._steps.append(step)

    def pop(self, index=0):
        return self._steps.pop(index)

    def insert_after(self, step_name, step: Step):
        for index, prev_step in enumerate(self._steps):
            if prev_step.name == step_name:
                break
        self.insert(index+1, step)

    def insert_before(self, step_name, step: Step):
        for index, prev_step in enumerate(self._steps):
            if prev_step.name == step_name:
                break
        self.insert(index, step)

    def step_names(self):
        return [step.name for step in self._steps]

    def get_step(self, step_method):
        for step in self._steps:
            if step['method'] == step_method:
                return step
        else:
            logger.error("step not found by %s", step_method)

    def get_steps(self):
        return self._steps

    def __iter__(self):
        for i in self._steps:
            yield i

    def __len__(self):
        return len(self._steps)


class Platform:
    start_url = None
    name = None
    required_attrs = ['title', 'content']
    max_invoke_times = 3
    steps = StepGroup(
        Step(name='访问登录页', method='request_url', succeed='input_username', sleep=2),
        Step(name='输入账号', method='input_username', succeed='input_password', max_invoke_times=3),
        Step(name='输入密码', method='input_password', succeed='click_login'),
        Step(name='点击登录', method='click_login', succeed='click_write_post'),
        Step(name='点击写文章', method='click_write_post', succeed='input_post'),
        Step(name='输入文章', method='input_post', succeed='click_post'),
        Step(name='点击发布', method='click_post', succeed='close'),
    )

    def __init__(self, title=None, content=None, category=None, tag=None, driver=None, author=None, auth=None):
        self.title = title
        self.content = content
        self.category = category
        self.tag = tag
        self.logs = []
        self.driver: Chrome = driver
        self.author = author
        self.auth = auth or {}
        self.check_filed()
        self._step = None

    def request_url(self):
        self.driver.get(self.start_url)
        return True

    def find_element(self, selector, value):
        method = getattr(self.driver, f'find_element_by_{selector}')
        try:
            element = method(value)
            return element
        except Exception as e:
            logger.error("[%s][%s]find element error, %s", self.name, self._step['name'], str(e))
            return None

    def input(self, message):
        selector: dict = self._step['selector']
        for selector, value in selector.items():
            element = self.find_element(selector, value)
            if element:
                element.send_keys(message)
                return True
        else:
            logger.error("[%s][%s]input account element not found", self.name, self._step['name'])
            return False

    def input_username(self):
        return self.input(self.auth.get('username'))

    def input_password(self):
        return self.input(self.auth.get('password'))

    def click_login(self):
        return True

    def click_write_post(self):
        return True

    def click_post(self):   # 发布
        return True

    def input_post(self):
        pass

    def post(self):
        logger.info('[%s]Post have %s step', self.name, len(self.steps))
        if len(self.steps):
            step = self.steps.pop(0)
        index = 1
        while step:
            self._step = step
            logger.info("[%s][Step%s]%s...", self.name, index, step['name'])
            log = {'name': step['name']}
            try:
                method = getattr(self, step['method'])
                if method.invoke_times <= step['max_invoke_times']:
                    result = method()
                    if result:
                        next_method = step['succeed']
                    else:
                        next_method = step['failed']
                else:
                    log['success'] = False
                    log['error'] = 'Max invoke times'
                    break
                log['success'] = True
            except Exception as e:
                log['success'] = False
                log['msg'] = traceback.format_exc()
                method.invoke_times += 1
                next_method = step['failed']
            if step.get('sleep', 0):
                time.sleep(step['sleep'])
            self.logs.append(log)
            step = self.steps.get_step(next_method)
            print(next_method, step)
            if not step:
                self.failed()
                break
            logger.info("[%s][Step%s]%s -> %s, Next step ", self.name, index, self._step,
                        '成功' if log['success'] else '失败', step['name'])
            index += 1

    def check_filed(self):
        assert self.start_url is not None, '[%s]must have a start_url' % self.name
        for attr in self.required_attrs:
            value = getattr(self, attr, None)
            assert value is not None, '[%s]%s cant be none' % (self.name, attr)

    def failed(self):
        pass

    def close(self):
        logger.info("[%s]post close", self.name)

    def print_logs(self):
        logger.info('[%s]%s', self.name, json.dumps(self.logs, indent=4, ensure_ascii=False))

    @classmethod
    def instance(cls, **kwargs):
        for step in cls.steps.get_steps():
            method = getattr(cls, step['method'])
            succeed_method = getattr(cls, step['succeed'])
            failed_method = getattr(cls, step['failed'])
            if method.__name__ != 'step_wrapper':
                t = post_step(method)
                t.max_invoke_times = step['max_invoke_times']
                t.invoke_times = 1
                setattr(cls, method.__name__, t)
            if succeed_method.__name__ != 'step_wrapper':
                t = post_step(succeed_method)
                t.max_invoke_times = step['max_invoke_times']
                t.invoke_times = 1
                setattr(cls, succeed_method.__name__, t)
            if failed_method.__name__ != 'step_wrapper':
                t = post_step(failed_method)
                t.max_invoke_times = step['max_invoke_times']
                t.invoke_times = 1
                setattr(cls, failed_method.__name__, t)
        return cls(**kwargs)


