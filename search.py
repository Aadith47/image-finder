def search_from_queries(queries, search_fn, per_query=5):
    all_images = []
    seen_keys = set()

    for query in queries:
        results = search_fn(query, per_page=per_query)

        for image in results:
            key = (image.source, str(image.id))
            if key not in seen_keys:
                seen_keys.add(key)
                all_images.append(image)

    return all_images