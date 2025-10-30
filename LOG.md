## Here is the log of the progress on [this issue](https://github.com/learningequality/kolibri/issues/9253)

1. Generated the hook using [this plugin creator](https://github.com/learningequality/cookiecutter-kolibri-plugin)

2. Discovered some outdated syntax in the imports generated in [setup.py](https://github.com/KidlingYT/kolibri-usb-backup-plugin/commit/ddb8faea6d6a303fadd03ed81285acf7ebd84f84)

3. From the directory of the **plugin** run:

```sh
cd kolibri_kolibri_usb_backup_plugin_plugin
pip install -e .
```

4. From the directory kolibri (root one), with your pyenv vitrual env running, run:

```sh
kolibri plugin enable kolibri_kolibri_usb_backup_plugin_plugin
```