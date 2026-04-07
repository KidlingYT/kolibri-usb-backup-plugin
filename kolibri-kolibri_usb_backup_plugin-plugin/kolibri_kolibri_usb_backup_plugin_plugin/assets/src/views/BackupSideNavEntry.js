import { registerNavItem } from 'kolibri/composables/useNav';

const sideNavConfig = {
  get label()    { return 'USB Backup'; },
  get icon()     { return 'dashboard'; },
  get url()      { return '/kolibri_kolibri_usb_backup_plugin_plugin/'; },
  get priority() { return 100; },
};

registerNavItem(sideNavConfig);

export default sideNavConfig;