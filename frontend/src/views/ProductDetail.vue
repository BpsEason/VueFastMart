<script type="text/javascript">
        var gk_isXlsx = false;
        var gk_xlsxFileLookup = {};
        var gk_fileData = {};
        function filledCell(cell) {
          return cell !== '' && cell != null;
        }
        function loadFileData(filename) {
        if (gk_isXlsx && gk_xlsxFileLookup[filename]) {
            try {
                var workbook = XLSX.read(gk_fileData[filename], { type: 'base64' });
                var firstSheetName = workbook.SheetNames[0];
                var worksheet = workbook.Sheets[firstSheetName];

                // Convert sheet to JSON to filter blank rows
                var jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1, blankrows: false, defval: '' });
                // Filter out blank rows (rows where all cells are empty, null, or undefined)
                var filteredData = jsonData.filter(row => row.some(filledCell));

                // Heuristic to find the header row by ignoring rows with fewer filled cells than the next row
                var headerRowIndex = filteredData.findIndex((row, index) =>
                  row.filter(filledCell).length >= filteredData[index + 1]?.filter(filledCell).length
                );
                // Fallback
                if (headerRowIndex === -1 || headerRowIndex > 25) {
                  headerRowIndex = 0;
                }

                // Convert filtered JSON back to CSV
                var csv = XLSX.utils.aoa_to_sheet(filteredData.slice(headerRowIndex)); // Create a new sheet from filtered array of arrays
                csv = XLSX.utils.sheet_to_csv(csv, { header: 1 });
                return csv;
            } catch (e) {
                console.error(e);
                return "";
            }
        }
        return gk_fileData[filename] || "";
        }
        </script><template>
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
    const response = await axios.get(`http://localhost:8000/products/${route.params.id}`)
    product.value = {
      ...response.data,
      image_url: 'https://via.placeholder.com/300' // 模擬圖片
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
      'http://localhost:8000/cart/',
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

// 懶加載指令
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