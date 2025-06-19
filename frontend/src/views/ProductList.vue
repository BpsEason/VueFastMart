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
    const response = await axios.get('http://localhost:8000/products/?skip=0&limit=10')
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
      'http://localhost:8000/cart/',
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