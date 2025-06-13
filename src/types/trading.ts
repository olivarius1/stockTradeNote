export interface TradeRecord {
    code: string;
    name: string;
    date: string;
    type: 'buy' | 'sell';
    price: number;
    quantity: number;
    amount: number;
}

// 此类型用于匹配常见的券商导出CSV文件中的中文列名
export type RawTradeRecord = {
    '成交日期': string;
    '证券代码': string;
    '证券名称': string;
    '操作': '买入' | '卖出';
    '成交均价'?: string;
    '成交价格'?: string;
    '成交数量': string;
    '成交金额': string;
    [key: string]: any; // 兼容其他可能存在的列
} 