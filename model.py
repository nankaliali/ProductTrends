# pip install sentence-transformers scikit-learn pandas nlpaug

import json

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import nlpaug.augmenter.word as naw

# Read JSON file
with open("data_with_hierarchical_category.json", "r", encoding="utf-8") as file:
    products = json.load(file)


product_info = [
    f"{product['product_title']} {' > '.join(product['category_full_name'].split(' > '))}"
    for product in products
]

# Define augmentation methods
synonym_aug = naw.SynonymAug(aug_src="wordnet")
random_aug = naw.RandomWordAug(action="swap")
delete_aug = naw.RandomWordAug(action="delete")


# Function to augment a single sentence using different methods
def augment_text(text):
    augmented_texts = []
    # augmented_texts.append(f"sys: {synonym_aug.augment(text)}")
    # augmented_texts.append(f"rand: {random_aug.augment(text)}")
    # augmented_texts.append(f"del: {delete_aug.augment(text)}")
    return augmented_texts


# Function to augment a list of sentences
def augment_sentences(sentences):
    augmented_sentences = []
    for sentence in sentences:
        augmented_sentences.extend(augment_text(sentence))
    return augmented_sentences


# Augment the product info
# augmented_product_info = augment_sentences(product_info)

# Flatten the list of augmented sentences and ensure all elements are strings
# flattened_augmented_product_info = [item for sublist in augmented_product_info for item in sublist if isinstance(item, str)]

# Combine original and augmented data
# combined_product_info = product_info + flattened_augmented_product_info
combined_product_info = product_info
# Check if combined_product_info contains any non-string items
print([type(item) for item in combined_product_info])

# Ensure all elements in combined_product_info are strings
combined_product_info = [str(item) for item in combined_product_info]

# Load pre-trained model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Calculate embeddings for combined product information
embeddings = model.encode(combined_product_info)

# Compute cosine similarity
similarity_matrix = cosine_similarity(embeddings)

# Convert to DataFrame for better readability
# product_titles = [product['product_title'] for product in products] + flattened_augmented_product_info
product_titles = [product["product_title"] for product in products]
similarity_df = pd.DataFrame(
    similarity_matrix, index=product_titles, columns=product_titles
)


def find_similar_products(given_product, product_info, similarity_df, top_n=20):
    # Calculate embedding for the given product
    given_product_embedding = model.encode([given_product])

    # Compute similarity between given product and all existing products
    existing_embeddings = model.encode(product_info)
    similarity_scores = cosine_similarity(
        given_product_embedding, existing_embeddings
    ).flatten()

    # Get the top_n similar products
    similar_indices = similarity_scores.argsort()[-top_n:][::-1]
    similar_products = [product_info[i] for i in similar_indices]

    return similar_products


# Given product to find similar products
given_product = "apple"

# Find and display products similar to the given product
similar_to_given_product = find_similar_products(
    given_product, combined_product_info, similarity_df
)
print("\nProducts similar to '{}': {}".format(given_product, similar_to_given_product))
