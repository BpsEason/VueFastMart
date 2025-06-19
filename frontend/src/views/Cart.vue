<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">購物車</h1>
    <div v-if="cartItems.length > 0">
      <div v-for="item in cartItems" :key="item.id" class="border p-4 mb-4 rounded flex justify-between">
        <div>
          <h2 class="text-xl">{{ item.product?.name || '未知產品' }}</h2>
          <p>數量: {{ item.quantity }}</p>
          <p class="text-lg font-semibold">NT${{ (item.product?.price * item.quantity).toFixed(2) }}</p>
        </div>
        <button
          @click="removeFromCart(item.id)"
          class="bg-red-500 text-white px-4 py-2 rounded"
        >
          移除
        </button>
      </div>
    </div>
    <p v-else>購物車為空</p>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useCartStore } from '../store/cart'

const cartStore = useCartStore()
const cartItems = computed(() => cartStore.items)

const fetchCart = async () => {
  try {
    await cartStore.fetchCart()
  } catch (error) {
    console.error('無法獲取購物車:', error)
    alert('請先登入或檢查網路')
  }
}

const removeFromCart = async (itemId) => {
  try {
    await cartStore.removeItem(itemId)
  } catch (error) {
    console.error('移除失敗:', error)
    alert('移除失敗，請稍後重試')
  }
}

onMounted(fetchCart)
</script>