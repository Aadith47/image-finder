import os

import requests
from dotenv import load_dotenv

from models import Image

load_dotenv()


def search_images(query, per_page=5):
    api_key = os.getenv("PEXELS_API_KEY")

    url = "https://api.pexels.com/v1/search"

    headers = {
        "Authorization": api_key
    }

    params = {
        "query": query,
        "per_page": per_page
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    data = response.json()

    images = []

    for photo in data["photos"]:
        image = Image(
            id=photo["id"],
            photographer=photo["photographer"],
            width=photo["width"],
            height=photo["height"],
            alt=photo["alt"],
            image_url=photo["src"]["original"]
        )

        images.append(image)

    return images