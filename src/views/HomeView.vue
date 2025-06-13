<template>
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold text-center mb-8">网格交易账本</h1>

        <div class="grid grid-cols-1 lg:grid-cols-5 gap-8">
            <!-- Left side: Upload and Stats -->
            <div class="lg:col-span-2 space-y-8">
                <el-card>
                    <template #header>
                        <h2 class="text-xl font-semibold">数据导入</h2>
                    </template>
                    <csv-upload />
                </el-card>

                <el-card>
                    <template #header>
                        <h2 class="text-xl font-semibold">收益统计</h2>
                    </template>
                    <div class="text-center text-gray-500 py-8">
                        功能开发中...
                    </div>
                </el-card>
            </div>

            <!-- Right side: Trade Table -->
            <div class="lg:col-span-3">
                <el-card>
                    <template #header>
                        <h2 class="text-xl font-semibold">交易记录</h2>
                    </template>
                    <trade-table />
                </el-card>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import CsvUpload from '@/components/common/CsvUpload.vue'
import TradeTable from '@/components/trading/TradeTable.vue'
</script>

<style scoped>
.el-card {
    --el-card-padding: 20px;
}
</style>