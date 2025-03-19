# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from pandas import pd

class DataAnalysisPipeline:
    def process_item(self, item, spider):
        df = pd.DataFrame(item['products'])

        # 执行数据清洗
        df = df.drop_duplicates(subset=['name'])
        df['price'] = df['price'].str.extract(r'(\d+\.\d+)').astype(float)

        # 数据分析示例
        price_dist = df['price'].describe()
        print(f"价格分布统计:\n{price_dist}")

        # 保存增强版数据
        df.to_csv('enhanced_products.csv', index=False)
        return item
