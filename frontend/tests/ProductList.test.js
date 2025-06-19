import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ProductList from '../src/views/ProductList.vue'
import axios from 'axios'

// 模擬 axios
vi.mock('axios')

describe('ProductList.vue', () => {
  it('renders product list correctly', async () => {
    // 模擬 API 響應
    const mockProducts = [
      { id: 1, name: '產品 1', description: '描述 1', price: 100, stock: 10 },
      { id: 2, name: '產品 2', description: '描述 2', price: 200, stock: 5 }
    ]
    axios.get.mockResolvedValue({ data: mockProducts })

    // 掛載組件
    const wrapper = mount(ProductList)

    // 等待非同步請求完成
    await wrapper.vm.$nextTick()

    // 驗證產品數量
    const productCards = wrapper.findAll('.card')
    expect(productCards).toHaveLength(2)

    // 驗證第一個產品的內容
    expect(productCards[0].text()).toContain('產品 1')
    expect(productCards[0].text()).toContain('NT$100.00')
    expect(productCards[0].text()).toContain('庫存: 10')
  })

  it('displays empty message when no products', async () => {
    // 模擬空響應
    axios.get.mockResolvedValue({ data: [] })

    // 掛載組件
    const wrapper = mount(ProductList)

    // 等待非同步請求完成
    await wrapper.vm.$nextTick()

    // 驗證空訊息
    expect(wrapper.text()).toContain('暫無產品')
  })

  it('handles API error gracefully', async () => {
    // 模擬 API 錯誤
    axios.get.mockRejectedValue(new Error('API 錯誤'))

    // 掛載組件
    const wrapper = mount(ProductList)

    // 等待非同步請求完成
    await wrapper.vm.$nextTick()

    // 驗證錯誤處理
    expect(wrapper.text()).toContain('無法載入產品')
  })
})