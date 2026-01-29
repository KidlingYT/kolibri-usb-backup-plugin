import KolibriApp from 'kolibri-app';
import RootVue from './views/KolibriUsbBackupPluginPluginIndex';
import routes from './routes';

class UsbBackupModule extends KolibriApp {
  get routes() {
    return routes;
  }
  get RootVue() {
    return RootVue;
  }
}

export default new UsbBackupModule();