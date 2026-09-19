import re


def tokenize(text):
    return set(re.findall(r"\b\w+\b", text.lower()))


def calculate_score(context, image):
    context_words = tokenize(context)
    photographer_words = tokenize(image.photographer)

    score = len(context_words.intersection(photographer_words))

    return score


def rank_images(context, images):
    ranked_images = []

    for image in images:
        score = calculate_score(context, image)

        ranked_images.append((score, image))

    ranked_images.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [image for score, image in ranked_images]