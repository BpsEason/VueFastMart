import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: [],
  }),
  actions: {
    addItem(product) {
      this.items.push({ ...product, quantity: 1 })
    },
    removeItem(productId) {
      this.items = this.items.filter(item => item.id !== productId)
    },
  },
})