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
  <div class="container mx-auto p-4 max-w-md">
    <h1 class="text-2xl font-bold mb-4">註冊</h1>
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
      <button @click="handleRegister" class="btn-primary w-full">
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
    await axios.post('http://localhost:8000/auth/register', {
      email: form.value.email,
      password: form.value.password,
    })
    alert('註冊成功，請登入')
    router.push('/login')
  } catch (error) {
    console.error('註冊失敗:', error)
    alert('註冊失敗，電子郵件可能已被使用或輸入無效')
  }
}
</script>