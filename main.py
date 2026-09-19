import os

from dotenv import load_dotenv
from google import genai

from search import search_from_queries


load_dotenv()


def generate_queries(client, context):
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=f"""
Convert the following image description into 3 useful
image search queries for a stock photo website.

Image description:
{context}

Return only the 3 search queries, one per line.
"""
    )

    queries = response.text.strip().split("\n")

    return queries


def main():
    api_key = os.getenv("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    context = input("Describe the image you need: ")

    queries = generate_queries(client, context)

    print("\nGenerated search queries:")

    for query in queries:
        print("-", query)

    print("\nSearching Pexels...\n")

    all_images = search_from_queries(queries)

    print(f"Found {len(all_images)} images.\n")

    for image in all_images:
        print("ID:", image.id)
        print("Photographer:", image.photographer)
        print("Size:", image.width, "x", image.height)
        print("Alt:", image.alt)
        print("URL:", image.image_url)
        print("-" * 50)


if __name__ == "__main__":
    main()