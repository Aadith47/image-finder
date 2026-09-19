from pexels import search_images


def search_from_queries(queries, per_query=5):
    all_images = []
    seen_ids = set()

    for query in queries:
        images = search_images(query, per_query)

        for image in images:
            if image.id not in seen_ids:
                all_images.append(image)
                seen_ids.add(image.id)

    return all_images