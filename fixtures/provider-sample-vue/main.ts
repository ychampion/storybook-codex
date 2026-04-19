import { createApp } from 'vue';
import { createPinia } from 'pinia';
import router from './router';
import i18n from './i18n';
import App from './App.vue';

const pinia = createPinia();

createApp(App).use(router).use(pinia).use(i18n).mount('#app');
