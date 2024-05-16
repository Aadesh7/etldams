import scrapy
from scrapy_splash import SplashRequest # For JS render for infinite scroll pagination
from datetime import datetime
import html

class TotalSpider(scrapy.Spider):

    name = 'totalspider'
    start_urls = ['https://www.cheers.com.np/'] # Main page of the website to be scraped

    def start_requests(self):   # Start request gets the rendered page of the provided url (extraction process)

        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint='render.html',
                args={'timeout': 90.0, 'wait': 2}
            )

    def parse(self, response):  # Link of each category is scraped through the category bar and another callback is made

        # Here, since the category url also contains the category name, we pass the category url as meta data

        category_links = response.css('li.active div.sub-menu-cateogry > ul > li > a.container-link::attr(href)').getall() # The > sign is used to get the direct descendants of the tag
        
        for category_link in category_links:
            category_url = response.urljoin(category_link)  # join the category href attribute with the url to create the actual link of the product
            yield SplashRequest(
                url=category_url,
                callback=self.parse_category,
                endpoint='render.html',
                args={'timeout': 90.0, 'wait': 2},
                meta={'category_url': category_url}
            )
    
    def parse_category(self, response):  # Products from each category is scraped here
        
        # The cheers website used infinite scrolling for pagination
        # For each category, 50 maximum products were loaded and if a user scrolled to the bottom, an ajax request would load more products, without any change in the url
        # For this main reason, splash has been used in this project to simulate scrolling as can be seen
        # One challenge was that after each ajax request, the additional products would be loaded in the same page, hence product duplication would be an issue
        # Hence, this script first scrolls down to the bottom of the page repeatedly and calculates the vertical axis of the scroll
        # If the vertical axis of the scroll remains unhanged after 2 successive scrolls, the loop breaks
        # After each scroll, 2 seconds of wait time is provided for the additional products to render successfully (initially 0.5 seconds given, but did not work properly)
        # In this way, once all the products are first loaded, only then will the products be scraped

        script = """
            function main(splash)
                -- Load the specified URL
                splash:go(splash.args.url)
                assert(splash:wait(2))  -- Wait for 2 seconds for the page to load

                local last_scroll_position = 0
                local scroll_delay = 2  -- Adjust the scroll delay if needed
                
                -- Keep scrolling until the bottom of the page is reached
                while true do
                    -- Scroll to the bottom of the page
                    splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
                    assert(splash:wait(scroll_delay))  -- Wait for the page to scroll
                    
                    -- Get the current scroll position
                    local scroll_position = splash:evaljs("window.scrollY")
                    
                    -- If no further scrolling is possible, exit the loop
                    if scroll_position == last_scroll_position then
                        break
                    else
                        -- Update the last scroll position
                        last_scroll_position = scroll_position
                    end
                end
                
                -- Return the HTML content and the final scroll position
                return {
                    html = splash:html()
                }
            end
        """  # written in lua syntax, courtesy of chatGPT and some adjustments of scroll_delay time through trial and error
        
        yield SplashRequest(
            url=response.url,
            callback=self.parse_products,
            endpoint='execute',
            args={'lua_source': script, 'timeout': 90.0, 'wait': 2},
            meta={'category_url': response.meta['category_url']}
        )

    def parse_products(self, response):
        
        category_url = response.meta.get('category_url')
        if category_url:
            category_name = category_url.split('=')[1]  # retrieval of category name, eg: snacks, mixers, beer
        else:
            category_name = "none"
        for products in response.css('div.text-center.product-list'):
            name = products.css('a > h5::text').get()
            url = self.start_urls[0] + products.css('a::attr(href)').get()  # Add head url to product url slug
            price = products.css('h4::text').get()
            decoded_price = html.unescape(price)
            # cleaned_price = self.extract_numbers(price)  # removes Rs. and the &nbsp dynamically;
            yield {
                'category': category_name,
                'name': name,
                'link': url,
                'price': decoded_price,
                'source': "cheers",
                'updated_date': datetime.now()
            }
