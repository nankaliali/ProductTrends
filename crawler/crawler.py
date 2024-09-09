"""
This module provides a set of tools for scraping web content, managing URL
transformations, processing web pages, and preparing structured data from various web
sources. It is designed to support complex data extraction and transformation tasks,
particularly for projects involving localization and content management across
different language paths.
"""

import datetime
import random
import re
import time
from typing import Any, Dict, List
from urllib.parse import urlparse
from schema import SQLServerManager
from playwright.sync_api import ElementHandle, Page, sync_playwright
import json
import requests
import os
from sqlalchemy.exc import IntegrityError


def download_image(image_url, save_path):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(image_url, headers=headers)
    if response.status_code == 200:
        # with open(save_path, "wb") as file:
        #     file.write(response.content)
        return save_path
    else:
        print(f"Failed to download image: {response.status_code}")
        return None


def split_category(categories: list[str]) -> list[str]:
    list_category = []
    for cat in categories:
        list_category.append(cat.strip())
    return list_category[1:]


def read_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def get_element_content(
    element_handles: list[ElementHandle], element: dict[str, Any], url: str
) -> list[str]:
    """Get HTML contents of the `element_handles` wrt `element` configs.

    Args:
        element_handles (list[ElementHandle]): List of element handles.
        element (dict[str, Any]): Target element config.
        url (str): URL of current page.

    Returns:
        list[str]: List of element contents.
    """
    element_contents = []

    for element_handle in element_handles:
        html_content = None
        if "attr" in element:
            html_content = element_handle.get_attribute(element["attr"])
        elif element.get("outer_html", False):
            html_content = element_handle.evaluate("el => el.outerHTML")
        elif element.get("text_content", False):
            html_content = element_handle.text_content()
        else:
            html_content = element_handle.inner_html()

        if html_content and "regex" in element:
            match = re.search(element["regex"], html_content)
            html_content = match.group(0) if match else None

        if html_content is None:
            print(f"Failed to extract content for {element['name']} from {url}")
            continue

        html_content = html_content.strip()

        if element.get("remove_comma", False):
            html_content = (
                html_content.replace(",", "")
                .replace("<sup>", ".")
                .replace("</sup>", "")
            )

        element_contents.append(html_content)
    return element_contents


def extract_page_content(
    page: Page, url: str, config: List[Dict[str, Any]]
) -> Dict[str, Any]:
    print(f"Extracting content from URL: {url}")
    product_content = {"url": {"content": url}}

    for element in config:
        selector = element.get("selector")

        element_content = get_element_content(
            page.query_selector_all(selector), element, url
        )

        if not element_content:
            element_name = element.get("name", "Unnamed element")
            if element.get("product_identifier", False):
                print(
                    f"Product identifier element '{element_name}' not found on URL '{url}'"
                )

                return {}
            print(f"Element '{element_name}' not found on URL '{url}'")
            continue

        if element["name"] == "category":
            product_content[element["name"]] = split_category(element_content)
        else:
            product_content[element["name"]] = element_content[0]

    return product_content


def perform_scraping(income_url, config) -> Dict[str, Any]:
    contents = {}
    browser = None

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(
                headless=True,
                args=["--disable-gpu"],
            )

            page = browser.new_context().new_page()

            page.goto(income_url)

            contents.update(extract_page_content(page, income_url, config))

        except Exception as e:
            print(f"An error occurred while scraping the URL {income_url}. {str(e)}")

        finally:
            if browser is not None:
                browser.close()

    return contents


def main():
    manager = SQLServerManager(
        server="localhost,1433",
        database="master",
        username="sa",
        password="YourStrong!Passw0rd",
    )

    elements_config = read_json("almarsa-gourmet.json")
    elements = elements_config["elements"]
    organization_name = elements_config["organization_name"]

    with open("product_urls_almarsa.txt", "r") as file:
        product_urls = [line.strip() for line in file.readlines()]

    session = manager.get_session()

    try:
        for url in product_urls:
            try:
                content = perform_scraping(url, elements)
            except Exception as e:
                print(f"Failed to process URL {url}: {e}")
                continue

            try:
                manager.add_hierarchical_category(content["category"], session)
                category_id = manager.get_category_by_name(
                    content["category"][-1], session
                ).id

                image_id = None

                if content.get("image"):
                    image_filename = os.path.basename(content["image"].split("?")[0])
                    unique_substring = (
                        f"{int(time.time())}_{random.randint(10000000, 99999999)}"
                    )
                    save_path = os.path.join(
                        "images_muscat", f"{image_filename}_{unique_substring}.jpeg"
                    )
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    saved_image_path = download_image(content["image"], save_path)
                    content["image_url"] = content["image"]
                    del content["image"]
                    content["image_path"] = saved_image_path
                if content.get("image_path"):
                    image_id = manager.add_image(
                        content["image_url"], content["image_path"], session
                    )

                organization_id = manager.add_organization(organization_name, session)

                manager.add_product(
                    title=content.get("title", ""),
                    url=content.get("url", "")["content"],
                    category_id=category_id,
                    price=float(content.get("price", 0.0)),
                    description=content.get("description", ""),
                    image_id=image_id,
                    organization_id=organization_id,
                    session=session,
                )

            except Exception as e:
                session.rollback()
                continue
                print(f"Error adding product from URL {url}: {e}")

        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    main()
