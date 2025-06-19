import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Cart from '../src/views/Cart.vue'
import axios from 'axios'
import { useCartStore } from '../src/stores/cart'

vi.mock('axios')

describe('Cart.vue', () => {
  let pinia, cartStore

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
    cartStore = useCartStore()
  })

  it('displays cart items correctly', async () => {
    cartStore.items = [
      { id: 1, product_id: 1, name: '產品 1', price: 100, quantity: 2 },
      { id: 2, product_id: 2, name: '產品 2', price: 200, quantity: 1 },
    ]
    const wrapper = mount(Cart, { global: { plugins: [pinia] } })
    const cartItems = wrapper.findAll('.cart-item')
    expect(cartItems).toHaveLength(2)
    expect(cartItems[0].text()).toContain('產品 1')
    expect(cartItems[0].text()).toContain('NT$100.00')
    expect(cartItems[0].text()).toContain('數量: 2')
    expect(wrapper.text()).toContain('總計: NT$400.00')
  })

  it('adds item to cart via API', async () => {
    axios.post.mockResolvedValue({
      data: { id: 1, product_id: 1, name: '產品 1', price: 100, quantity: 1 },
    })
    const wrapper = mount(Cart, { global: { plugins: [pinia] } })
    await cartStore.addItem({ product_id: 1, quantity: 1 })
    expect(axios.post).toHaveBeenCalledWith(
      '/api/cart/',
      { product_id: 1, quantity: 1 },
      { headers: { Authorization: 'Bearer mock-token' } }
    )
    expect(cartStore.items).toHaveLength(1)
    expect(cartStore.items[0].name).toBe('產品 1')
  })

  it('removes item from cart via API', async () => {
    cartStore.items = [{ id: 1, product_id: 1, name: '產品 1', price: 100, quantity: 1 }]
    axios.delete.mockResolvedValue({ data: { message: '已移除購物車項目' } })
    const wrapper = mount(Cart, { global: { plugins: [pinia] } })
    await cartStore.removeItem(1)
    expect(axios.delete).toHaveBeenCalledWith(
      '/api/cart/1',
      { headers: { Authorization: 'Bearer mock-token' } }
    )
    expect(cartStore.items).toHaveLength(0)
  })

  it('displays empty cart message', () => {
    cartStore.items = []
    const wrapper = mount(Cart, { global: { plugins: [pinia] } })
    expect(wrapper.text()).toContain('購物車是空的')
  })