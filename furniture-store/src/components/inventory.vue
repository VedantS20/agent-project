<template>
  <div class="d-flex flex-column justify-center ma-10">
    <v-text-field
      v-model="productName"
      variant="outlined"
      label="Product title"
    ></v-text-field>
    <v-textarea
      v-model="productDescription"
      variant="outlined"
      label="Product description"
    ></v-textarea>
    <v-text-field
      v-model="productPrice"
      variant="outlined"
      type="number"
      label="Product price (in Rupees)"
    ></v-text-field>
    <v-select
      label="Product category"
      :items="['wardrobe', 'chair', 'table', 'bed', 'sofa']"
      v-model="productCategory"
    ></v-select>
    <v-file-input
      :loading="isFileUploading"
      variant="outlined"
      label="Product image upload"
      @update:modelValue="handleImageUpload"
    ></v-file-input>
    <a
      v-if="uploadedFileUrl"
      :href="uploadedFileUrl"
      target="_blank"
      class="mt-0 mb-2"
      >Uploaded File Link</a
    >
    <v-btn variant="outlined" color="brown-darken-1" @click="saveInInventory">
      Save
    </v-btn>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isFileUploading: false,
      uploadedFileUrl: undefined,
      productName: undefined,
      productDescription: undefined,
      productPrice: undefined,
      productCategory: undefined,
    };
  },
  methods: {
    async handleImageUpload(file) {
      this.isFileUploading = true;
      console.log(file);
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(
        `${import.meta.env.VITE_BACKEND_URL}/upload_image/`,
        {
          method: "POST",
          body: formData,
        }
      );

      const { url } = await res.json();
      this.uploadedFileUrl = url;
      console.log("Uploaded to:", url);
      this.isFileUploading = false;
    },
    async saveInInventory() {
      if (
        !this.productName ||
        !this.productDescription ||
        !this.productPrice ||
        !this.uploadedFileUrl ||
        !this.productCategory
      ) {
        alert("Please fill all the fields");
      } else {
        const productData = {
          name: this.productName,
          description: this.productDescription,
          price: this.productPrice,
          image: this.uploadedFileUrl,
          category: this.productCategory,
        };

        try {
          const response = await fetch(
            `${import.meta.env.VITE_BACKEND_URL}/add_product/`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(productData),
            }
          );

          if (response.ok) {
            alert("Product added successfully!");
            this.productName = undefined;
            this.productDescription = undefined;
            this.productPrice = undefined;
            this.uploadedFileUrl = undefined;
            this.productCategory = undefined;
          } else {
            console.error("Error adding product:", await response.text());
          }
        } catch (error) {
          console.error("Request error:", error);
        }
      }
    },
  },
};
</script>

<style></style>
