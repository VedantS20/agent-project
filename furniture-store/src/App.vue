<template>
  <v-responsive class="border rounded">
    <v-app class="position-relative">
      <v-app-bar color="brown-lighten-2">
        <template v-slot:prepend>
          <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
        </template>

        <v-app-bar-title>FutureFurnish</v-app-bar-title>
        <!-- <template v-slot:append>
          <v-app-bar-nav-icon to="/"
            ><v-icon>mdi-cart</v-icon>
          </v-app-bar-nav-icon>
        </template> -->
      </v-app-bar>
      <v-navigation-drawer v-model="drawer">
        <v-list-item class="mt-4">
          <RouterLink to="/">Home</RouterLink>
        </v-list-item>
        <v-list-item class="mt-4">
          <RouterLink to="/inventory">Manage Inventory</RouterLink>
        </v-list-item>
      </v-navigation-drawer>
      <v-main>
        <RouterView />
      </v-main>
    </v-app>
    <v-fab
      class="me-4 mic-btn"
      icon="mdi-microphone"
      size="x-large"
      :color="isAssistantStarted ? 'red' : 'success'"
      @click="isAssistantStarted ? stopVoiceAssistant() : startVoiceAssistant()"
    ></v-fab>
  </v-responsive>
</template>

<script>
// import HomePage from "./components/homePage.vue";
// import Inventory from "./components/inventory.vue";
import Vapi from "@vapi-ai/web";
const vapi = new Vapi("e3d9175f-9ca9-46d6-9be8-aff539e4e5f9");
const assistant_id = "d650718b-32bb-478c-8494-5c3f04da631a";

export default {
  data() {
    return {
      drawer: false,
      isAssistantStarted: false,
    };
  },
  methods: {
    startVoiceAssistant() {
      this.isAssistantStarted = true;
      vapi.start(assistant_id);
    },
    stopVoiceAssistant() {
      this.isAssistantStarted = false;
      vapi.stop();
    },
  },
};
</script>

<style lang="scss" scoped>
.mic-btn {
  position: fixed;
  bottom: 50px;
  left: 50%;
}
</style>
