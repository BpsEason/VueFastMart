<template>
  <div>
    <nav class="bg-gray-800 text-white p-4">
      <div class="max-w-7xl mx-auto flex justify-between items-center">
        <router-link to="/" class="text-xl font-bold">VueFastMart</router-link>
        <div class="space-x-4">
          <router-link to="/">首頁</router-link>
          <router-link to="/cart">購物車</router-link>
          <router-link v-if="!isLoggedIn" to="/login">登入</router-link>
          <router-link v-if="!isLoggedIn" to="/register">註冊</router-link>
          <button v-if="isLoggedIn" @click="logout" class="text-white">登出</button>
        </div>
      </div>
    </nav>
    <router-view class="p-4" />
  </div>
</template>

<script>
export default {
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token');
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token');
      this.$router.push('/login');
    }
  }
}
</script>