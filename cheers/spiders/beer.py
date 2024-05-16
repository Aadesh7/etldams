import scrapy

class Beer(scrapy.Spider):
    name="beer"
    head_url = 'https://cheers.com.np'
    start_urls = ['https://cheers.com.np/liquor/category?c=beer']

    def parse(self, response):
        for products in response.css('div.text-center.product-list'):
            name = products.css('a > h5::text').get()
            url = self.head_url + products.css('a::attr(href)').get()
            price = products.css('h4::text').get()
            cleaned_price = price[4:]
            yield {
                'name': name,
                'link': url,
                'price': cleaned_price
            }