<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">{{ product.name }}</h1>
    <div class="card">
      <img
        :data-src="product.image_url"
        alt="Product Image"
        class="w-full h-64 object-cover rounded"
        v-lazyload
      />
      <p class="mt-4 text-gray-600">{{ product.description }}</p>
      <p class="text-lg font-semibold mt-2">NT${{ product.price.toFixed(2) }}</p>
      <p class="mt-2 text-sm">庫存: {{ product.stock }} 件</p>
      <button
        @click="addToCart"
        :disabled="product.stock === 0"
        class="btn-primary mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ product.stock > 0 ? '加入購物車' : '無庫存' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const product = ref({})

const fetchProduct = async () => {
  try {
    const response = await axios.get(`/api/products/${route.params.id}`)
    product.value = {
      ...response.data,
      image_url: 'https://via.placeholder.com/300'
    }
  } catch (error) {
    console.error('無法獲取產品:', error)
    alert('產品載入失敗')
  }
}

const addToCart = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      alert('請先登入')
      return
    }
    await axios.post(
      '/api/cart/',
      { product_id: product.value.id, quantity: 1 },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    alert('已加入購物車')
  } catch (error) {
    console.error('加入購物車失敗:', error)
    alert('加入購物車失敗，請稍後重試')
  }
}

onMounted(fetchProduct)

const vLazyload = {
  mounted(el) {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        el.src = el.dataset.src
        observer.unobserve(el)
      }
    })
    observer.observe(el)
  }
}
</script>