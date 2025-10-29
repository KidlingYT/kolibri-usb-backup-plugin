#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from setuptools import find_packages, setup

name = "kolibri_kolibri_usb_backup_plugin_plugin"


setup(
    name=name,
    version="0.1.0",
    description="Kolibri",
    author="Learning Equality",
    author_email="info@learningequality.org",
    url="https://github.com/KidlingYT/kolibri-usb-backup-plugi",
    packages=find_packages(),
    package_dir={name: name},
    include_package_data=True,
    license="MIT",
    zip_safe=False,
)
