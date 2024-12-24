"""
读取这样的csv(数据是通过通义chat解析截图给到的)
"名称/代码,日期,交易类型,数量,价格,金额,手续费"
name/code,date,type,number,price,amount,brokerage
银行ETF/512800,2024-10-21 14:47:28,B,3500,1.416,4956.00,0.89

字段含义:
    name/code: 名称/代码
    date: 交易日期
    type: 交易类型 B:买入 S:卖出 D:分红
    number: 持有数量(分红时为参与分红的股数)
    price: 交易价格/每股分红
    amount: 交易金额/分红金额
    brokerage: 手续费(分红时通常为0)
"""

import csv
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List


@dataclass
class Trade:
    name: str
    code: str
    date: datetime
    type: str  # 'B' for buy, 'S' for sell, 'D' for dividend
    number: int
    price: Decimal
    amount: Decimal
    brokerage: Decimal

class StockAnalyzer:
    def __init__(self):
        self.trades: List[Trade] = []
        self.holdings = {}  # {code: {'number': int, 'cost': Decimal}}
    
    def load_from_csv(self, filepath: str):
        trades_temp = []  # 临时存储所有交易记录
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name_code = row['name/code'].split('/')
                name, code = name_code[0], name_code[1]
        
                # 处理日期，允许为空
                date = None
                if row['date']:
                    date_str = row['date'].strip()
                    date_formats = [
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%d %H:%M',
                        '%Y-%m-%d %H%M%S',
                        '%Y%m%d %H%M%S'
                    ]
                    
                    for fmt in date_formats:
                        try:
                            date = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue

                # 如果amount为空，使用number和price计算
                amount = row['amount']
                if not amount or amount.strip() == '':
                    number = int(row['number'])
                    price = Decimal(str(row['price']))
                    amount = str(number * price)

                trade = Trade(
                    name=name,
                    code=code,
                    date=date,
                    type=row['type'],
                    number=int(row['number']),
                    price=Decimal(str(row['price'])),
                    amount=Decimal(str(amount)),
                    brokerage=Decimal(str(row['brokerage']))
                )
                trades_temp.append(trade)

            # 按日期排序 时间从早到晚
            trades_temp.sort(key=lambda x: x.date if x.date else datetime.max)
            
            # 更新交易记录和持仓
            self.trades = trades_temp
            self.holdings = {}  # 重置持仓信息
            for trade in self.trades:
                self._update_holdings(trade)

    def _update_holdings(self, trade: Trade):
        """
        更新持仓信息，使用LIFO（后进先出）原则处理交易
        """
        if trade.code not in self.holdings:
            self.holdings[trade.code] = {
                'number': 0, 
                'cost': Decimal('0'),
                'transactions': [],          # 记录每笔买入交易
                'diluted_cost': Decimal('0') # 新增：单独跟踪摊薄成本
            }
        
        holding = self.holdings[trade.code]
        
        if trade.type == 'B':  # 买入
            # 记录本次买入交易��详细信息
            holding['transactions'].append({
                'number': trade.number,
                'price': trade.price,
                'remaining': trade.number,
                'date': trade.date
            })
            # 更新总持仓数量
            holding['number'] += trade.number
            
            # 计算摊薄成本：考虑所有历史交易
            old_cost = holding['diluted_cost'] * (holding['number'] - trade.number)
            new_cost = trade.amount + trade.brokerage
            holding['diluted_cost'] = (old_cost + new_cost) / holding['number']
            
            # 计算实际成本：只考虑当前未卖出的股票
            total_cost = sum(tx['remaining'] * tx['price'] for tx in holding['transactions'])
            total_shares = sum(tx['remaining'] for tx in holding['transactions'])
            holding['cost'] = total_cost / total_shares if total_shares > 0 else Decimal('0')
            
        elif trade.type == 'S':  # 卖出
            remaining_to_sell = trade.number
            
            # 按照LIFO原则处理卖出
            for tx in reversed(holding['transactions']):
                if remaining_to_sell <= 0:
                    break
                    
                if tx['remaining'] > 0:
                    sold_from_this_tx = min(tx['remaining'], remaining_to_sell)
                    tx['remaining'] -= sold_from_this_tx
                    remaining_to_sell -= sold_from_this_tx
            
            # 更新持仓数量
            old_number = holding['number']
            holding['number'] -= trade.number
            
            # 更新摊薄成本：保持每股摊薄成本不变
            if holding['number'] > 0:
                # 摊薄成本保持不变
                # 实际成本需要重新计算
                total_cost = sum(tx['remaining'] * tx['price'] for tx in holding['transactions'])
                total_shares = sum(tx['remaining'] for tx in holding['transactions'])
                holding['cost'] = total_cost / total_shares if total_shares > 0 else Decimal('0')
            else:
                holding['cost'] = Decimal('0')
                holding['diluted_cost'] = Decimal('0')
                holding['transactions'] = []

    def get_position_summary(self):
        """
        获取当前持仓摘要
        """
        summary = {}
        for code, holding in self.holdings.items():
            if holding['number'] > 0:
                # 计算实际成本
                total_shares = sum(tx['remaining'] for tx in holding['transactions'])
                total_cost = sum(tx['remaining'] * tx['price'] for tx in holding['transactions'])
                actual_cost = total_cost / total_shares if total_shares > 0 else Decimal('0')
                
                summary[code] = {
                    'number': holding['number'],
                    'diluted_cost': round(holding['diluted_cost'], 3),  # 使用单独跟踪的摊薄成本
                    'actual_cost': round(actual_cost, 3),               # 使用实际成本
                    'total_cost': round(actual_cost * holding['number'], 2)
                }
        return summary

    def calculate_profit(self):
        profits = {}
        for code in set(trade.code for trade in self.trades):
            profits[code] = Decimal('0')
            for trade in self.trades:
                if trade.code == code:
                    if trade.type == 'S':  # 卖出
                        # 卖出收入减去手续费，是正收益
                        profits[code] += (trade.amount - trade.brokerage)
                    elif trade.type == 'B':  # 买入
                        # 买入支出加上手续费，是负收益
                        profits[code] -= (trade.amount + trade.brokerage)
                    elif trade.type == 'D':  # 分红
                        # 分红是正收益
                        profits[code] += trade.amount
        return {code: round(profit, 2) for code, profit in profits.items()}

    def generate_report(self, output_file: str):
        """生成交易明细和持仓报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            # 按代码排序处理所有持仓
            for code in sorted(set(trade.code for trade in self.trades)):
                name = next(t.name for t in self.trades if t.code == code)
                holding = self.holdings.get(code)
                
                if holding and holding['number'] > 0:
                    f.write(f"{name}({code}):\n")
                    f.write("交易明细:\n")
                    
                    # 输出该股票的所有交易记录
                    for trade in sorted(
                        (t for t in self.trades if t.code == code),
                        key=lambda x: x.date if x.date else datetime.max
                    ):
                        if trade.date:
                            date_str = trade.date.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            date_str = ''
                        
                        f.write(f"  {date_str},{trade.type},{trade.number},"
                               f"{trade.price},{trade.amount:.2f},{trade.brokerage:.2f}\n")
                    
                    # 输出当前持仓信息
                    f.write(f"  当前持有数量: {holding['number']:,} 股\n")
                    f.write(f"  摊薄成本: {round(holding['diluted_cost'], 3):.3f} 元/股\n")
                    f.write(f"  实际成本: {round(holding['cost'], 3):.3f} 元/股\n\n")

analyzer = StockAnalyzer()
analyzer.load_from_csv('data_example.csv')
analyzer.generate_report('stock_report.txt')