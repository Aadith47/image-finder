from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

from search import search_from_queries
from ranker import rank_images


class ImageFinderState(TypedDict):
    context: str
    queries: list[str]
    images: list


def generate_queries(state: ImageFinderState) -> ImageFinderState:
    model = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

    prompt = (
        "You generate short image-search queries.\n"
        f"User description: {state['context']}\n"
        "Give exactly 3 short search queries, one per line, "
        "no numbering, no extra text."
    )

    response = model.invoke(prompt)

    # response.content can be a plain string, or a list of content blocks
    # depending on the langchain-google-genai version.
    if isinstance(response.content, str):
        text = response.content
    else:
        parts = []
        for block in response.content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
        text = "\n".join(parts)

    lines = text.strip().split("\n")

    queries = []
    for line in lines:
        cleaned = line.strip("-* \t")
        if cleaned:
            queries.append(cleaned)

    state["queries"] = queries
    return state


def search_pexels(state: ImageFinderState) -> ImageFinderState:
    images = search_from_queries(state["queries"], per_query=5)
    state["images"] = images
    return state


def rank_node(state: ImageFinderState) -> ImageFinderState:
    state["images"] = rank_images(state["context"], state["images"])
    return state


def create_graph():
    graph = StateGraph(ImageFinderState)

    graph.add_node("generate_queries", generate_queries)
    graph.add_node("search_pexels", search_pexels)
    graph.add_node("rank_images", rank_node)

    graph.set_entry_point("generate_queries")
    graph.add_edge("generate_queries", "search_pexels")
    graph.add_edge("search_pexels", "rank_images")
    graph.add_edge("rank_images", END)

    return graph.compile()