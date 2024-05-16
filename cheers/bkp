import csv
import os

class CSVPipeline:

    def open_spider(self, spider):  # Runs when the spider is opened

        self.csvfile = open('allproducts.csv', 'a+', newline='', encoding='utf-8')
        self.csvwriter = csv.DictWriter(self.csvfile, fieldnames=['category', 'name', 'link', 'price', 'updated_date'])
        if os.path.getsize('allproducts.csv') == 0:
            self.csvwriter.writeheader()

    def close_spider(self, spider):  # Runs when the spider is closed

        self.csvfile.close()

    def process_item(self, item, spider):

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
    
