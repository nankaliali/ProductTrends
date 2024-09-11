import time
import requests
from bs4 import BeautifulSoup


with open("configs/muscat_category.txt", "r") as file:
    product_urls = [line.strip() for line in file.readlines()]


name = f"data/product_urls_muscat_2.txt"

for next_url in product_urls:
    print("categort: ", next_url)
    # Open a file to write the product URLs
    with open(name, "a") as file:
        while True:
            # Send a GET request to the webpage
            response = requests.get(next_url)

            # Check if the request was successful
            if response.status_code != 200:
                print(
                    f"Failed to retrieve the webpage. Status code: {response.status_code}"
                )
                break

            # Parse the content of the request with BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")

            # Find all elements with the selector ".item.product.product-item"
            items = soup.select(".item.product.product-item")

            # Extract and write the URL of each found element to the file
            for item in items:
                url_product = item.find("a")["href"]
                file.write(url_product + "\n")

            # Find the URL for the next page
            next_button = soup.select(".action.next")
            if not next_button:
                break
            next_url = next_button[0]["href"]
            print(next_url)
