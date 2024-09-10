from playwright.sync_api import sync_playwright


def get_product_elements(page):
    return page.query_selector_all(".product__list--item > div")


def scrape_products():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )  # Set headless=True for headless mode
        page = browser.new_page()

        with open("lulu_category.txt", "r") as file:
            links = [line.strip() for line in file.readlines()]

        with open("product_urls_lulu.txt", "a") as output_file:
            for link in links:
                page.goto(link)

                all_products = set()

                while True:
                    # Scroll down incrementally
                    page.evaluate("window.scrollBy(0, window.innerHeight)")
                    page.wait_for_timeout(2000)  # Wait for 2 seconds

                    # Get the new scroll height
                    current_height = page.evaluate(
                        "window.scrollY + window.innerHeight"
                    )
                    total_height = page.evaluate(
                        "document.documentElement.scrollHeight"
                    )

                    # Check if we have reached the bottom of the page
                    if current_height + 10 >= total_height:
                        # Scroll up by 500 pixels before breaking
                        page.evaluate("window.scrollBy(0, -500)")
                        page.wait_for_timeout(
                            2000
                        )  # Wait for 2 seconds after scrolling up
                        break

                # Get product elements after scrolling
                products = get_product_elements(page)
                for product in products:
                    product_url = product.get_attribute("data-url")
                    if product_url:
                        full_url = f"https://www.luluhypermarket.com{product_url}"
                        all_products.add(full_url)
                    else:
                        print("asd")

                print(f"Total products found: {len(all_products)}")

                # Write all product URLs to the output file
                for product_url in all_products:
                    output_file.write(f"{product_url}\n")
                    print(product_url)

        browser.close()


if __name__ == "__main__":
    scrape_products()
