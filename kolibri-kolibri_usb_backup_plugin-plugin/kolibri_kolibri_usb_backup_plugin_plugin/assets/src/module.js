import RootVue from './views/KolibriUsbBackupPluginPluginIndex';


import logger from 'kolibri.lib.logging';
import Vue from 'kolibri.lib.vue';
import KolibriModule from 'kolibri_module';

const logging = logger.getLogger(__filename);

class KolibriUsbBackupPluginPluginModule extends KolibriModule {
  /*
   Callback invoked when this module is initialized.
   */
  initialize() {
    logging.debug('Module is initialized.');
  }

  /*
   Callback invoked when this module is registered.
   */
  ready() {
    this.rootvue = new Vue({
      el: 'rootvue',
      render: createElement => createElement(RootVue),
    });
  }
}




const kolibriUsbBackupPluginPlugin = new KolibriUsbBackupPluginPluginModule();

export { kolibriUsbBackupPluginPlugin as default };
