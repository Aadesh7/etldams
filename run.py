import subprocess

# Run the Scrapy spider
def run_scrapy_spider():
    try:
        subprocess.run(['scrapy', 'crawl', 'totalspider'], check=True)
    except subprocess.CalledProcessError as e:
        print("Error running Scrapy spider:", e)

# Run the script to get products from API
def run_api_script():
    try:
        subprocess.run(['python', 'getproducts.py'], check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print("Error running API script:", e)


# Main function to orchestrate the process
def main():
    # Run the Scrapy spider
    run_scrapy_spider()
    
    # Run the script to get products from API
    run_api_script()

if __name__ == "__main__":
    main()
