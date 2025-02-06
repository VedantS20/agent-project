<template>
  <div class="card-container">
    <v-row class="mb-6" no-gutters>
      <v-col :cols="3" v-for="product in products" :key="product._id">
        <ItemCardVue
          class="ma-2"
          :name="product.name"
          :description="product.description"
          :price="product.price"
          :image="product.image"
        />
      </v-col>
    </v-row>
  </div>
</template>

<script>
import ItemCardVue from "./itemCard.vue";

export default {
  components: { ItemCardVue },
  data() {
    return {
      products: [],
    };
  },
  mounted() {
    this.fetchProducts();
  },
  methods: {
    async fetchProducts() {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_BACKEND_URL}/products`
        );
        if (response.ok) {
          const data = await response.json();
          this.products = data.products; // Store fetched products in Vue state
        } else {
          console.error("Error fetching products:", await response.text());
        }
      } catch (error) {
        console.error("Request error:", error);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.card-container {
}
</style>
