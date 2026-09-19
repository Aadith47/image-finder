# 🖼️ Image Finder

A Python CLI tool that uses **Gemini AI** to understand natural-language image descriptions and finds relevant stock photos via the **Pexels API**.

## Overview

Instead of searching with simple keywords, Image Finder lets you describe the image you need in plain English. Gemini converts your description into optimized search queries, and the tool fetches matching images from Pexels — deduplicating results automatically.

**Example:**

```text
Describe the image you need: A coffee on a table with GitHub open on a monitor
```

## Architecture

```
User prompt
    │
    ▼
┌──────────────────┐
│  main.py         │  ← Entry point & Gemini query generation
└────────┬─────────┘
         │ 3 search queries
         ▼
┌──────────────────┐
│  search.py       │  ← Orchestrates searches & deduplicates
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  pexels.py       │  ← Pexels API client
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  models.py       │  ← Image dataclass
└──────────────────┘

┌──────────────────┐
│  ranker.py       │  ← Keyword-overlap relevance ranker (available for use)
└──────────────────┘
```

## Modules

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point. Prompts the user, calls Gemini to generate 3 search queries, fetches images, and prints results. |
| `search.py` | Runs each query through the Pexels client and deduplicates results by image ID. |
| `pexels.py` | Wraps the Pexels `/v1/search` endpoint. Returns a list of `Image` objects. |
| `models.py` | Defines the `Image` dataclass (`id`, `photographer`, `width`, `height`, `image_url`, `alt`, `source`). |
| `ranker.py` | Provides a token-overlap scoring function to rank images by relevance to the original description. |

## Prerequisites

- **Python 3.10+**
- A **Gemini API key** — [Get one here](https://ai.google.dev/)
- A **Pexels API key** — [Get one here](https://www.pexels.com/api/)

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/Aadith47/image-finder.git
   cd image-finder
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install google-genai python-dotenv requests
   ```

4. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   GEMINI_API_KEY = your_gemini_api_key_here
   PEXELS_API_KEY = your_pexels_api_key_here
   ```

## Usage

```bash
python main.py
```

You'll be prompted to describe the image you need. The tool will:

1. Send your description to **Gemini 3.6 Flash** to generate 3 optimized search queries.
2. Search **Pexels** with each query (5 results per query by default).
3. Deduplicate and display the results.

**Sample output:**

```
Describe the image you need: A sunset over the ocean with a sailboat

Generated search queries:
- sunset ocean sailboat
- sailboat silhouette golden hour sea
- ocean horizon sunset boat

Searching Pexels...

Found 12 images.

ID: 1234567
Photographer: Jane Doe
Size: 4000 x 2667
Alt: Sailboat on calm ocean during sunset
URL: https://images.pexels.com/photos/...
--------------------------------------------------
```

## License

This project is open source and available under the [MIT License](LICENSE).
