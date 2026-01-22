from __future__ import absolute_import, print_function, unicode_literals

from kolibri.core.webpack.hooks import WebpackBundleHook
from kolibri.plugins import KolibriPluginBase


class KolibriUsbBackupPluginPlugin(KolibriPluginBase):
    pass


class KolibriUsbBackupPluginPluginAsset(WebpackBundleHook):
    bundle_id = "kolibri_kolibri_usb_backup_plugin_plugin_module"
