import requests
import mysql.connector
from datetime import datetime

def insert_item(conn, item):
    cursor = conn.cursor()
    query = """
        INSERT INTO products (id, name, price, category, source, updated_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (item['id'], item['name'], item['price'], item['category'], item['source'], item['updated_date'])
    cursor.execute(query, values)
    conn.commit()

def update_item(conn, item):
    cursor = conn.cursor()
    query = """
        UPDATE products
        SET name = %s, price = %s, category = %s, source = %s, updated_date = %s
        WHERE id = %s
    """
    values = (item['name'], item['price'], item['category'], item['source'], item['updated_date'], item['id'])
    cursor.execute(query, values)
    conn.commit()

def fetch_products_from_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        response_json = response.json()
        return response_json["products"]
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        return None

def filter_products(products):
    filtered_products = []
    for product in products:

        removelist = ["beer",  "bottle", "vodka", "whisky", "wine", "blonde", "strong", "bott", "btl", "gold", "extra", "can"]

        arr = product["name"].split(".")
        name = " ".join(arr)
        name = name.lower()
        words = name.split()
        words = [word for word in words if word not in removelist]
        finalname = " ".join(words)

        category = product["category"]["name"].lower()


        json_object = {}
        json_object["id"] = product["id"]
        json_object["name"] = finalname
        json_object["price"] = product["salePrice"]
        json_object["category"] = category
        json_object["source"] = "salesberry"
        json_object["updated_date"] = datetime.now()
        filtered_products.append(json_object)
    return filtered_products

def main():
    api_url = "https://api.salesberry.com.np/products?filter[where][category_id]=2633&filter[skip]=0&filter[order]=dealPrice%20DESC"
    conn = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='password',
        database='liquor'
    )

    products = fetch_products_from_api(api_url)

    if products:
        filtered_products = filter_products(products)
        for product in filtered_products:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE id = %s", (product['id'],))
            existing_product = cursor.fetchone()
            if existing_product:
                update_item(conn, product)
            else:
                insert_item(conn, product)
        print("Products successfully inserted/updated in the database.")
    conn.close()

if __name__ == "__main__":
    main()
