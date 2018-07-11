# encoding : utf-8

import sys
from setuptools import setup

with open('README.md', 'r') as f:
    README = f.read()

sys.path.append("./test")

setup(
    name='slack_notifier',
    version='0.0.1',
    description='Slack notifier with Incoming Webhook',
    long_description=README,
    packages=['slack_notifier', 'test'],
    author='Takashi Yamamura',
    author_email='t_yamamura@pluto.ai.kyutech.ac.jp',
    # url='http://gitlab.pluto.ai.kyutech.ac.jp/t_yamamura/ShimadaNLPGuide2017',
    test_suite='test_slack_notifier'
    )