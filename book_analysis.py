#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
豆瓣图书数据分析与可视化
功能：
1. 按分类统计各个分类的本数
2. 可视化图表展示
3. 统计其他常用指标（价格、字数、热度等）
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体以支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class BookDataAnalyzer:
    def __init__(self, csv_file='books.csv'):
        """初始化分析器"""
        self.csv_file = csv_file
        self.data = None
        self.load_data()
        
    def load_data(self):
        """加载数据"""
        try:
            self.data = pd.read_csv(self.csv_file, encoding='utf-8')
            print(f"成功加载数据，共 {len(self.data)} 条记录")
            print(f"数据列名: {list(self.data.columns)}")
        except Exception as e:
            print(f"加载数据失败: {e}")
            
    def clean_data(self):
        """清洗数据"""
        if self.data is None:
            return
            
        # 清洗价格数据
        def clean_price(price_str):
            if pd.isna(price_str):
                return 0
            # 移除￥符号和空格
            price_str = str(price_str).replace('￥', '').replace(' ', '')
            try:
                return float(price_str)
            except:
                return 0
        
        # 清洗字数数据
        def clean_word_count(word_str):
            if pd.isna(word_str):
                return 0
            # 提取数字部分
            word_str = str(word_str).replace('万字', '').replace(' ', '')
            try:
                return float(word_str) * 10000  # 转换为实际字数
            except:
                return 0
        
        self.data['原价_清洗'] = self.data['原价'].apply(clean_price)
        self.data['现价_清洗'] = self.data['现价'].apply(clean_price)
        self.data['字数_清洗'] = self.data['字数'].apply(clean_word_count)
        
        # 计算折扣率
        self.data['折扣率'] = (self.data['现价_清洗'] / self.data['原价_清洗']).fillna(1)
        self.data['优惠金额'] = self.data['原价_清洗'] - self.data['现价_清洗']
        
        print("数据清洗完成")
        
    def analyze_categories(self):
        """分析图书分类"""
        if self.data is None:
            return
            
        # 处理分类数据，有些书可能有多个分类，用+分隔
        all_categories = []
        for category in self.data['分类'].dropna():
            # 按+号分割多个分类
            cats = [cat.strip() for cat in str(category).split('+')]
            all_categories.extend(cats)
        
        # 统计各分类的数量
        category_counts = Counter(all_categories)
        
        # 转换为DataFrame便于分析
        self.category_stats = pd.DataFrame([
            {'分类': cat, '数量': count} 
            for cat, count in category_counts.items()
        ]).sort_values('数量', ascending=False)
        
        print("\n=== 分类统计结果 ===")
        print(self.category_stats.head(20))
        
        return self.category_stats
    
    def visualize_categories(self, top_n=15):
        """可视化分类统计"""
        if not hasattr(self, 'category_stats'):
            self.analyze_categories()
            
        # 创建图表，增大图表尺寸和间距
        fig, axes = plt.subplots(2, 2, figsize=(24, 18))
        fig.suptitle('豆瓣图书分类统计分析', fontsize=22, fontweight='bold', y=0.98)
        
        # 1. 条形图 - Top N 分类
        top_categories = self.category_stats.head(top_n)
        axes[0, 0].bar(range(len(top_categories)), top_categories['数量'], 
                       color='skyblue', alpha=0.7)
        axes[0, 0].set_title(f'Top {top_n} 图书分类数量统计', fontsize=16, pad=20)
        axes[0, 0].set_xlabel('分类', fontsize=12, labelpad=10)
        axes[0, 0].set_ylabel('图书数量', fontsize=12, labelpad=10)
        axes[0, 0].set_xticks(range(len(top_categories)))
        axes[0, 0].set_xticklabels(top_categories['分类'], rotation=45, ha='right', fontsize=10)
        axes[0, 0].tick_params(axis='y', labelsize=10)
        
        # 在条形图上添加数值标签，增加间距
        for i, v in enumerate(top_categories['数量']):
            axes[0, 0].text(i, v + max(top_categories['数量']) * 0.01, str(v), 
                           ha='center', va='bottom', fontsize=9)
        
        # 2. 饼图 - Top 10 分类
        top10_categories = self.category_stats.head(10)
        wedges, texts, autotexts = axes[0, 1].pie(top10_categories['数量'], 
                                                  labels=top10_categories['分类'],
                                                  autopct='%1.1f%%',
                                                  startangle=90,
                                                  textprops={'fontsize': 10},
                                                  pctdistance=0.85)
        axes[0, 1].set_title('Top 10 图书分类占比', fontsize=16, pad=20)
        
        # 调整饼图标签距离，防止重叠
        for text in texts:
            text.set_fontsize(9)
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_color('white')
            autotext.set_weight('bold')
        
        # 3. 水平条形图 - Top 20 分类
        top20_categories = self.category_stats.head(20)
        axes[1, 0].barh(range(len(top20_categories)), top20_categories['数量'],
                        color='lightcoral', alpha=0.7)
        axes[1, 0].set_title('Top 20 图书分类详细统计', fontsize=16, pad=20)
        axes[1, 0].set_xlabel('图书数量', fontsize=12, labelpad=10)
        axes[1, 0].set_ylabel('分类', fontsize=12, labelpad=10)
        axes[1, 0].set_yticks(range(len(top20_categories)))
        axes[1, 0].set_yticklabels(top20_categories['分类'], fontsize=9)
        axes[1, 0].tick_params(axis='x', labelsize=10)
        axes[1, 0].invert_yaxis()  # 倒置y轴，让最大值在顶部
        
        # 在水平条形图上添加数值标签
        for i, v in enumerate(top20_categories['数量']):
            axes[1, 0].text(v + max(top20_categories['数量']) * 0.01, i, str(v), 
                           ha='left', va='center', fontsize=8)
        
        # 4. 分类分布直方图
        axes[1, 1].hist(self.category_stats['数量'], bins=20, 
                        color='lightgreen', alpha=0.7, edgecolor='black')
        axes[1, 1].set_title('分类数量分布直方图', fontsize=16, pad=20)
        axes[1, 1].set_xlabel('每个分类的图书数量', fontsize=12, labelpad=10)
        axes[1, 1].set_ylabel('分类个数', fontsize=12, labelpad=10)
        axes[1, 1].tick_params(axis='both', labelsize=10)
        
        # 调整子图间距，防止重叠
        plt.subplots_adjust(left=0.08, bottom=0.08, right=0.95, top=0.92, 
                           wspace=0.25, hspace=0.35)
        plt.savefig('图书分类统计.png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.show()
        
    def analyze_common_metrics(self):
        """分析其他常用指标"""
        if self.data is None:
            return
            
        print("\n=== 基础统计信息 ===")
        print(f"总图书数量: {len(self.data)}")
        print(f"有价格信息的图书: {(self.data['原价_清洗'] > 0).sum()}")
        print(f"有字数信息的图书: {(self.data['字数_清洗'] > 0).sum()}")
        
        # 价格统计
        price_stats = self.data[self.data['原价_清洗'] > 0]['原价_清洗'].describe()
        print("\n=== 价格统计 (原价) ===")
        print(f"平均价格: ￥{price_stats['mean']:.2f}")
        print(f"价格中位数: ￥{price_stats['50%']:.2f}")
        print(f"最低价格: ￥{price_stats['min']:.2f}")
        print(f"最高价格: ￥{price_stats['max']:.2f}")
        print(f"价格标准差: ￥{price_stats['std']:.2f}")
        
        # 现价统计
        current_price_stats = self.data[self.data['现价_清洗'] > 0]['现价_清洗'].describe()
        print("\n=== 价格统计 (现价) ===")
        print(f"平均现价: ￥{current_price_stats['mean']:.2f}")
        print(f"现价中位数: ￥{current_price_stats['50%']:.2f}")
        
        # 折扣统计
        discount_data = self.data[(self.data['原价_清洗'] > 0) & (self.data['现价_清洗'] > 0)]
        if len(discount_data) > 0:
            avg_discount = discount_data['折扣率'].mean()
            print(f"\n=== 折扣统计 ===")
            print(f"平均折扣率: {avg_discount:.2f} ({avg_discount*100:.1f}%)")
            print(f"平均优惠金额: ￥{discount_data['优惠金额'].mean():.2f}")
            
        # 字数统计
        word_data = self.data[self.data['字数_清洗'] > 0]
        if len(word_data) > 0:
            word_stats = word_data['字数_清洗'].describe()
            print("\n=== 字数统计 ===")
            print(f"平均字数: {word_stats['mean']:.0f} 字")
            print(f"字数中位数: {word_stats['50%']:.0f} 字")
            print(f"最少字数: {word_stats['min']:.0f} 字")
            print(f"最多字数: {word_stats['max']:.0f} 字")
        
        # 热度排名统计
        print("\n=== 热度排名统计 ===")
        print(f"排名范围: {self.data['热度排名'].min()} - {self.data['热度排名'].max()}")
        print(f"前100名图书数: {(self.data['热度排名'] <= 100).sum()}")
        print(f"前500名图书数: {(self.data['热度排名'] <= 500).sum()}")
        
        return {
            'price_stats': price_stats,
            'current_price_stats': current_price_stats,
            'word_stats': word_stats if len(word_data) > 0 else None,
            'total_books': len(self.data)
        }
    
    def visualize_metrics(self):
        """可视化各项指标"""
        fig, axes = plt.subplots(2, 3, figsize=(28, 20))
        fig.suptitle('豆瓣图书各项指标分析', fontsize=24, fontweight='bold', y=0.98)
        
        # 1. 价格分布
        price_data = self.data[self.data['原价_清洗'] > 0]['原价_清洗']
        axes[0, 0].hist(price_data, bins=30, color='skyblue', alpha=0.7, edgecolor='black')
        axes[0, 0].set_title('图书价格分布', fontsize=16, pad=20)
        axes[0, 0].set_xlabel('价格 (￥)', fontsize=12, labelpad=10)
        axes[0, 0].set_ylabel('图书数量', fontsize=12, labelpad=10)
        axes[0, 0].axvline(price_data.mean(), color='red', linestyle='--', linewidth=2,
                          label=f'平均价格: ￥{price_data.mean():.2f}')
        axes[0, 0].legend(fontsize=10, loc='upper right')
        axes[0, 0].tick_params(axis='both', labelsize=10)
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 字数分布
        word_data = self.data[self.data['字数_清洗'] > 0]['字数_清洗']
        if len(word_data) > 0:
            axes[0, 1].hist(word_data/10000, bins=30, color='lightgreen', alpha=0.7, edgecolor='black')
            axes[0, 1].set_title('图书字数分布', fontsize=16, pad=20)
            axes[0, 1].set_xlabel('字数 (万字)', fontsize=12, labelpad=10)
            axes[0, 1].set_ylabel('图书数量', fontsize=12, labelpad=10)
            axes[0, 1].axvline(word_data.mean()/10000, color='red', linestyle='--', linewidth=2,
                              label=f'平均字数: {word_data.mean()/10000:.1f}万字')
            axes[0, 1].legend(fontsize=10, loc='upper right')
            axes[0, 1].tick_params(axis='both', labelsize=10)
            axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 热度排名分布
        axes[0, 2].hist(self.data['热度排名'], bins=50, color='lightcoral', alpha=0.7, edgecolor='black')
        axes[0, 2].set_title('热度排名分布', fontsize=16, pad=20)
        axes[0, 2].set_xlabel('热度排名', fontsize=12, labelpad=10)
        axes[0, 2].set_ylabel('图书数量', fontsize=12, labelpad=10)
        axes[0, 2].tick_params(axis='both', labelsize=10)
        axes[0, 2].grid(True, alpha=0.3)
        
        # 4. 价格与字数关系散点图
        valid_data = self.data[(self.data['原价_清洗'] > 0) & (self.data['字数_清洗'] > 0)]
        if len(valid_data) > 0:
            axes[1, 0].scatter(valid_data['字数_清洗']/10000, valid_data['原价_清洗'], 
                              alpha=0.6, color='purple', s=30)
            axes[1, 0].set_title('字数与价格关系', fontsize=16, pad=20)
            axes[1, 0].set_xlabel('字数 (万字)', fontsize=12, labelpad=10)
            axes[1, 0].set_ylabel('价格 (￥)', fontsize=12, labelpad=10)
            
            # 添加趋势线
            z = np.polyfit(valid_data['字数_清洗']/10000, valid_data['原价_清洗'], 1)
            p = np.poly1d(z)
            axes[1, 0].plot(valid_data['字数_清洗']/10000, p(valid_data['字数_清洗']/10000), 
                           "r--", alpha=0.8, linewidth=2, label='趋势线')
            axes[1, 0].legend(fontsize=10, loc='upper left')
            axes[1, 0].tick_params(axis='both', labelsize=10)
            axes[1, 0].grid(True, alpha=0.3)
        
        # 5. 折扣率分布
        discount_data = self.data[(self.data['折扣率'] > 0) & (self.data['折扣率'] <= 1)]
        if len(discount_data) > 0:
            axes[1, 1].hist(discount_data['折扣率'], bins=20, color='orange', alpha=0.7, edgecolor='black')
            axes[1, 1].set_title('图书折扣率分布', fontsize=16, pad=20)
            axes[1, 1].set_xlabel('折扣率', fontsize=12, labelpad=10)
            axes[1, 1].set_ylabel('图书数量', fontsize=12, labelpad=10)
            axes[1, 1].axvline(discount_data['折扣率'].mean(), color='red', linestyle='--', linewidth=2,
                              label=f'平均折扣率: {discount_data["折扣率"].mean():.2f}')
            axes[1, 1].legend(fontsize=10, loc='upper left')
            axes[1, 1].tick_params(axis='both', labelsize=10)
            axes[1, 1].grid(True, alpha=0.3)
        
        # 6. Top 10 最贵图书
        top_expensive = self.data[self.data['原价_清洗'] > 0].nlargest(10, '原价_清洗')
        bars = axes[1, 2].barh(range(len(top_expensive)), top_expensive['原价_清洗'], 
                              color='gold', alpha=0.7, height=0.6)
        axes[1, 2].set_title('Top 10 最贵图书', fontsize=16, pad=20)
        axes[1, 2].set_xlabel('价格 (￥)', fontsize=12, labelpad=10)
        axes[1, 2].set_ylabel('图书', fontsize=12, labelpad=10)
        axes[1, 2].set_yticks(range(len(top_expensive)))
        # 截断过长的书名，增加可读性
        book_names = [name[:12] + '...' if len(name) > 12 else name for name in top_expensive['书名']]
        axes[1, 2].set_yticklabels(book_names, fontsize=9)
        axes[1, 2].tick_params(axis='x', labelsize=10)
        axes[1, 2].invert_yaxis()
        axes[1, 2].grid(True, alpha=0.3, axis='x')
        
        # 在条形图上添加价格标签
        for i, (bar, price) in enumerate(zip(bars, top_expensive['原价_清洗'])):
            axes[1, 2].text(price + max(top_expensive['原价_清洗']) * 0.01, bar.get_y() + bar.get_height()/2,
                           f'￥{price:.0f}', ha='left', va='center', fontsize=8)
        
        # 调整子图间距，防止重叠
        plt.subplots_adjust(left=0.06, bottom=0.06, right=0.96, top=0.92,
                           wspace=0.25, hspace=0.35)
        plt.savefig('图书指标分析.png', dpi=300, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.show()
    
    def generate_report(self):
        """生成分析报告"""
        print("\n" + "="*60)
        print("豆瓣图书数据分析报告")
        print("="*60)
        
        # 基础统计
        metrics = self.analyze_common_metrics()
        
        # 分类统计
        category_stats = self.analyze_categories()
        
        print(f"\n=== 分类洞察 ===")
        print(f"总分类数: {len(category_stats)}")
        print(f"最热门分类: {category_stats.iloc[0]['分类']} ({category_stats.iloc[0]['数量']}本)")
        print(f"前5名分类占比: {(category_stats.head(5)['数量'].sum() / category_stats['数量'].sum() * 100):.1f}%")
        
        # 价格洞察
        if metrics['price_stats'] is not None:
            print(f"\n=== 价格洞察 ===")
            high_price_books = (self.data['原价_清洗'] > metrics['price_stats']['75%']).sum()
            low_price_books = (self.data['原价_清洗'] < metrics['price_stats']['25%']).sum()
            print(f"高价图书数量 (>75%分位数): {high_price_books}")
            print(f"低价图书数量 (<25%分位数): {low_price_books}")
        
        # 保存详细报告到文件
        with open('豆瓣图书分析报告.txt', 'w', encoding='utf-8') as f:
            f.write("豆瓣图书数据分析报告\n")
            f.write("="*60 + "\n\n")
            f.write(f"分析时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"数据文件: {self.csv_file}\n")
            f.write(f"总图书数: {len(self.data)}\n\n")
            
            # 分类统计写入文件
            f.write("分类统计 (Top 20):\n")
            f.write("-" * 30 + "\n")
            for _, row in category_stats.head(20).iterrows():
                f.write(f"{row['分类']}: {row['数量']}本\n")
            
        print(f"\n详细报告已保存至: 豆瓣图书分析报告.txt")
        
    def run_full_analysis(self):
        """运行完整分析"""
        print("开始豆瓣图书数据分析...")
        
        # 数据清洗
        self.clean_data()
        
        # 分类分析
        self.analyze_categories()
        
        # 指标分析
        self.analyze_common_metrics()
        
        # 生成可视化图表
        print("\n正在生成分类统计图表...")
        self.visualize_categories()
        
        print("正在生成指标分析图表...")
        self.visualize_metrics()
        
        # 生成报告
        self.generate_report()
        
        print("\n分析完成！生成的文件:")
        print("- 图书分类统计.png")
        print("- 图书指标分析.png") 
        print("- 豆瓣图书分析报告.txt")

def main():
    """主函数"""
    # 创建分析器实例
    analyzer = BookDataAnalyzer('books.csv')
    
    # 运行完整分析
    analyzer.run_full_analysis()
    
    # 可以单独运行某个分析功能
    # analyzer.clean_data()
    # analyzer.analyze_categories()
    # analyzer.visualize_categories(top_n=20)
    # analyzer.analyze_common_metrics()
    # analyzer.visualize_metrics()

if __name__ == "__main__":
    main()