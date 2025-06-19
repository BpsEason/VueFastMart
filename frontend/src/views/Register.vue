<template>
  <div class="container mx-auto p-4 max-w-md">
    <h1 class="text-2xl font-bold mb-4">註冊</h1>
    <div class="card">
      <div class="mb-4">
        <label for="email" class="block text-sm font-medium">電子郵件</label>
        <input
          id="email"
          v-model="form.email"
          type="email"
          class="w-full border rounded px-3 py-2 mt-1"
          placeholder="輸入您的電子郵件"
          required
        />
      </div>
      <div class="mb-4">
        <label for="password" class="block text-sm font-medium">密碼</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          class="w-full border rounded px-3 py-2 mt-1"
          placeholder="輸入您的密碼"
          required
        />
      </div>
      <button @click="handleRegister" class="btn-primary w-full">
        註冊
      </button>
      <p class="mt-4 text-sm text-center">
        已有帳號？<router-link to="/login" class="text-blue-500 hover:underline">立即登入</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const form = ref({ email: '', password: '' })
const router = useRouter()

const handleRegister = async () => {
  try {
    await axios.post('/api/auth/register', {
      email: form.value.email,
      password: form.value.password,
    })
    alert('註冊成功，請登入')
    router.push('/login')
  } catch (error) {
    console.error('註冊失敗:', error)
    const message = error.response?.data?.detail || '註冊失敗，請檢查輸入'
    alert(message)
  }
}
</script>