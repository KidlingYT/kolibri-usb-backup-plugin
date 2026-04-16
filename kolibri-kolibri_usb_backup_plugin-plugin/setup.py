#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from setuptools import find_packages, setup

name = "kolibri-kolibri-usb-backup-plugin-plugin"

setup(
    name=name,
    version="0.1.3",
    description="Kolibri USB Backup Plugin",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Learning Equality",
    author_email="info@learningequality.org",
    url="https://github.com/KidlingYT/kolibri-usb-backup-plugin",
    packages=find_packages(include=[name, f"{name}.*"]),
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    entry_points={
        "kolibri.plugins": [
            "kolibri_kolibri_usb_backup_plugin_plugin = kolibri_kolibri_usb_backup_plugin_plugin",
        ],
    },
)
