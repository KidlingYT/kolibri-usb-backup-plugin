## Setup

> Make sure you are in `~/kolibri-usb-backup-plugin/kolibri-kolibri_usb_backup_plugin-plugin`

1. Activate the pyenv virtualenv

```sh
pyenv activate kolibri-py3.9
```

2. Pip Install

```sh
pip install -e .
```

3. Go to Kolibri

```sh
cd ~/kolibri
```

4. Enable the plugin

```sh
kolibri plugin enable kolibri_kolibri_usb_backup_plugin_plugin
```

5. Sometimes, you have to run this cmd, then start the server:

```sh
cd  ~/kolibri
yarn run kolibri-build dev --file ~/plugin_build.txt
```

6. The plugin page is accessible at http://localhost:8000/en/kolibri_kolibri_usb_backup_plugin_plugin/
