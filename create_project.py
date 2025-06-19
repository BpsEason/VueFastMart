import os
from pathlib import Path

def create_file(path, content):
    """Create a file with the given content, creating parent directories if needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def create_project():
    """Create the VueFastMart project structure with all necessary files."""
    project_structure = {
        "frontend": {
            "src": {
                "components": {
                    "ProductCard.vue": '''<template>
  <div class="border p-4 rounded">
    <img
      :data-src="product.image_url"
      alt="Product Image"
      class="w-full h-48 object-cover"
      v-lazyload
    />
    <h2 class="text-xl">{{ product.name }}</h2>
    <p>{{ product.description }}</p>
    <p class="text-lg font-semibold">NT${{ product.price.toFixed(2) }}</p>
    <button
      @click="$emit('add-to-cart', product)"
      class="bg-blue-500 text-white px-4 py-2 rounded mt-2"
    >
      加入購物車
    </button>
  </div>
</template>

<script setup>
defineProps(['product'])
defineEmits(['add-to-cart'])

const vLazyload = {
  mounted(el) {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        el.src = el.dataset.src
        observer.unobserve(el)
      }
    })
    observer.observe(el)
  }
}
</script>
'''
                },
                "store": {
                    "auth.js": '''import { defineStore } from 'pinia'

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
''',
                    "cart.js": '''import { defineStore } from 'pinia'
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
'''
                },
                "views": {
                    "Register.vue": '''<template>
  <div class="container mx-auto p-4 max-w-md">
    <h1 class="text-2xl font-bold mb-4">寄存</h1>
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
      <button @click="handleRegister" class="btn-primary w-full mt-2">
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
    const message = error.response?.data?.detail || '註冊失敗，請檢查輸入項目'
    alert(message)
  }
}
</script>
''',
                    "ProductDetail.vue": '''<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">{{ product.name }}</h1>
    <div class="card">
      <img
        :data-src="product.image_url"
        alt="Product Image"
        class="w-full h-64 object-cover rounded"
        v-lazyload
      />
      <p class="mt-4 text-gray-600">{{ product.description }}</p>
      <p class="text-lg font-semibold mt-2">NT${{ product.price.toFixed(2) }}</p>
      <p class="mt-2 text-sm">庫存: {{ product.stock }} 件</p>
      <button
        @click="addToCart"
        :disabled="product.stock === 0"
        class="btn-primary mt-4 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ product.stock > 0 ? '加入購物車' : '無庫存' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const product = ref({})

const fetchProduct = async () => {
  try {
    const response = await axios.get(`/api/products/${route.params.id}`)
    product.value = {
      ...response.data,
      image_url: 'https://via.placeholder.com/300'
    }
  } catch (error) {
    console.error('無法獲取產品:', error)
    alert('產品載入失敗')
  }
}

const addToCart = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      alert('請先登入')
      return
    }
    await axios.post(
      '/api/cart/',
      { product_id: product.value.id, quantity: 1 },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    alert('已加入購物車')
  } catch (error) {
    console.error('加入購物車失敗:', error)
    alert('加入購物車失敗，請稍後重試')
  }
}

onMounted(fetchProduct)

const vLazyload = {
  mounted(el) {
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        el.src = el.dataset.src
        observer.unobserve(el)
      }
    })
    observer.observe(el)
  }
}
</script>
''',
                    "Login.vue": '''<template>
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
''',
                    "ProductList.vue": '''<template>
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">產品列表</h1>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <ProductCard
        v-for="product in products"
        :key="product.id"
        :product="product"
        @add-to-cart="addToCart"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import ProductCard from '../components/ProductCard.vue'

const products = ref([])

const fetchProducts = async () => {
  try {
    const response = await axios.get('/api/products/?skip=0&limit=10')
    products.value = response.data.map(item => ({
      ...item,
      image_url: 'https://via.placeholder.com/150'
    }))
  } catch (error) {
    console.error('無法獲取產品:', error)
  }
}

const addToCart = async (product) => {
  try {
    const token = localStorage.getItem('token')
    await axios.post(
      '/api/cart/',
      { product_id: product.id, quantity: 1 },
      { headers: { Authorization: `Bearer ${token}` } }
    )
    alert('已加入購物車')
  } catch (error) {
    console.error('加入購物車失敗:', error)
  }
}

onMounted(fetchProducts)
</script>
''',
                    "Cart.vue": '''<template>
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
'''
                },
                "router": {
                    "index.js": '''import { createRouter, createWebHistory } from 'vue-router'
import ProductList from '../views/ProductList.vue'
import ProductDetail from '../views/ProductDetail.vue'
import Cart from '../views/Cart.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import { useAuthStore } from '../store/auth'

const routes = [
  { path: '/', component: ProductList },
  { path: '/product/:id', component: ProductDetail },
  { path: '/cart', component: Cart, meta: { requiresAuth: true } },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
'''
                }
            },
            "tests": {
                "ProductList.test.js": '''import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ProductList from '../src/views/ProductList.vue'
import ProductCard from '../src/components/ProductCard.vue'
import axios from 'axios'

vi.mock('axios')

describe('ProductList', () => {
  it('renders product cards', async () => {
    axios.get.mockResolvedValue({
      data: [
        { id: 1, name: 'Product 1', price: 100, description: 'Desc 1' },
        { id: 2, name: 'Product 2', price: 200, description: 'Desc 2' },
      ],
    })

    const wrapper = mount(ProductList)
    await wrapper.vm.$nextTick()

    const cards = wrapper.findAllComponents(ProductCard)
    expect(cards).toHaveLength(2)
    expect(cards[0].props('product').name).toBe('Product 1')
  })
})
''',
                "Cart.test.js": '''import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Cart from '../src/views/Cart.vue'
import { useCartStore } from '../src/store/cart'
import { createPinia, setActivePinia } from 'pinia'
import axios from 'axios'

vi.mock('axios')

describe('Cart', () => {
  let pinia

  beforeEach(() => {
    pinia = createPinia()
    setActivePinia(pinia)
  })

  it('renders cart items', async () => {
    const cartStore = useCartStore()
    axios.get.mockResolvedValue({
      data: [
        { id: 1, product: { name: 'Product 1', price: 100 }, quantity: 1 },
      ],
    })

    const wrapper = mount(Cart, { global: { plugins: [pinia] } })
    await wrapper.vm.$nextTick()
    await cartStore.fetchCart()

    const items = wrapper.findAll('.border.p-4.mb-4.rounded')
    expect(items).toHaveLength(1)
    expect(items[0].text()).toContain('Product 1')
  })
})
'''
            },
            "tailwind.config.js": '''/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
}
''',
            "vite.config.js": '''import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: true,
      },
    },
    minify: 'esbuild',
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
''',
            "package.json": '''{
  "name": "vuefastmart-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest run"
  },
  "dependencies": {
    "axios": "^1.7.7",
    "pinia": "^2.2.4",
    "vue": "^3.5.12",
    "vue-router": "^4.4.5"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.1.4",
    "tailwindcss": "^3.4.13",
    "vite": "^5.4.8",
    "vitest": "^2.1.3",
    "@vue/test-utils": "^2.4.6"
  }
}
''',
            ".env.example": '''VITE_API_URL=http://localhost:8000
'''
        },
        "backend": {
            "app": {
                "api": {
                    "auth.py": '''from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, models
from app.auth import get_password_hash, verify_password, create_access_token

router = APIRouter()

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
''',
                    "products.py": '''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, models
from typing import List

router = APIRouter()

@router.get("/", response_model=List[schemas.Product])
def get_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products

@router.get("/{id}", response_model=schemas.Product)
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
''',
                    "cart.py": '''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, models
from app.auth import get_current_user
from typing import List

router = APIRouter()

@router.get("/", response_model=List[schemas.CartItem])
async def get_cart(current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    for item in cart_items:
        item.product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    return cart_items

@router.post("/", response_model=schemas.CartItem)
async def add_to_cart(cart_item: schemas.CartItemCreate, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == cart_item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < cart_item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    db_item = models.CartItem(user_id=current_user.id, product_id=cart_item.product_id, quantity=cart_item.quantity)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db_item.product = product
    return db_item

@router.delete("/{id}")
async def remove_from_cart(id: int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_item = db.query(models.CartItem).filter(models.CartItem.id == id, models.CartItem.user_id == current_user.id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed"}
'''
                },
                "database.py": '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vuefastmart.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
                "cache.py": '''import redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True
)

def cache_get(key: str):
    return redis_client.get(key)

def cache_set(key: str, value: str, ex: int = 3600):
    redis_client.setex(key, ex, value)
''',
                "main.py": '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api import auth, products, cart
from app.database import engine, Base
from sqlalchemy import inspect
import os

load_dotenv()

# 驗證環境變數
if not os.getenv("FRONTEND_URL"):
    raise ValueError("FRONTEND_URL environment variable is not set")

app = FastAPI(title="VueFastMart API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加安全頭部
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' https://via.placeholder.com; "
        "style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

# 檢查資料庫連線
def check_database_connection():
    try:
        with engine.connect() as connection:
            inspect(engine).get_table_names()
    except Exception as e:
        raise RuntimeError(f"Database connection failed: {str(e)}")

check_database_connection()
Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/auth", tags=["認證"])
app.include_router(products.router, prefix="/products", tags=["產品"])
app.include_router(cart.router, prefix="/cart", tags=["購物車"])

@app.get("/")
def read_root():
    return {"message": "歡迎使用 VueFastMart API"}

@app.get("/health")
def health_check():
    try:
        with engine.connect() as connection:
            return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
'''
            },
            "tests": {
                "test_auth.py": '''import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_and_login():
    response = client.post("/auth/register", json={"email": "test@example.com", "password": "securepassword"})
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

    response = client.post("/auth/token", data={"username": "test@example.com", "password": "securepassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()
'''
                "test_products.py": '''import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from app import models
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    product = models.Product(name="Test Product", description="Desc", price=100, stock=10)
    db.add(product)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def test_get_products():
    response = client.get("/products/?skip=0&limit=10")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Product"
'''
                "test_cart.py": '''import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base, engine
from app import models
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    user = models.User(email="test@example.com", hashed_password="hashed")
    product = models.Product(name="Test Product", description="Desc", price=100, stock=10)
    db.add_all([user, product])
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def test_cart_operations():
    # Register and login to get token
    response = client.post("/auth/token", data={"username": "test@example.com", "password": "hashed"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add to cart
    response = client.post("/cart/", json={"product_id": 1, "quantity": 1}, headers=headers)
    assert response.status_code == 200
    assert response.json()["product_id"] == 1

    # Get cart
    response = client.get("/cart/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Remove from cart
    response = client.delete("/cart/1", headers=headers)
    assert response.status_code == 200
'''
            },
            "requirements.txt": '''fastapi==0.115.2
uvicorn==0.32.0
sqlalchemy==2.0.35
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.1
redis==5.1.1
pytest==8.3.3
pytest-cov==5.0.0
httpx==0.27.2
'''
            ".env.example": '''DATABASE_URL=sqlite:///./vuefastmart.db
SECRET_KEY=your-secret-key
REDIS_HOST=localhost
REDIS_PORT=6379
FRONTEND_URL=http://localhost:5173
'''
        },
        "README.md": '''# VueFastMart

VueFastMart 是一個基於 Vue.js 和 FastAPI 的現代電商平台，提供產品瀏覽、購物車管理和用戶認證功能。專案設計注重新手友好，支援前端懶加載、API 快取和安全認證，適合學習全端開發。

## 功能

### 前端功能
- **產品列表與詳情**：展示產品資訊（名稱、描述、價格、庫存），支援圖片懶加載。
- **購物車管理**：添加、移除購物車項目，與後端 API 同步，使用 Pinia 狀態管理。
- **用戶認證**：支援註冊和登入，使用 JWT 認證。
- **響應式設計**：使用 Tailwind CSS，適配手機和桌面。

### 後端 API
- **認證**：`POST /auth/register`, `POST /auth/token` - 用戶註冊和登入。
- **產品**：`GET /products/` - 分頁查詢產品，`GET /products/{id}` - 產品詳情。
- **購物車**：`GET /cart/` - 獲取購物車，`POST /cart/` - 添加項目，`DELETE /cart/{id}` - 移除項目。
- **健康檢查**：`GET /health` - 檢查 API 和資料庫狀態。

## 技術棧
- **前端**：Vue.js 3, Pinia, Vue Router, Axios, Tailwind CSS, Vite
- **後端**：FastAPI, SQLAlchemy, SQLite/PostgreSQL, Redis（快取）
- **測試**：Vitest（前端），Pytest（後端）

## 專案結構
```
VueFastMart/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── products.py
│   │   │   └── cart.py
│   │   ├── database.py
│   │   ├── cache.py
│   │   └── main.py
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_products.py
│   │   └── test_cart.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ProductCard.vue
│   │   ├── store/
│   │   │   ├── auth.js
│   │   │   └── cart.js
│   │   ├── views/
│   │   │   ├── ProductList.vue
│   │   │   ├── ProductDetail.vue
│   │   │   ├── Cart.vue
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   └── router/
│   │       └── index.js
│   ├── tests/
│   │   ├── ProductList.test.js
│   │   └── Cart.test.js
│   ├── tailwind.config.js
│   ├── vite.config.js
│   ├── package.json
│   └── .env.example
├── create_project.py
└── README.md
```

## 設置與運行

### 前提條件
- **Node.js**: v18 或更高版本
- **Python**: 3.10 或更高版本
- **Redis**: 用於快取（可選）
- **Git**: 用於版本控制

### 設置後端
1. 克隆專案：
   ```bash
   git clone https://github.com/BpsEason/VueFastMart.git
   cd VueFastMart/backend
   ```
2. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```
3. 配置環境變數：
   ```bash
   cp .env.example .env
   ```
   編輯 `.env`，設置：
   ```env
   DATABASE_URL=sqlite:///./vuefastmart.db
   SECRET_KEY=your-secret-key
   REDIS_HOST=localhost
   REDIS_PORT=6379
   FRONTEND_URL=http://localhost:5173
   ```
   生成 `SECRET_KEY`：
   ```bash
   openssl rand -hex 32
   ```
4. 啟動後端：
   ```bash
   uvicorn app.main:app --reload
   ```
   訪問 `http://localhost:8000/docs` 查看 API 文件，`http://localhost:8000/health` 檢查健康狀態。

### 設置前端
1. 進入前端目錄：
   ```bash
   cd frontend
   ```
2. 安裝依賴：
   ```bash
   npm install
   ```
3. 配置環境變數：
   ```bash
   cp .env.example .env
   ```
   編輯 `.env`，設置：
   ```env
   VITE_API_URL=http://localhost:8000
   ```
4. 啟動前端：
   ```bash
   npm run dev
   ```
   訪問 `http://localhost:5173`。

### 運行測試
- **後端測試**：
   ```bash
   cd backend
   pytest tests/ --cov=app --cov-report=html
   ```
- **前端測試**：
   ```bash
   cd frontend
   npm run test
   ```

## 部署指引

### 部署前端到 Vercel
1. 將前端程式碼推送到 GitHub。
2. 在 Vercel 創建新專案，連接到 GitHub 倉庫。
3. 設置環境變數：
   - `VITE_API_URL`: 後端 API 地址（例如 `https://vuefastmart-api.onrender.com`）
4. 部署並獲取前端 URL，更新後端 `.env` 的 `FRONTEND_URL`。

### 部署後端到 Render
1. 將後端程式碼推送到 GitHub。
2. 在 Render 創建新 Web Service，選擇 Python 環境。
3. 設置環境變數：
   - `DATABASE_URL`: PostgreSQL URL（由 Render 提供）
   - `SECRET_KEY`: 安全密鑰
   - `FRONTEND_URL`: 前端部署地址
   - `REDIS_HOST` 和 `REDIS_PORT`（若使用 Redis）
4. 部署並驗證 `/health` 端點。

## 開發與貢獻
1. 提交問題或功能請求到 GitHub Issues。
2. Fork 專案，創建分支，提交 Pull Request。
3. 遵循 PEP 8（Python）和 ESLint（JavaScript）規範。

## 故障排除
- **CORS 錯誤**：檢查後端 `.env` 的 `FRONTEND_URL` 是否與前端地址一致。
- **API 請求失敗**：確認 `vite.config.js` 的代理設置和後端是否運行。
- **資料庫錯誤**：檢查 `DATABASE_URL` 和資料庫服務。
- 查看日誌：
  - 後端：`uvicorn` 輸出或 `tail -f uvicorn.log`
  - 前端：瀏覽器開發者工具（F12）Network 標籤

## 致謝
感謝 FastAPI、Vue.js 和 Tailwind CSS 社群的優秀工具！本專案受《Python 電商教學》啟發，旨在幫助新手學習全端開發。
'''
    }

    # Create all files in the project structure
    base_path = Path("VueFastMart")
    for dir_path, contents in project_structure.items():
        if isinstance(contents, dict):
            for file_or_dir, content in contents.items():
                if isinstance(content, dict):
                    # Recursive call for nested directories
                    for sub_path, sub_content in content.items():
                        if isinstance(sub_content, dict):
                            for sub_file, sub_file_content in sub_content.items():
                                full_path = base_path / dir_path / file_or_dir / sub_path / sub_file
                                create_file(full_path, sub_file_content)
                        else:
                            full_path = base_path / dir_path / file_or_dir / sub_path
                            create_file(full_path, sub_content)
                else:
                    full_path = base_path / dir_path / file_or_dir
                    create_file(full_path, content)
        else:
            full_path = base_path / dir_path
            create_file(full_path, contents)

if __name__ == "__main__":
    create_project()
    print("VueFastMart project structure created successfully!")