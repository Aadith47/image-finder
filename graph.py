import os
import json
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from search import search_from_queries
from pexels import search_images as pexels_search
from unsplash import search_images as unsplash_search
from pixabay import search_images as pixabay_search
from ranker import rank_images
from jev import rank_with_jev


class ImageFinderState(TypedDict):
    context: str
    queries: list[str]
    structured_info: dict
    pexels_images: list
    unsplash_images: list
    pixabay_images: list
    images: list


def extract_text(response) -> str:
    # response.content can be a plain string, or a list of content blocks,
    # depending on the model/provider. Normalize both shapes into one string.
    if isinstance(response.content, str):
        return response.content

    parts = []
    for block in response.content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and "text" in block:
            parts.append(block["text"])

    return "\n".join(parts)


def parse_queries(text: str) -> list[str]:
    lines = text.strip().split("\n")

    queries = []
    for line in lines:
        cleaned = line.strip("-* \t")
        if cleaned:
            queries.append(cleaned)

    return queries


def build_prompt(context: str) -> str:
    return (
        "You analyze an image description and break it down into structured fields.\n"
        f"User description: {context}\n\n"
        "Return ONLY a JSON object, no markdown, no code fences, no extra text, "
        "with exactly these keys:\n"
        '  "main_subject": the main thing in the image\n'
        '  "environment": where the scene takes place\n'
        '  "device": any device present, or "" if none\n'
        '  "screen_content": what is on a screen, or "" if not applicable\n'
        '  "style": visual style, e.g. realistic, illustration\n'
        '  "queries": a list of exactly 3 short image-search strings\n\n'
        "Use an empty string for any field that doesn't apply."
    )


def parse_structured_response(text: str):
    # A model may still wrap JSON in a code fence even when told not to -
    # strip that off before trying to parse it.
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        queries = data.get("queries", [])
        if isinstance(queries, list) and queries:
            return data, queries
    except (json.JSONDecodeError, AttributeError):
        pass

    # JSON parsing failed or came back empty - fall back to the old
    # line-by-line style so a query still gets generated either way.
    return None, parse_queries(text)


FALLBACK_MODELS = [
    "google/gemma-4-31b-it:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "openai/gpt-oss-20b:free",
    "z-ai/glm-4.5-air:free",
    "mistralai/mistral-small-4:free",
]


def generate_queries(state: ImageFinderState) -> ImageFinderState:
    prompt = build_prompt(state["context"])

    try:
        model = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
        response = model.invoke(prompt)
        text = extract_text(response)
        print("(used Gemini)")
        structured, queries = parse_structured_response(text)
        state["structured_info"] = structured
        state["queries"] = queries
        return state

    except Exception as error:
        print(f"Gemini failed ({error}), trying OpenRouter fallbacks...")

    api_key = os.getenv("OPENROUTER_API_KEY")

    for model_name in FALLBACK_MODELS:
        try:
            fallback_model = ChatOpenAI(
                model=model_name,
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
            )
            response = fallback_model.invoke(prompt)
            text = extract_text(response)
            print(f"(used OpenRouter fallback: {model_name})")
            structured, queries = parse_structured_response(text)
            state["structured_info"] = structured
            state["queries"] = queries
            return state

        except Exception as error:
            print(f"{model_name} failed ({error}), trying next fallback...")

    print("All fallback models failed, no queries generated")
    state["structured_info"] = None
    state["queries"] = []
    return state


def search_pexels(state: ImageFinderState) -> ImageFinderState:
    images = search_from_queries(state["queries"], pexels_search, per_query=5)
    state["pexels_images"] = images
    return state


def search_unsplash(state: ImageFinderState) -> ImageFinderState:
    images = search_from_queries(state["queries"], unsplash_search, per_query=5)
    state["unsplash_images"] = images
    return state


def search_pixabay(state: ImageFinderState) -> ImageFinderState:
    images = search_from_queries(state["queries"], pixabay_search, per_query=5)
    state["pixabay_images"] = images
    return state


def combine_images(state: ImageFinderState) -> ImageFinderState:
    combined = []
    seen_keys = set()

    all_images = state["pexels_images"] + state["unsplash_images"] + state["pixabay_images"]

    for image in all_images:
        key = (image.source, str(image.id))
        if key not in seen_keys:
            seen_keys.add(key)
            combined.append(image)

    state["images"] = combined
    return state


def rank_node(state: ImageFinderState) -> ImageFinderState:
    try:
        state["images"] = rank_with_jev(state["context"], state["images"])
        print("(ranked using Jev)")

    except Exception as error:
        print(f"Jev ranking failed ({error}), falling back to keyword ranker...")
        state["images"] = rank_images(state["context"], state["images"])

    return state


def create_graph():
    graph = StateGraph(ImageFinderState)

    graph.add_node("generate_queries", generate_queries)
    graph.add_node("search_pexels", search_pexels)
    graph.add_node("search_unsplash", search_unsplash)
    graph.add_node("search_pixabay", search_pixabay)
    graph.add_node("combine_images", combine_images)
    graph.add_node("rank_images", rank_node)

    graph.set_entry_point("generate_queries")
    graph.add_edge("generate_queries", "search_pexels")
    graph.add_edge("search_pexels", "search_unsplash")
    graph.add_edge("search_unsplash", "search_pixabay")
    graph.add_edge("search_pixabay", "combine_images")
    graph.add_edge("combine_images", "rank_images")
    graph.add_edge("rank_images", END)

    return graph.compile()