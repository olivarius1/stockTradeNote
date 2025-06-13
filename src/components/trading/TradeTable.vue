<template>
    <div class="trade-table">
        <div v-if="records.length === 0"
            class="flex items-center justify-center h-48 bg-gray-50 dark:bg-gray-800 rounded-md">
            <span class="text-gray-500">暂无数据，请先上传CSV文件</span>
        </div>
        <el-table v-else :data="records" stripe border>
            <el-table-column prop="date" label="交易日期" width="120" sortable />
            <el-table-column prop="code" label="证券代码" width="100" />
            <el-table-column prop="name" label="证券名称" width="150" show-overflow-tooltip />
            <el-table-column prop="type" label="交易类型" width="90" align="center">
                <template #default="{ row }">
                    <el-tag :type="row.type === 'buy' ? 'success' : 'danger'" size="small">
                        {{ row.type === 'buy' ? '买入' : '卖出' }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column prop="price" label="成交价格" width="110" align="right" sortable>
                <template #default="{ row }">
                    ¥{{ row.price.toFixed(2) }}
                </template>
            </el-table-column>
            <el-table-column prop="quantity" label="成交数量" width="110" align="right" sortable>
                <template #default="{ row }">
                    {{ row.quantity.toLocaleString() }}
                </template>
            </el-table-column>
            <!-- 修改点：将 '成交金额' 从 min-width 改回 width -->
            <el-table-column prop="amount" label="成交金额" width="130" align="right" sortable>
                <template #default="{ row }">
                    ¥{{ row.amount.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
                </template>
            </el-table-column>
        </el-table>
    </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useTradeStore } from '@/stores/trade'

const tradeStore = useTradeStore()
const { records } = storeToRefs(tradeStore)
</script>

<style scoped>
.trade-table {
    width: 100%;
}
</style>