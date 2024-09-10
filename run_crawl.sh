#!/bin/bash
# This script runs Docker Compose and the crawlers sequentially, and then cleans up containers and images for this project

echo "Starting Docker Compose..."
docker compose up -d
echo "Docker Compose started."

echo "Running the crawler for Almarsa Gourmet..."
python crawler/crawler.py --product_urls data/product_urls_almarsa.txt --config configs/almarsa-gourmet.json
echo "Crawler finished for Almarsa Gourmet."

echo "Running the crawler for LULU Hypermarket..."
python crawler/crawler.py --product_urls data/product_urls_lulu.txt --config configs/lulu_config.json
echo "Crawler finished for LULU Hypermarket."

echo "Running the crawler for Muscat Bakery..."
python crawler/crawler.py --product_urls data/product_urls_muscat.txt --config configs/muscat-bakery.json
echo "Crawler finished for Muscat Bakery."

echo "Shutting down Docker Compose and removing local images for this project..."
docker compose down --rmi local
echo "Docker Compose stopped and cleaned up images for this project."
