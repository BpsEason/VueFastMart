<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">產品列表</h1>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <ProductCard
        v-for="product in products"
        :key="product.id"
        :product="product"
        @add-to-cart="addToCart"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import ProductCard from '../components/ProductCard.vue'

const products = ref([])

const fetchProducts = async () => {
  try {
    const response = await axios.get('/api/products/?skip=0&limit=10')
    products.value = response.data.map(item => ({
      ...item,
      image_url: 'https://via.placeholder.com/150'
    }))
  } catch (error) {
    console.error('無法獲取產品:', error)
  }
}

const addToCart = async (product) => {
  try {
    const token = localStorage.getItem('token')
    await axios.post(
      '/api/cart/',
      { product_id: product.id, quantity: 1 },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    alert('已加入購物車')
  } catch (error) {
    console.error('加入購物車失敗:', error)
  }
}

onMounted(fetchProducts)
</script>