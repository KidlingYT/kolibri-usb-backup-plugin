

# kolibri_usb_backup_plugin

Note: this plugin was originally generated from a [Cookiecutter template](https://github.com/learningequality/cookiecutter-kolibri-plugin). The instructions below should be updated by the plugin author.

If this plugin is in the `kolibri/plugins` directory of the Kolibri repo, most of the instructions below do not apply.

## Install this plugin in Kolibri

Activate your Kolibri Python virtual environment.

If this plugin is on PyPi, inside your Kolibri virtual environment you can run:

```bash
pip install kolibri_kolibri_usb_backup_plugin_plugin
```

Enable the plugin:

```bash
kolibri plugin kolibri_kolibri_usb_backup_plugin_plugin enable
```

Add the plugin name to `kolibri/build_tools/build_plugins.txt`.

Finally, rebuild and restart Kolibri.


## Install this plugin for development

Clone this repo, install the plugin in your Kolibri Python virtual environment and enable it:


```bash
pip install -e <LOCAL-PATH-TO-REPO>
kolibri plugin kolibri_kolibri_usb_backup_plugin_plugin enable
```


From the Kolibri repo, update any frontend dependenices:

```bash
yarn install
```


## Publishing to PyPi

Follow the instructions above to install the plugin for development.


From the Kolibri directory, build the frontend assets:

```bash
yarn run build
```


Update _setup.py_ to a newer version. From the root of the plugin directory run:

```bash
make release
``
