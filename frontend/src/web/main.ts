import { createApp } from 'vue';
import { FrappeUI } from 'frappe-ui';
import Badge from 'src/components/Badge.vue';
import FeatherIcon from 'src/components/FeatherIcon.vue';
import { outsideClickDirective } from 'src/utils/outsideClick';
import { fyo } from 'src/initFyo';
import router from 'src/router';
import WebApp from './WebApp.vue';
import { installWebIpc } from './ipc';

installWebIpc();

const app = createApp(WebApp);
app.use(FrappeUI);
app.use(router);
app.component('FeatherIcon', FeatherIcon);
app.component('Badge', Badge);
app.directive('on-outside-click', outsideClickDirective);
app.mixin({
  computed: {
    fyo() {
      return fyo;
    },
    platform() {
      return 'Web';
    },
  },
  methods: { t: fyo.t, T: fyo.T },
});
app.mount('#app');
