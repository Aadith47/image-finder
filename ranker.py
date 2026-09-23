def score_image(context_words, image):
    alt_words = set(image.alt.lower().split())
    matching_words = context_words.intersection(alt_words)
    return len(matching_words)


def rank_images(context, images):
    context_words = set(context.lower().split())

    scored = []
    for image in images:
        score = score_image(context_words, image)
        scored.append((score, image))

    # highest score first
    scored.sort(key=lambda pair: pair[0], reverse=True)

    ranked_images = []
    for score, image in scored:
        ranked_images.append(image)

    return ranked_images