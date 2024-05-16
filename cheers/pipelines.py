import csv
import os
import mysql.connector

class CSVPipeline:

    def open_spider(self, spider):  # Runs when the spider is opened

        self.csvfile = open('allproducts.csv', 'a+', newline='', encoding='utf-8')
        self.csvwriter = csv.DictWriter(self.csvfile, fieldnames=['category', 'name', 'link', 'price', 'updated_date'])
        if os.path.getsize('allproducts.csv') == 0:
            self.csvwriter.writeheader()

    def close_spider(self, spider):  # Runs when the spider is closed

        self.csvfile.close()

    def process_item(self, item, spider):

        # transforming name
        removelist = ["beer",  "bottle", "vodka", "whisky", "wine", "blonde", "strong", "bott", "btl", "gold", "extra", "can"]
        
        item['name'] = item['name'].lower()
        words = item['name'].split()
        words = [word for word in words if word not in removelist]
        item['name'] = " ".join(words)

        # transforming price
        # "Rs.Â 4,240"

        # item['price'] = float(item['price'])

        if not self.is_duplicate(item):
            self.csvwriter.writerow(item)
            spider.logger.info(f"Item added: {item['name']}")
        else:
            spider.logger.info(f"Item already exists: {item['name']}")
        return item

    def is_duplicate(self, item):

        with open('allproducts.csv', 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['link'] == item['link']:
                    return True
        return False
    
class MySQLPipeline:

    def open_spider(self, spider):
        self.conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='password',
            database='liquor'
        )
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):

        # transforming name
        removelist = ["beer",  "bottle", "vodka", "whisky", "wine", "blonde", "strong"]
        
        item['name'] = item['name'].lower()
        words = item['name'].split()
        words = [word for word in words if word not in removelist]
        item['name'] = " ".join(words)

        prices = item['price'].split()
        price = prices[1].replace(',', '')
        item['price'] = float(price)

        if not self.is_duplicate(item):
            self.insert_item(item)
            spider.logger.info(f"Item added: {item['name']}")
        else:
            self.update_item(item)
            spider.logger.info(f"Item updated: {item['name']}")
        return item

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