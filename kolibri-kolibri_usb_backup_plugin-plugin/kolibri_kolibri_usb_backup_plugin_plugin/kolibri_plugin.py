from __future__ import absolute_import, print_function, unicode_literals

from kolibri.core.webpack.hooks import WebpackBundleHook
from kolibri.plugins import KolibriPluginBase
from kolibri.plugins.hooks import register_hook


class KolibriUsbBackupPluginPlugin(KolibriPluginBase):
    translated_view_urls = "urls"


@register_hook
class KolibriUsbBackupPluginPluginAsset(WebpackBundleHook):
    bundle_id = "app"
