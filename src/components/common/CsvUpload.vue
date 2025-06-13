<template>
  <el-upload
    drag
    action="#"
    :show-file-list="false"
    :http-request="handleUpload"
    accept=".csv"
  >
    <el-icon class="el-icon--upload"><upload-filled /></el-icon>
    <div class="el-upload__text">
      将文件拖到此处，或<em>点击上传</em>
    </div>
    <template #tip>
      <div class="el-upload__tip">
        请上传.csv格式的文件
      </div>
    </template>
  </el-upload>
</template>

<script setup lang="ts">
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import Papa from 'papaparse'
import { useTradeStore } from '@/stores/trade'
import type { TradeRecord, RawTradeRecord } from '@/types/trading'

const tradeStore = useTradeStore()

const handleUpload = (options: any) => {
  const file = options.file
  if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
    ElMessage.error('请上传 CSV 格式的文件!')
    return
  }

  Papa.parse(file, {
    header: true,
    skipEmptyLines: true,
    complete: (results) => {
      if (results.errors.length) {
        ElMessage.error('CSV 文件解析失败')
        console.error('CSV parsing errors:', results.errors)
        return
      }
      
      try {
        const records = mapRawToTradeRecords(results.data as RawTradeRecord[])
        tradeStore.setRecords(records)
        ElMessage.success(`成功导入 ${records.length} 条记录!`)
      } catch (error: any) {
        ElMessage.error(error.message || '数据格式不正确，无法处理。')
        console.error(error)
      }
    },
    error: (error) => {
      ElMessage.error('文件读取失败')
      console.error('File reading error:', error)
    }
  })
}

const mapRawToTradeRecords = (rawRecords: RawTradeRecord[]): TradeRecord[] => {
  return rawRecords.map((raw, index) => {
    const price = parseFloat(raw['成交价格'] || raw['成交均价'] || '0')
    const quantity = parseInt(raw['成交数量'] || '0', 10)
    const amount = parseFloat(raw['成交金额'] || '0')
    const operation = raw['操作']

    if (!raw['证券代码'] || !operation || !raw['成交日期']) {
        throw new Error(`第 ${index + 2} 行数据不完整，缺少关键字段。`)
    }

    if (operation !== '买入' && operation !== '卖出') {
        throw new Error(`第 ${index + 2} 行的操作类型'${operation}'无法识别，应为'买入'或'卖出'。`)
    }
    
    if (isNaN(price) || isNaN(quantity) || isNaN(amount)) {
        throw new Error(`第 ${index + 2} 行的成交价格、数量或金额格式不正确。`)
    }

    return {
      code: raw['证券代码'],
      name: raw['证券名称'] || '',
      date: raw['成交日期'],
      type: operation === '买入' ? 'buy' : 'sell',
      price: price,
      quantity: Math.abs(quantity),
      amount: Math.abs(amount)
    }
  })
}
</script> 