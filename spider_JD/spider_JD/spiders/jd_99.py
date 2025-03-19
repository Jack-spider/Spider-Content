import scrapy
from scrapy_redis.spiders import RedisSpider
from DrissionPage import WebPage
from urllib.parse import quote


class JDSpider(RedisSpider):
    name = 'jd_99'
    redis_key = 'jd:start_urls'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 保留原有DrissionPage配置
        self.driver = WebPage()  # 或具体配置参数
        # self.driver.set.timeouts(implicit=20)
        self.driver.get('https://search.jd.com/Search?keyword=9.9'+quote('元')+'&qrst=1&psort=3&suggest=1.his.0.0&wq=9.9'+quote('元')+'&stock=1&psort=3&pvid=10cfb04ade9e4782a7dcab79c9d1218c&isList=0&page=33&s=961&click=0&log_id=1741959896239.7954')  # 复用原有浏览器实例

    def extract_products(self):
        """京东商品数据提取逻辑"""
        products = []
        items = self.driver.eles('xpath://*[@id="J_goodsList"]/ul/li')

        for item in items:
            products.append({
                'title': item.ele('xpath:.//div[@class="p-name"]/a/em').text,
                'price': item.ele('xpath:.//div[@class="p-price"]').text,
                'shop': item.ele('xpath:.//div[@class="p-shop"]//a').text,
                'link': item.ele('xpath:.//div[@class="p-name"]/a').attr('href')
            })
        return products

    def parse(self, response, **kwargs):
        self.driver.get(response.url)
        self.driver.run_js('window.scrollTo(0, document.body.scrollHeight)')

        # 解析产品数据
        products = self.extract_products()

        # 分页逻辑（京东典型下一页按钮特征）
        next_btn = self.driver.ele('xpath://a[@class="pn-next"]')
        if next_btn:
            next_page = next_btn.attr('href')
            if next_page and 'javascript:;' not in next_page:
                yield scrapy.Request(next_page, callback=self.parse)

        yield {'products': products}
    def closed(self, reason):
        self.driver.close()