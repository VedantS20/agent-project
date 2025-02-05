<template>
  <!-- <v-card class="ma-2" elevation-10 min-height="400px" max-width="300px">
    <v-img max-height="200px" max-width="300px" :src="image"></v-img>
    <v-card-title class="text-wrap"> {{ name }} </v-card-title>
    <v-card-subtitle> {{ price }} Rs </v-card-subtitle>
    <v-card-text class="text-justify description-text">
      {{ description }}
    </v-card-text>
  </v-card> -->
  <v-card class="mx-auto" max-width="400">
    <v-img
      max-height="200px"
      max-width="300px"
      class="align-end text-white"
      height="200"
      :src="image"
    >
    </v-img>
    <v-card-title class="text-subtitle-2 font-weight-bold text-wrap">{{
      name
    }}</v-card-title>
    <v-card-subtitle class="pt-4"> ₹{{ price }} </v-card-subtitle>

    <v-card-text class="text-justify description-text">
      {{ description }}
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  props: {
    image: String,
    name: String,
    price: Number,
    description: String,
  },
};
</script>

<style lang="scss">
.description-text {
  max-height: 200px;
  overflow-y: auto;
}
</style>
