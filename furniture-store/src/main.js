import { createApp } from "vue";
import "./style.css";
import App from "./App.vue";
import "@mdi/font/css/materialdesignicons.css";
import "vuetify/styles";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { createRouter, createWebHashHistory } from "vue-router";
import HomePage from "./components/homePage.vue";
import Inventory from "./components/inventory.vue";

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: "/", name: "HomePage", component: HomePage },
    { path: "/inventory", name: "Inventory", component: Inventory },
  ],
});

const vuetify = createVuetify({
  components,
  directives,
});

createApp(App).use(vuetify).use(router).mount("#app");
