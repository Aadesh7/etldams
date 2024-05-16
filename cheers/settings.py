BOT_NAME = "cheers"

SPIDER_MODULES = ["cheers.spiders"]
NEWSPIDER_MODULE = "cheers.spiders"

# Splash set up

SPLASH_URL = 'http://localhost:8050/'
# SPLASH_URL = 'http://15.206.160.139:8050/'
SPLASH_LOG_400 = True
SPLASH_LOG_ENABLED = True
DOWNLOAD_TIMEOUT = 300

DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'

HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# DOWNLOAD_TIMEOUT = 300

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Items pipeline
ITEM_PIPELINES = {
    'cheers.pipelines.MySQLPipeline': 100,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
