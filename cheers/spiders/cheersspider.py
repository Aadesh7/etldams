import scrapy

class CheersSpider(scrapy.Spider):
    name = 'cheers'
    start_urls = ['https://cheers.com.np/']

    def parse(self, response):
        for li in response.css('li.active div.sub-menu-cateogry > ul > li'):
            link = li.css('a.container-link::attr(href)').get()
            yield {
                'link': self.start_urls[0] + link[1:]
            }