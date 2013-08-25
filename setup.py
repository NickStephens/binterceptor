#!/usr/bin/python

import shutil
from distutils.core import setup

shutil.copyfile("binterceptor.py", "binterceptor/binterceptor")

setup(name='binterceptor',
      version='0.2',
      author='Nick Stephens',
      description="An interception proxy specializing in binary protocols",
      packages=['binterceptor'],
      scripts=["binterceptor/binterceptor"],
     )
