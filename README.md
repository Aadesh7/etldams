<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>Cheers: A Data Scraping Project with Scrapy</h1><br>
    <h2>Tools and Technologies Used:</h2>
    <ul>
        <li>Python 3.12.1</li>
        <li>Docker 4.27.1 in local</li>
        <li>Docker image automatically built through github actions in remote (using Dockerfile)</li>
        <li>Github for version control</li>
        <li>Github actions to schedule the crawl run</li>
        <li>Dependencies:
            <ul>
                <li>scrapy 2.11.1</li>
                <li>scrapy-splash 0.9.0</li>
            </ul>
        </li>
    </ul><br>
    <h2>Project Structure:</h2>
    <pre>
    .github/workflows
    ├── scrapy_run.yml
    cheers
    ├── __pycache__ (folder)
    ├── spiders
    │   ├── __init.py__
    │   └── totalspider.py
    ├── __init.py__
    ├── middlewares.py
    ├── pipelines.py
    ├── settings.py
    ├── Dockerfile
    ├── README.md
    └── scrapy.cfg
    </pre><br>
    <h2>Description of Major Files:</h2><br>
    <h3>totalspider.py</h3>
    <p>The file contains the code for the main scraping operation. It uses the scrapy and scrapy-splash library to:
    <ul>
        <li>Request the provided URL using SplashRequest.</li>
        <li><b>Extract each category of the items available</b> (beer, whisky, wine, snacks, mixers, etc.).</li>
        <li>Go through each category link, scroll to the bottom of each category page (<b>scroll through all pagination to get all products within the category</b>) and get each product.</li>
        <li>Finally, return the following data for each product (<b>Data Schema</b> for the CSV file is the same):
            <ul>
                <li><b>category</b></li>
                <li><b>name</b></li>
                <li><b>link</b></li>
                <li><b>price</b></li>
                <li><b>updated_date</b></li>
            </ul>
        </li>
    </ul></p><br>
    <h3>pipelines.py</h3>
    <p><b>A class CSVPipeline is defined</b> here which provides following services to the registered spiders:
    <ul>
        <li>open_spider method which opens (and if not available, creates) a csv file named allproducts.csv with read and write privileges.</li>
        <li>close_spider which then closes the csv file.</li>
        <li>Each item is written with the help of another method and for each item, duplicate entry is also checked with the help of another check method.</li>
    </ul></p><br>
    <h3>settings.py</h3>
    <p>Contains the <b>configurations</b> used by the project. Some examples include splash URL used (hosted in docker hence a URL with port should be provided), timeout, middlewares. ROBOTSTXT_OBEY = False is used to bypass the robots file. It is also here that your created pipeline is registered.</p>
    <h2>Settings:</h2>
    <pre>
        BOT_NAME = "cheers"
        SPIDER_MODULES = ["cheers.spiders"]
        NEWSPIDER_MODULE = "cheers.spiders"
        # Splash set up
        SPLASH_URL = 'http://0.0.0.0:8050/'
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
            'cheers.pipelines.CSVPipeline': 100,
        }
        REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
        TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
        FEED_EXPORT_ENCODING = "utf-8"
    </pre><br>
    <h3>Dockerfile</h3>
    <p>This file is used by the GitHub actions to automatically create docker container images for splash and to expose the port (8050) used.</p><br>
    <h3>scrapy_run.yml</h3>
    <p>This is the YAML file used by the GitHub actions. The file describes how to set up the environment, download required dependencies and build docker images if any such that the crawler can be run. It is also here that the schedule is specified. For this project, I have specified the cron syntax as cron: '0 0 * * 6' which means it runs on Saturday at 12 am every week.</p><br>
    <h2>complete Yaml file:</h2>
    <pre>
        name: Scrapy Run Job
        on:
        schedule:
            - cron: '0 0 * * 6'
        # on:
        #   push:
        #     branches:
        #       - main
        jobs:
        scrape:
            runs-on: ubuntu-latest
            steps:
            - name: Checkout code
                uses: actions/checkout@v2
            - name: Set up Python
                uses: actions/setup-python@v2
                with:
                python-version: '3.12.1'
            - name: Install dependencies
                run: |
                pip install scrapy scrapy-splash
            - name: Build Docker Image
                run: |
                docker build -t splash-image -f Dockerfile .
                working-directory: ${{ github.workspace }}
            - name: Run Splash Container
                run: |
                docker run -d -p 8050:8050 --name splash-container splash-image
                sleep 10
                continue-on-error: true
            - name: Test Splash availability
                run: |
                curl -sSf http://0.0.0.0:8050/render.html?url=www.cheers.com.np > /dev/null
                continue-on-error: false
            - name: Run Scrapy spider
                run: scrapy crawl totalspider
            - name: Upload CSV artifact
                uses: actions/upload-artifact@v2
                with:
                name: allproducts
                path: allproducts.csv
    </pre><br>
    <h2>How to Run Locally:</h2>
    <ol>
        <li>In your preferred directory, create a virtual environment for Python.</li>
        <li>Activate it (Commonly done in Windows by running dirname\Scripts\activate.bat).</li>
        <li>Pull the main branch. Make sure Scrapy and Scrapy-Splash are installed.<pre>pip install scrapy scrapy-splash</pre></li>
        <li>Using Docker (Docker Desktop in Windows), create an image for Splash <pre>docker pull scrapinghub/splash</pre> and specify port to 8050. Also, make sure to go to <pre>http://localhost:8050</pre> to check if Splash is running. Also, make sure that is the URL in the SPLASH_URL in settings.py file.</li>
        <li>In the main directory, run <pre>scrapy crawl totalspider</pre>, and the crawler will scrape the website and download all the products and write in allproducts.csv which can be found in the main directory. For successive runs, the script will update the products rather than add duplicate ones.</li>
    </ol><br>
    <h2>Conclusion:</h2>
    <p>This project was a requirement for my Data Acquisition class. It involves data scraping for multiple pages and just for fun I also updated it to get data from multiple categories, i.e., multiple links.
    <br>
    Since I had to use Splash to get to multiple pages (pagination was implemented dynamically through infinite pagination), I have also utilized Docker to create a Splash image in the GitHub actions environment to smoothly run the Splash dependency. I tried creating a Lightsail instance to host the Docker image with Splash to utilize it remotely, but due to the networking overhead, some issues were faced, hence I decided to build the Docker environment using GitHub actions.
    <br>
    While the requirement was to update the same file over and over, since we can download the CSV file created using artifacts download feature from GitHub actions, I have utilized that feature. However, I have written the update logic in the pipeline class so that while running locally or in a different environment, the same file can be updated successively rather than creating a new file.</p>
</body>
</html>
