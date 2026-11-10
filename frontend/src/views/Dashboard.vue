<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card stat-card-1" shadow="hover">
          <div class="stat-icon">
            <el-icon :size="36"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statsData.newUsers }}</div>
            <div class="stat-label">新增用户 (7天)</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card stat-card-2" shadow="hover">
          <div class="stat-icon">
            <el-icon :size="36"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statsData.newArticles }}</div>
            <div class="stat-label">新增文章 (7天)</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card stat-card-3" shadow="hover">
          <div class="stat-icon">
            <el-icon :size="36"><View /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statsData.views }}</div>
            <div class="stat-label">浏览数 (7天)</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card stat-card-4" shadow="hover">
          <div class="stat-icon">
            <el-icon :size="36"><Star /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ statsData.likes }}</div>
            <div class="stat-label">点赞数 (7天)</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :lg="16" :md="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>近 7 天数据趋势</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :lg="8" :md="24">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>数据占比</span>
            </div>
          </template>
          <div ref="pieChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { User, Document, View, Star } from '@element-plus/icons-vue'

const trendChartRef = ref<HTMLElement>()
const pieChartRef = ref<HTMLElement>()
let trendChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

// 生成最近7天日期
const getLast7Days = () => {
  const days = []
  for (let i = 6; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    days.push(`${date.getMonth() + 1}/${date.getDate()}`)
  }
  return days
}

const statsData = reactive({
  newUsers: 128,
  newArticles: 56,
  views: 12580,
  likes: 3420
})

// 模拟7天数据
const trendData = {
  dates: getLast7Days(),
  newUsers: [12, 18, 15, 22, 19, 25, 17],
  newArticles: [6, 8, 5, 10, 9, 12, 6],
  views: [1520, 1890, 1650, 2100, 1980, 2340, 1100],
  likes: [420, 480, 390, 520, 560, 610, 440]
}

const initTrendChart = () => {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['新增用户', '新增文章', '浏览数', '点赞数'],
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: 40,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trendData.dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '新增用户',
        type: 'line',
        smooth: true,
        data: trendData.newUsers,
        itemStyle: { color: '#409EFF' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      },
      {
        name: '新增文章',
        type: 'line',
        smooth: true,
        data: trendData.newArticles,
        itemStyle: { color: '#67C23A' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ])
        }
      },
      {
        name: '浏览数',
        type: 'line',
        smooth: true,
        data: trendData.views,
        itemStyle: { color: '#E6A23C' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(230, 162, 60, 0.3)' },
            { offset: 1, color: 'rgba(230, 162, 60, 0.05)' }
          ])
        }
      },
      {
        name: '点赞数',
        type: 'line',
        smooth: true,
        data: trendData.likes,
        itemStyle: { color: '#F56C6C' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.05)' }
          ])
        }
      }
    ]
  }
  trendChart.setOption(option)
}

const initPieChart = () => {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: 0,
      left: 'center'
    },
    series: [
      {
        name: '数据占比',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '42%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: statsData.newUsers, name: '新增用户', itemStyle: { color: '#409EFF' } },
          { value: statsData.newArticles, name: '新增文章', itemStyle: { color: '#67C23A' } },
          { value: statsData.views / 10, name: '浏览数(÷10)', itemStyle: { color: '#E6A23C' } },
          { value: statsData.likes, name: '点赞数', itemStyle: { color: '#F56C6C' } }
        ]
      }
    ]
  }
  pieChart.setOption(option)
}

const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

onMounted(async () => {
  await nextTick()
  initTrendChart()
  initPieChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 10px;
  border: none;
  border-radius: 8px;
  margin-bottom: 20px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 16px;
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  margin-right: 20px;
  flex-shrink: 0;
}

.stat-card-1 .stat-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card-2 .stat-icon {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card-3 .stat-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card-4 .stat-icon {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 6px;
}

.charts-row {
  margin-bottom: 0;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
}

.chart-container {
  width: 100%;
  height: 360px;
}
</style>
