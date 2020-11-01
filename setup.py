# !/usr/bin/env python

from distutils.core import setup

setup(
    name='Webly Dataset Creator',
    version='0.1.0',
    author='Justin Rokisky',
    author_email='jrokisky831@gmail.com',
    packages=['webly-dataset-creator'],
    scripts=['webly-dataset-creator/webly-dataset-creator.py'],
    description='Helper functions for creating a webly dataset.',
    install_requires=[
        "flickrapi",
        "bing-image-downloader",
        "yandex-images-download"
    ],
)



