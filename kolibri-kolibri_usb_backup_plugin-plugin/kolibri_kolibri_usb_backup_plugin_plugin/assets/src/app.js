import KolibriApp from 'kolibri-app';
import RootVue from './views/KolibriUsbBackupPluginPluginIndex.vue';
import routes from './routes';
import pluginModule from './modules/pluginModule';

class UsbBackupModule extends KolibriApp {
  get routes() {
    return routes;
  }
  get RootVue() {
    return RootVue;
  }
  get pluginModule() {
    return pluginModule;
  }
}

export default  new UsbBackupModule();;