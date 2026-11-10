<template>
  <div class="page-container">
    <el-card shadow="never">
      <!-- 搜索区 -->
      <div class="search-bar">
        <el-select
          v-model="searchForm.type"
          placeholder="日志类型"
          clearable
          style="width: 160px"
        >
          <el-option label="登录日志" value="登录" />
          <el-option label="操作日志" value="操作" />
          <el-option label="错误日志" value="错误" />
        </el-select>
        <el-select
          v-model="searchForm.level"
          placeholder="日志级别"
          clearable
          style="width: 140px"
        >
          <el-option label="INFO" value="INFO" />
          <el-option label="WARNING" value="WARNING" />
          <el-option label="ERROR" value="ERROR" />
        </el-select>
        <el-input
          v-model="searchForm.username"
          placeholder="操作人"
          clearable
          style="width: 160px"
          :prefix-icon="User"
        />
        <el-date-picker
          v-model="searchForm.dateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          value-format="YYYY-MM-DD HH:mm:ss"
          style="width: 360px"
        />
        <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        <div class="search-bar-right">
          <el-button type="danger" :icon="Delete" @click="handleBatchDelete">批量删除</el-button>
          <el-button :icon="Download" @click="handleExport">导出日志</el-button>
        </div>
      </div>

      <!-- 表格 -->
      <el-table
        :data="tableData"
        style="width: 100%"
        v-loading="loading"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column type="index" label="序号" width="80" align="center" />
        <!-- <el-table-column prop="id" label="ID" width="100" align="center" /> -->
        <el-table-column prop="type" label="类型" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.log_type }}</el-tag>
            <!-- <el-tag v-if="row.type === 'login'" type="primary">登录</el-tag>
            <el-tag v-else-if="row.type === 'operation'" type="success">操作</el-tag>
            <el-tag v-else type="danger">错误</el-tag> -->
          </template>
        </el-table-column>
        <el-table-column prop="level" label="级别" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.log_level === 'INFO'" type="info">INFO</el-tag>
            <el-tag v-else-if="row.log_level === 'WARNING'" type="warning">WARNING</el-tag>
            <el-tag v-else type="ERROR">ERROR</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="oper_username" label="操作人" width="120" align="center" />
        <el-table-column prop="oper_content" label="操作内容" min-width="240" show-overflow-tooltip align="center" />
        <el-table-column prop="oper_ip" label="IP地址" width="140" align="center" />
        <!-- <el-table-column prop="duration" label="耗时(ms)" width="100" align="center" /> -->
        <el-table-column 
          prop="oper_time" 
          label="操作时间" 
          width="180"
          align="center" 
          :formatter="(row: any) => dayjs(row.oper_time).format('YYYY-MM-DD HH:mm:ss')" 
        />
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link :icon="View" @click="handleView(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="日志详情" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="日志ID">{{ currentLog?.id }}</el-descriptions-item>
        <el-descriptions-item label="日志类型">{{ currentLog?.log_type }}</el-descriptions-item>
        <el-descriptions-item label="日志级别">{{ currentLog?.log_level }}</el-descriptions-item>
        <el-descriptions-item label="操作人">{{ currentLog?.oper_username }}</el-descriptions-item>
        <el-descriptions-item label="操作内容">{{ currentLog?.oper_content }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ currentLog?.oper_ip }}</el-descriptions-item>
        <!-- <el-descriptions-item label="请求参数">{{ currentLog?.params }}</el-descriptions-item>
        <el-descriptions-item label="执行结果">{{ currentLog?.result }}</el-descriptions-item> -->
        <el-descriptions-item label="耗时">{{ currentLog?.cost_ms }}ms</el-descriptions-item>
        <el-descriptions-item label="操作时间">{{ dayjs(currentLog?.oper_time).format('YYYY-MM-DD HH:mm:ss') }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { dayjs, ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Delete, Download, View, User } from '@element-plus/icons-vue'
import { getLogs, exportLogs } from '@/api/log'

const loading = ref(false)
const detailVisible = ref(false)
const currentLog = ref<any>(null)
const selectedRows = ref<any[]>([])

const searchForm = reactive({
  type: '',
  level: '',
  username: '',
  dateRange: [] as string[]
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref<any[]>([])

const actions = [
  '用户登录系统', '用户退出系统', '新增文章', '编辑文章', '删除文章',
  '新增分类', '编辑分类', '删除分类', '新增用户', '编辑用户信息',
  '修改密码', '上传图片', '导出数据', '查看用户列表', '查看日志'
]

const mockData = Array.from({ length: 36 }, (_, i) => {
  const types = ['login', 'operation', 'error']
  const levels = ['info', 'warning', 'error']
  const typeIdx = i % 3 === 0 ? 0 : i % 5 === 0 ? 2 : 1
  const type = types[typeIdx]
  const level = type === 'error' ? 'error' : levels[i % 3]
  const date = new Date(Date.now() - i * 3600000 * 2)
  return {
    id: 1000 + i,
    type,
    level,
    username: ['admin', 'zhangsan', 'lisi', 'editor'][i % 4],
    action: actions[i % actions.length],
    ip: `192.168.${(i % 200) + 1}.${(i % 255) + 1}`,
    params: type === 'error' ? '{"id": 123, "name": "test"}' : '—',
    result: type === 'error' ? '系统异常：NullPointerException' : '操作成功',
    duration: Math.floor(Math.random() * 500) + 10,
    createTime: date.toLocaleString('zh-CN', { hour12: false }).replace(/\//g, '-')
  }
})

const fetchData = async() => {
  loading.value = true
  const hasDateRange = searchForm.dateRange && searchForm.dateRange.length > 0
  const res = await getLogs({
    log_level: searchForm.level,
    log_type: searchForm.type,
    oper_username: searchForm.username,
    page: pagination.page,
    pageSize: pagination.pageSize,
    start_time: hasDateRange ? `${searchForm.dateRange[0]} 00:00:00` : '',
    end_time: hasDateRange ? `${searchForm.dateRange[1]} 23:59:59` : ''
  })
  if (res.code === 200) {
    tableData.value = res.data
    // pagination.total = res.total
  }
  loading.value = false
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.type = ''
  searchForm.level = ''
  searchForm.username = ''
  searchForm.dateRange = []
  pagination.page = 1
  fetchData()
}

const handleSelectionChange = (rows: any[]) => {
  selectedRows.value = rows
}

const handleBatchDelete = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请先选择要删除的日志')
    return
  }
  ElMessageBox.confirm(`确定要删除选中的 ${selectedRows.value.length} 条日志吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const ids = selectedRows.value.map(r => r.id)
    for (let i = mockData.length - 1; i >= 0; i--) {
      if (ids.includes(mockData[i].id)) mockData.splice(i, 1)
    }
    ElMessage.success('批量删除成功')
    fetchData()
  }).catch(() => {})
}

const handleExport = async () => {
  const hasDateRange = searchForm.dateRange && searchForm.dateRange.length > 0
  const res = await exportLogs({
    log_level: searchForm.level,
    log_type: searchForm.type,
    oper_username: searchForm.username,
    start_time: hasDateRange ? `${searchForm.dateRange[0]} 00:00:00` : '',
    end_time: hasDateRange ? `${searchForm.dateRange[1]} 23:59:59` : ''
  })
  // 导出成功后，下载文件
  // if (res.code === 200) {
    const a = document.createElement('a')
    a.href = URL.createObjectURL(res)
    a.download = 'log.xlsx'
    a.click()
    URL.revokeObjectURL(a.href)
  // }
}

const handleView = (row: any) => {
  currentLog.value = row
  detailVisible.value = true
}

onMounted(fetchData)
</script>

<style scoped>
.page-container {
  width: 100%;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.search-bar-right {
  margin-left: auto;
  display: flex;
  gap: 12px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
