import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: !!localStorage.getItem('token'),
  }),
  actions: {
    setAuthenticated(status) {
      this.isAuthenticated = status
    },
    logout() {
      localStorage.removeItem('token')
      this.isAuthenticated = false
    },
  },
})