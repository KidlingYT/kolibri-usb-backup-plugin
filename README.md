# kolibri-usb-backup-plugin
This is a kolibri plugin for allowing users to backup volatile data to a usb drive

Creating a plugin

Plugins can be standalone Django apps in their own right, meaning they can define templates, models, new urls, and views just like any other app. Any activated plugin is added to the INSTALLED_APPS setting of Django, so any models, templates, or templatetags defined in the conventional way for Django inside an app will work inside of a Kolibri plugin.

In addition, Kolibri exposes some additional functionality that allows for the core URLs, Django settings, and Kolibri options to be extended by a plugin. These are set

class ExamplePlugin(KolibriPluginBase):
    untranslated_view_urls = "api_urls"
    translated_view_urls = "urls"
    options = "options"
    settings = "settings"


These are all path references to modules within the plugin itself, so options would be accessible on the Python module path as kolibri.plugins.example_plugin.options.

untranslated_view_urls, translated_view_urls should both be standard Django urls modules in the plugin that expose a urlpatterns variable - the first will be mounted as API urls - with no language prefixing, the second will be mounted with language prefixing and will be assumed to contain language specific content.

settings should be a module containing Django settings that should be added to the Kolibri settings. This should not be used to override existing settings (and an error will be thrown if it is used in this way), but rather as a way for plugins to add additional settings to the Django settings. This is particularly useful when a plugin is being used to wrap a Django library that requires its own settings to define its behaviour - this module can be used to add these extra settings in a way that is encapsulated to the plugin.

options should be a module that exposes a variable options_spec which defines Kolibri options specific to this plugin. For more information on how to configure these, see the base Kolibri options specification in kolibri/utils/options.py. These values can then be set either by environment variables or by editing the options.ini file in the KOLIBRI_HOME directory. These options values can also be used inside the settings module above, to provide customization of plugin specific behaviour. These options cannot clash with existing Kolibri options defined in kolibri.utils.options, except in order to change the default value of a Kolibri option - attempting to change any other value of a core Kolibri option will result in a Runtime Error.

A very common use case for plugins is to implement a single page app or other Kolibri module for adding frontend functionality using Kolibri Javascript code. Each of these Javascript bundles are defined in the kolibri_plugin.py file by subclassing the WebpackBundleHook class to define each frontend Kolibri module. This allows a webpack built Javascript bundle to be cross-referenced and loaded into Kolibri. For more information on developing frontend code for Kolibri please see Frontend architecture.

Place to hook into for backups:
https://github.com/learningequality/kolibri/blob/600ec5ce6bc7fd8f03083e2960248cc27911074b/kolibri/core/device/hooks.py
https://github.com/learningequality/kolibri/blob/600ec5ce6bc7fd8f03083e2960248cc27911074b/kolibri/core/device/kolibri_plugin.py
