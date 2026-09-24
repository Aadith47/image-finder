def search_from_queries(queries, search_fn, per_query=5):
    all_images = []
    seen_urls = set()

    for query in queries:
        results = search_fn(query, per_page=per_query)

        for image in results:
            if image.image_url not in seen_urls:
                seen_urls.add(image.image_url)
                all_images.append(image)

    return all_images