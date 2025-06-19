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
    <h1 class="text-2xl font-bold mb-4">購物車</h1>
    <div v-if="cartItems.length > 0">
      <div v-for="item in cartItems" :key="item.id" class="border p-4 mb-4 rounded flex justify-between">
        <div>
          <h2 class="text-xl">{{ item.product.name }}</h2>
          <p>數量: {{ item.quantity }}</p>
          <p class="text-lg font-semibold">NT${{ item.product.price * item.quantity }}</p>
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
import { ref, onMounted } from 'vue'
import axios from 'axios'

const cartItems = ref([])

const fetchCart = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('http://localhost:8000/cart/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    cartItems.value = response.data
  } catch (error) {
    console.error('無法獲取購物車:', error)
  }
}

const removeFromCart = async (itemId) => {
  try {
    const token = localStorage.getItem('token')
    await axios.delete(`http://localhost:8000/cart/${itemId}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    cartItems.value = cartItems.value.filter(item => item.id !== itemId)
  } catch (error) {
    console.error('移除失敗:', error)
  }
}

onMounted(fetchCart)
</script>