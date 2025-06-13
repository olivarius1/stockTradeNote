import { defineStore } from 'pinia'
import type { TradeRecord } from '@/types/trading'

export const useTradeStore = defineStore('trade', {
    state: () => ({
        records: [] as TradeRecord[],
        selectedCode: ''
    }),

    getters: {
        uniqueCodes: (state) => {
            const codes = new Set(state.records.map(record => record.code))
            return Array.from(codes)
        },

        filteredRecords: (state) => {
            if (!state.selectedCode) return state.records
            return state.records.filter(record => record.code === state.selectedCode)
        }
    },

    actions: {
        setRecords(records: TradeRecord[]) {
            this.records = records
        },

        setSelectedCode(code: string) {
            this.selectedCode = code
        }
    }
}) 