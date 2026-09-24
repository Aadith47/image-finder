from dotenv import load_dotenv
from graph import create_graph

load_dotenv()


def main():
    context = input("Describe the image you need: ")

    graph = create_graph()

    result = graph.invoke({
        "context": context,
        "queries": [],
        "pexels_images": [],
        "unsplash_images": [],
        "images": []
    })

    print("\nGenerated search queries:")
    for query in result["queries"]:
        print("-", query)

    print(f"\nFound {len(result['images'])} images.\n")

    for image in result["images"]:
        print("ID:", image.id)
        print("Photographer:", image.photographer)
        print("Alt:", image.alt)
        print("URL:", image.image_url)
        print("-" * 50)


if __name__ == "__main__":
    main()