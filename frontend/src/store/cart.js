import { defineStore } from 'pinia'
import axios from 'axios'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
  }),
  actions: {
    async addItem({ product_id, quantity }) {
      try {
        const token = localStorage.getItem('token')
        if (!token) throw new Error('請先登入')
        const response = await axios.post(
          '/api/cart/',
          { product_id, quantity },
          { headers: { Authorization: `Bearer ${token}` } }
        )
        this.items.push(response.data)
      } catch (error) {
        console.error('加入購物車失敗:', error)
        throw error
      }
    },
    async removeItem(id) {
      try {
        const token = localStorage.getItem('token')
        if (!token) throw new Error('請先登入')
        await axios.delete(`/api/cart/${id}`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        this.items = this.items.filter(item => item.id !== id)
      } catch (error) {
        console.error('移除失敗:', error)
        throw error
      }
    },
    async fetchCart() {
      try {
        const token = localStorage.getItem('token')
        if (!token) throw new Error('請先登入')
        const response = await axios.get('/api/cart/', {
          headers: { Authorization: `Bearer ${token}` },
        })
        this.items = response.data
      } catch (error) {
        console.error('無法獲取購物車:', error)
        throw error
      }
    },
  },
})