#! -*- coding: utf-8 -*-

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='djchat',
    version='0.1',
    packages=['djchat'],
    description='Django based package to enable Async chat functionality using API and Django Channels with ASGI interface and live notifications enabled in it.',
    long_description=README,
    author='Naresh Kumar Jaggi',
    author_email='naresh.jaggi@exiverprojects.com',
    url='https://bitbucket.org/exiver/djchat/src/',
    license='MIT',
    install_requires=[
        'Django==3.0.2',
        'channels==2.4.0'
    ]
)
