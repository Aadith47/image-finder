from pexels import search_images


def search_from_queries(queries, per_query=5):
    all_images = []
    seen_ids = set()

    for query in queries:
        results = search_images(query, per_page=per_query)

        for image in results:
            if image.id not in seen_ids:
                seen_ids.add(image.id)
                all_images.append(image)

    return all_images