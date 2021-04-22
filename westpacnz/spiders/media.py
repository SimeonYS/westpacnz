import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import WwestpacnzItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'

class MediaSpider(scrapy.Spider):
    name = 'media'
    start_urls = ['https://www.westpac.co.nz/about-us/media/']
    ITEM_PIPELINES = {
        'media.pipelines.WwestpacnzPipeline': 300,

    }
    def parse(self, response):
        post_links = response.xpath('//h2/a/@href').getall()
        yield from response.follow_all(post_links, self.parse_post)

        next_page = response.xpath('//a[@class="pagination__item pagination__item--next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_post(self, response):
        date = response.xpath('//span[@class="blog-post-content-block__date"]/text()').get()
        title = response.xpath('//h1/text()').get()
        content = response.xpath('//div[@class="blog-post-content-block__content"]//text()').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=WwestpacnzItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()

