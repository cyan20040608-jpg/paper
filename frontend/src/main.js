import { createApp } from "vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import App from "./App.vue";
import router from "./router";
import "./assets/styles/base.css";
import "./assets/styles/admin.css";

createApp(App).use(router).use(ElementPlus).mount("#app");
