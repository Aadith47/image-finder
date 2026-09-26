import streamlit as st
from dotenv import load_dotenv
from graph import create_graph

load_dotenv()

st.set_page_config(
    page_title="CHITHRAM FINDER",
    page_icon="🖼️",
    layout="wide"
)

# Clean minimal CSS
st.markdown("""
<style>
    .block-container {
        padding-top: 3rem;
        max-width: 1100px;
    }
    .chithram-title {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 700;
        color: ##8AFF94;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .chithram-subtitle {
        text-align: center;
        color: #767676;
        font-size: 1rem;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 8px;
        padding: 12px 16px;
        border: 1px solid #d9d9d9;
        font-size: 0.95rem;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #1a1a1a;
        box-shadow: none;
    }
    .stButton button {
        border-radius: 8px;
        background: #1a1a1a;
        color: white;
        font-weight: 500;
        border: none;
        padding: 0.55rem 1rem;
        transition: background 0.15s ease;
    }
    .stButton button:hover {
        background: #333;
        color: white;
        border: none;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #eee;
        border-radius: 8px;
    }
    .image-card {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #eee;
        margin-bottom: 1.2rem;
    }
    .image-caption {
        padding: 0.5rem 0.7rem;
        font-size: 0.8rem;
        color: #767676;
    }
    hr {
        margin: 2rem 0;
        border-color: #eee;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='chithram-title'>CHITHRAM FINDER</div>", unsafe_allow_html=True)
st.markdown(
    "<p class='chithram-subtitle'>Describe an image and find the closest match across Pexels, Unsplash & Pixabay</p>",
    unsafe_allow_html=True
)

# Search bar
left_space, center, right_space = st.columns([1, 2, 1])

with center:
    context = st.text_input(
        "",
        placeholder="e.g. a laptop showing a dashboard on a wooden desk near a window",
        label_visibility="collapsed"
    )
    search_clicked = st.button("Search", use_container_width=True)

# Results
if search_clicked and context:
    with st.spinner("Searching Pexels, Unsplash and Pixabay..."):
        graph = create_graph()
        result = graph.invoke({
            "context": context,
            "queries": [],
            "structured_info": None,
            "pexels_images": [],
            "unsplash_images": [],
            "pixabay_images": [],
            "images": []
        })

    st.markdown("<hr>", unsafe_allow_html=True)

    if result["structured_info"]:
        info = result["structured_info"]
        with st.expander("Understood description as"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Main subject**  \n{info.get('main_subject', '—')}")
                st.markdown(f"**Environment**  \n{info.get('environment', '—')}")
                st.markdown(f"**Device**  \n{info.get('device', '—')}")
            with c2:
                st.markdown(f"**Screen content**  \n{info.get('screen_content', '—')}")
                st.markdown(f"**Style**  \n{info.get('style', '—')}")

    with st.expander("Search queries used"):
        for query in result["queries"]:
            st.write("•", query)

    st.markdown(f"**{len(result['images'])} images found**")
    st.write("")

    if result["images"]:
        columns = st.columns(3)
        for i, image in enumerate(result["images"]):
            column = columns[i % 3]
            with column:
                st.markdown("<div class='image-card'>", unsafe_allow_html=True)
                st.image(image.image_url, use_container_width=True)
                st.markdown(
                    f"<div class='image-caption'>{image.source} — {image.photographer}</div>",
                    unsafe_allow_html=True
                )
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No images found — try rephrasing your description.")

elif search_clicked and not context:
    st.warning("Type a description first.")