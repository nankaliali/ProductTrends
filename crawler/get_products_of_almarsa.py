from playwright.sync_api import sync_playwright
import time


def get_product_elements(page):
    return page.query_selector_all(
        "#comp-kfusujon > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x > li , #comp-ki5r04ni > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x > li , #comp-kam3rhg12 > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x > li , #comp-kcejd6ul > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x > li , #comp-ki5us8lp > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x > li , #comp-kcvs5qtz > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x > li , #comp-k8yd2h3k1 > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x > li , #comp-kcvt26s51 > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x > li , #comp-k8x1h4d52 > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x > li , #comp-k8x1gax6 > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x > li , #comp-k8x1gk8u > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x >  li , ul.S4WbK_.uQ5Uah.c2Zj9x.H1ux6p > li , #comp-k8eaqu4q2 > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x > li , #comp-k8okhi0f > div > div > div > div.ehEPJs.tkJraL > section > div > ul.S4WbK_.uQ5Uah.c2Zj9x > li"
    )


def scrape_products():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )  # Set headless=True for headless mode
        page = browser.new_page()

        with open("configs/almarsa_category.txt", "r") as file:
            links = [line.strip() for line in file.readlines()]

        # name - "product_urls_almarsa_now_time.txt"
        name = f"configs/product_urls_almarsa_{time.strftime('%Y%m%d-%H%M%S')}.txt"

        with open(name, "a") as output_file:
            for link in links:
                try:
                    all_products = set()
                    last_product = None

                    output_file.write(f"####{link}\n")
                    for page_number in range(1, 15):
                        if all_products:
                            last_product = len(all_products)

                        link_page = f"{link}&page={page_number}"
                        print(f"Scraping URL: {link_page}")
                        page.goto(link_page)
                        time.sleep(5)

                        # Get product elements after scrolling
                        products = get_product_elements(page)
                        for product in products:
                            a_tag_of_product = product.query_selector(" div > div > a")
                            product_url = a_tag_of_product.get_attribute("href")
                            if product_url:
                                all_products.add(product_url)

                        print(f"Total products found: {len(all_products)}")

                        if last_product:
                            if len(all_products) == last_product:
                                break
                        else:
                            print("No products found")

                    for product_url in all_products:
                        output_file.write(f"{product_url}\n")
                        print(product_url)

                except:
                    print(f"An error occurred while scraping the URL {link_page}")

        browser.close()


if __name__ == "__main__":
    scrape_products()
