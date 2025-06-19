<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">登入</h1>
    <div class="mb-4">
      <label for="email" class="block">電子郵件</label>
      <input
        id="email"
        v-model="form.email"
        type="email"
        class="w-full border rounded px-3 py-2"
        required
      />
    </div>
    <div class="mb-4">
      <label for="password" class="block">密碼</label>
      <input
        id="password"
        v-model="form.password"
        type="password"
        class="w-full border rounded px-3 py-2"
        required
      />
    </div>
    <button @click="handleLogin" class="bg-blue-500 text-white px-4 py-2 rounded">
      登入
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import axios from 'axios'

const form = ref({ email: '', password: '' })
const router = useRouter()
const authStore = useAuthStore()

const handleLogin = async () => {
  try {
    const response = await axios.post('/api/auth/token', {
      username: form.value.email,
      password: form.value.password,
    })
    localStorage.setItem('token', response.data.access_token)
    authStore.setAuthenticated(true)
    router.push('/')
  } catch (error) {
    console.error('登入失敗:', error)
    alert('電子郵件或密碼錯誤')
  }
}
</script>