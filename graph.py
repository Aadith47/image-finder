import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from search import search_from_queries
from pexels import search_images as pexels_search
from unsplash import search_images as unsplash_search
from ranker import rank_images


class ImageFinderState(TypedDict):
    context: str
    queries: list[str]
    pexels_images: list
    unsplash_images: list
    images: list


def extract_text(response) -> str:
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
        "You generate short image-search queries.\n"
        f"User description: {context}\n"
        "Give exactly 3 short search queries, one per line, "
        "no numbering, no extra text."
    )


def generate_queries(state: ImageFinderState) -> ImageFinderState:
    prompt = build_prompt(state["context"])

    try:
        model = ChatGoogleGenerativeAI(model="gemini-3.6-flash")
        response = model.invoke(prompt)
        text = extract_text(response)
        print("(used Gemini)")

    except Exception as error:
        print(f"Gemini failed ({error}), falling back to OpenRouter/Gemma...")

        fallback_model = ChatOpenAI(
            model="google/gemma-4-31b-it:free",
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        response = fallback_model.invoke(prompt)
        text = extract_text(response)
        print("(used OpenRouter fallback)")

    state["queries"] = parse_queries(text)
    return state


def search_pexels(state: ImageFinderState) -> ImageFinderState:
    images = search_from_queries(state["queries"], pexels_search, per_query=5)
    state["pexels_images"] = images
    return state


def search_unsplash(state: ImageFinderState) -> ImageFinderState:
    images = search_from_queries(state["queries"], unsplash_search, per_query=5)
    state["unsplash_images"] = images
    return state


def combine_images(state: ImageFinderState) -> ImageFinderState:
    combined = []
    seen_urls = set()

    all_images = state["pexels_images"] + state["unsplash_images"]

    for image in all_images:
        if image.image_url not in seen_urls:
            seen_urls.add(image.image_url)
            combined.append(image)

    state["images"] = combined
    return state


def rank_node(state: ImageFinderState) -> ImageFinderState:
    state["images"] = rank_images(state["context"], state["images"])
    return state


def create_graph():
    graph = StateGraph(ImageFinderState)

    graph.add_node("generate_queries", generate_queries)
    graph.add_node("search_pexels", search_pexels)
    graph.add_node("search_unsplash", search_unsplash)
    graph.add_node("combine_images", combine_images)
    graph.add_node("rank_images", rank_node)

    graph.set_entry_point("generate_queries")
    graph.add_edge("generate_queries", "search_pexels")
    graph.add_edge("search_pexels", "search_unsplash")
    graph.add_edge("search_unsplash", "combine_images")
    graph.add_edge("combine_images", "rank_images")
    graph.add_edge("rank_images", END)

    return graph.compile()