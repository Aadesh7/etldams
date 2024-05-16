<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>ETL pipeline for cheers and salesberry: liquor edition</h1><br>
    <h2>Tools and Technologies Used:</h2>
    <ul>
        <li>Python 3.12.1</li>
        <li>Docker containers for splash, mysql and phpmyadmin</li>
        <li>Github for version control</li>
        <li>Dependencies:
            <ul>
                <li>scrapy 2.11.1</li>
                <li>scrapy-splash 0.9.0</li>
                <li>mysql-connector</li>
            </ul>
        </li>
    </ul><br>
    <h2>Description of ETL pipeline:</h2><br>
    <p>The following link presents the basic ETL pipeline (in excalidraw): <a href="https://excalidraw.com/#json=W1BDrcGnY675G5-t6qDrg,W7ByJ76XOcuBUNXUAnFAKw">figure</a></p><br>
    ![Figure](https://raw.githubusercontent.com/Aadesh7/etldams/main/diagram.JPG)
    <h2>Extraction:</h2><br>
    <p>
    As shown in the figure, the liquor data is extracted from two sources. The project is an extension of previous assignment where I scraped all liquor products from cheers website. For another data source, I called salesberry store API to gather all liquor products from their website as well. The commands in run.py file were run in order specified below:</P><br>
    <ul>
        <li>scrapy crawl totalspider</li>
        <li>python getproducts.py</li>
    </ul><br>
    <p>where, totalspider was the spider for crawling where getproducts called the API. In this way, run.py file was used for orchestration. Both the commands ran files that performed extraction, transform and load on their own, which is described in detail below.</p><br>
    <h2>Transform:</h2><br>
    <p>
    Since we were gathering product data from two sources for comparision (end goal), we needed to transform the extracted data to create uniform end data to load to our desired database. The following assumptions were made to transform the data to create a uniform dataset for reporting:
    </p><br>
    <ul>
        <li>The price represented the sale value of the products, that is the price a customer would pay, and would be a datatype of float.</li>
        <li>The products were extracted through batch ingestion as the data in both websites were assumed to be updated periodically.</li>
        <li>The product names, after some transformation through cleaning, are assumed to be same from both sources.</li>
        <li>It was assumed that a lot of description in the name was unnecessary and was stripped after conversion to lower case for uniformity. For example "tuborg gold 500ml can beer" was converted to "tuborg 500ml", as only can could be 500ml, we already have beer in category and the gold served no purpose.</li>
    </ul><br>
    <p>For cheers data, the price needed to be cleaned, i.e., remove the html escape character and convert the string to float.</p><br>
    <pre>
    decoded_price = html.unescape(price) // in crawler
    prices = item['price'].split() // in pipeline
    price = prices[1].replace(',', '')
    item['price'] = float(price)
    </pre><br>
    <p>Similarly, for both cheers and salesberry data, the name had to be stripped of unnecessary descriptions as described in assumptions, and was done as shown below:</p><br>
    <pre>
        removelist = ["beer",  "bottle", "vodka", "whisky", "wine", "blonde", "strong", "bott", "btl", "gold", "extra", "can"]
        arr = product["name"].split(".")
        name = " ".join(arr)
        name = name.lower()
        words = name.split()
        words = [word for word in words if word not in removelist]
        finalname = " ".join(words)
    </pre><br>
    <h2>Load:</h2><br>
    <p>
    For loading, Mongo DB was preferred, but later I found out that Power BI integration for Mongo was limited and still in beta version, I switched to MySql. Loading for both data sources are similar with a minor difference during updation where for cheers, link is used as a unique identifying field, whereas for salesberry data, id is used.
    </p><br>
    <pre>
    def is_duplicate(self, item):
        query = "SELECT * FROM products WHERE link = %s"
        self.cursor.execute(query, (item['link'],))
        if self.cursor.fetchone():
            return True
        else:
            return False
    def insert_item(self, item):
        query = """
            INSERT INTO products (category, name, link, price, updated_date, source)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (item['category'], item['name'], item['link'], item['price'], item['updated_date'], item['source'])
        self.cursor.execute(query, values)
        self.conn.commit()
    def update_item(self, item):
        query = """
            UPDATE products
            SET category = %s, name = %s, price = %s, updated_date = %s, source = %s
            WHERE link = %s
        """
        values = (item['category'], item['name'], item['price'], item['updated_date'], item['source'], item['link'])
        self.cursor.execute(query, values)
        self.conn.commit()
    </pre><br>
    <h2>Reporting:</h2><br>
    <p>For any ETL project, there must be a final goal in mind, for example, ML, analytics or reporting. Here, I have compared the same products from two different sources and compared the prices. Power BI was used to create the graphical representation.</p><br>
    ![Figure](https://github.com/Aadesh7/etldams/blob/main/comparison.JPG)
    <h2>How to Run Locally:</h2>
    <ol>
        <li>In your preferred directory, create a virtual environment for Python.</li>
        <li>Activate it (Commonly done in Windows by running dirname\Scripts\activate.bat).</li>
        <li>Pull the main branch. Make sure Scrapy and Scrapy-Splash and mysql connector are installed.<pre>pip install scrapy scrapy-splash mysql-connector</pre></li>
        <li>Using Docker (Docker Desktop in Windows), create an image for Splash <pre>docker pull scrapinghub/splash</pre> and specify port to 8050. Also, make sure to go to <pre>http://localhost:8050</pre> to check if Splash is running. Also, make sure that is the URL in the SPLASH_URL in settings.py file.</li>
        <li>Similarly, we will need a database to connect to. We can use docker to create a mysql container and another container for phpmyadmin for our database needs.</li>
        <li>The schema creation for the final table to be loadedm with the database named liquor:</li>
        <pre>
        CREATE TABLE products (
            id INT UNIQUE,
            category VARCHAR(255),
            name VARCHAR(255),
            link VARCHAR(255) UNIQUE,
            price DECIMAL(10, 2),
            updated_date DATETIME
        );
        </pre><br>
        <li>In the main directory, run <pre>python run.py</pre>, and the script will first call the scrapy crawler and then the API caller respectively.</li>
    </ol><br>
    <h2>Conclusion:</h2>
    <p>This project was a requirement for my Data Acquisition class. I added a reporting segment where The final product data from two sources are compared with respect to their prices, which was a fun little addition to compare liquor prices and find cheap ones. This was done to clarify that ETL process is done with an end goal in mind.
    <br>
    Since this is an academic project and whatever data I scraped or used can easily be found on the main source's website which is accessible to public, I hereby declare that the project follows ethical guidelines.
    <br>
    For testing, we can compare final count in the database which should be over 2000 products and, the updated date, which should show the date and time of the last process run.
    <br>
    For further improvements:
    <br>
    We can create a cron to automate the complete orchestration of the pipeline such that we enable a batch ingestion (or in our case updation) of the data, for example lets say, every week.
    Also, we could create a webpage to show the actual comparison of the products in a visually appealing way rather than show it in a power BI graph.
    </p>
</body>
</html>
