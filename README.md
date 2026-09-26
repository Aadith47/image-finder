# Image Finder

A Python tool that takes a plain-English description of an image and finds the best matching photos across multiple stock image platforms — Pexels, Unsplash, and Pixabay — combined, deduplicated, and ranked by relevance.

```
"a coffee on a wooden table with ChatGPT open on the laptop"
        ↓
   Gemini breaks it down and writes search queries
        ↓
   Searched across Pexels + Unsplash + Pixabay
        ↓
   Combined, deduplicated
        ↓
   Ranked by relevance (Jev)
        ↓
   Top results shown
```

## Features

- **Natural-language input** — describe what you want, no need to think in search-engine keywords
- **Structured understanding** — Gemini breaks your description into main subject, environment, device, screen content, and style, then generates 3 targeted search queries from that
- **Three image platforms searched in parallel logic** — Pexels, Unsplash, and Pixabay, all normalized into one common format
- **Cross-platform deduplication** — the same photo won't show up twice, even if different search queries surface it under different URLs
- **AI-based relevance ranking** — uses Jev (TypeSafe AI) to judge which images actually match your description, not just keyword overlap, with an automatic fallback to keyword scoring if that's unavailable
- **Resilient query generation** — if Gemini is unreachable, it falls back through five other free models on OpenRouter before giving up
- **Two ways to use it** — a command-line interface (`main.py`) and a Streamlit web UI (`app.py`)

## Project structure

```
image-finder/
├── main.py         # CLI entry point
├── app.py          # Streamlit web UI
├── graph.py        # LangGraph pipeline: query generation, search, combine, rank
├── search.py       # Runs a list of queries against one platform, dedupes results
├── pexels.py       # Pexels API wrapper
├── unsplash.py     # Unsplash API wrapper
├── pixabay.py      # Pixabay API wrapper
├── jev.py          # Jev (TypeSafe) relevance-ranking wrapper
├── ranker.py       # Fallback keyword-overlap ranker
├── models.py       # Shared Image data structure
├── .env            # API keys (not committed)
└── .gitignore
```

## How it works

The pipeline is built with **LangGraph**, which runs as a sequence of nodes sharing one state object:

```
generate_queries → search_pexels → search_unsplash → search_pixabay
                                                            ↓
                                                     combine_images
                                                            ↓
                                                       rank_images
                                                            ↓
                                                          END
```

- **`generate_queries`** — asks Gemini to break the description into structured fields and 3 search queries, using an enforced JSON schema so the response is reliably parseable. If Gemini fails, it tries five OpenRouter free-tier models in order before giving up.
- **`search_pexels` / `search_unsplash` / `search_pixabay`** — each query gets run against that platform; each platform's own results are deduplicated by `(source, id)`.
- **`combine_images`** — merges all three platforms' results into one list, deduplicated again the same way, since the same photo can otherwise appear twice with different tracking-parameter URLs.
- **`rank_images`** — sends the combined list to Jev, which judges relevance to the original description in a single call and returns a probability per image. Falls back to a simple keyword-overlap score if Jev is unavailable.

## Setup

1. Clone the repo and create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

2. Install dependencies:
   ```
   pip install langchain langchain-google-genai langchain-openai langgraph python-dotenv requests pydantic streamlit
   ```

3. Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_key_here
   PEXELS_API_KEY=your_key_here
   UNSPLASH_ACCESS_KEY=your_key_here
   PIXABAY_API_KEY=your_key_here
   OPENROUTER_API_KEY=your_key_here
   ```
   - Gemini: https://ai.google.dev/
   - Pexels: https://www.pexels.com/api/
   - Unsplash: https://unsplash.com/developers
   - Pixabay: https://pixabay.com/api/docs/
   - OpenRouter: https://openrouter.ai/ (also powers the fallback models and the Jev ranker)

## Running it

**Command line:**
```
python main.py
```

**Web UI:**
```
streamlit run app.py
```
This opens the app in your browser, where you can type a description and view results as an image gallery.

## Known limitations

- Ranking and query generation depend on external APIs (Gemini, OpenRouter, Jev); each has a fallback, but if every fallback in a chain fails, that step degrades gracefully rather than crashing (empty queries, or keyword-only ranking).
- Jev is a very new (2026) model accessed through OpenRouter's alpha Decisions API — its behavior and availability may change.
- Deduplication is exact-match on `(platform, photo id)`. Two different platforms hosting the literal same photo under two different IDs would not be caught.

## Roadmap

- [x] LangGraph pipeline with Gemini + Pexels
- [x] Add Unsplash and Pixabay
- [x] Cross-platform search, combine, and dedupe
- [x] Gemini → OpenRouter fallback chain for query generation
- [x] AI-based ranking (Jev) with keyword-overlap fallback
- [x] Structured, schema-enforced query generation
- [x] Streamlit UI
- [ ] Push to GitHub with commit history