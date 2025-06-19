import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Cart from '../src/views/Cart.vue'
import axios from 'axios'
import { useCartStore } from '../src/stores/cart'

// 模擬 axios
vi.mock('axios')

describe('Cart.vue', () => {
  let pinia, cartStore

  beforeEach(() => {
    // 初始化 Pinia
    pinia = createPinia()
    setActivePinia(pinia)
    cartStore = useCartStore()
  })

  it('displays cart items correctly', async () => {
    // 模擬購物車狀態
    cartStore.items = [
      { id: 1, name: '產品 1', price: 100, quantity: 2 },
      { id: 2, name: '產品 2', price: 200, quantity: 1 }
    ]

    // 掛載組件
    const wrapper = mount(Cart, { global: { plugins: [pinia] } })

    // 驗證商品數量
    const cartItems = wrapper.findAll('.cart-item')
    expect(cartItems).toHaveLength(2)

    // 驗證第一個商品
    expect(cartItems[0].text()).toContain('產品 1')
    expect(cartItems[0].text()).toContain('NT$100.00')
    expect(cartItems[0].text()).toContain('數量: 2')

    // 驗證總價
    expect(wrapper.text()).toContain('總計: NT$400.00')
  })

  it('adds item to cart via API', async () => {
    // 模擬 API 響應
    axios.post.mockResolvedValue({ data: { id: 1, name: '產品 1', price: 100, quantity: 1 } })

    // 掛載組件
    const wrapper = mount(Cart, { global: { plugins: [pinia] } })

    // 模擬添加商品
    await cartStore.addItem({ productId: 1, quantity: 1 })

    // 驗證 API 請求
    expect(axios.post).toHaveBeenCalledWith('http://localhost:8000/cart/', {
      productId: 1,
      quantity: 1
    })

    // 驗證購物車狀態
    expect(cartStore.items).toHaveLength(1)
    expect(cartStore.items[0].name).toBe('產品 1')
  })

  it('removes item from cart via API', async () => {
    // 模擬初始購物車
    cartStore.items = [{ id: 1, name: '產品 1', price: 100, quantity: 1 }]

    // 模擬 API 響應
    axios.delete.mockResolvedValue({ data: { message: '商品已移除' } })

    // 掛載組件
    const wrapper = mount(Cart, { global: { plugins: [pinia] } })

    // 模擬移除商品
    await cartStore.removeItem(1)

    // 驗證 API 請求
    expect(axios.delete).toHaveBeenCalledWith('http://localhost:8000/cartItem/1')

    // 驗證購物車狀態
    expect(cartStore.items).toHaveLength(0)
  })

  it('displays empty cart message', () => {
    // 模擬空購物車
    cartStore.items = []

    // 掛載組件
    const wrapper = mount(Cart, { global: { plugins: [pinia] } })

    // 驗證空訊息
    expect(wrapper.text()).toContain('購物車是空的')
  })
})