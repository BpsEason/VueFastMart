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
    const response = await axios.post('http://localhost:8000/auth/token', {
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