"""
app.py
------
Streamlit front-end for the Autonomous Market Analyst.

Run locally with:
    streamlit run app.py
"""

import os
import traceback

import streamlit as st
from dotenv import load_dotenv

from crew import run_market_analysis

load_dotenv()

st.set_page_config(
    page_title="Autonomous Market Analyst",
    page_icon="📊",
    layout="centered",
)


def get_secret_or_env(key: str) -> str:
    """Looks up a key in Streamlit secrets first, then environment variables."""
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, "")


# --- Sidebar: API key configuration ---
st.sidebar.title("⚙️ Configuration")
st.sidebar.markdown(
    "Provide your API keys below. They are kept only in this browser "
    "session and are never stored on disk by this app."
)

default_google_key = get_secret_or_env("GOOGLE_API_KEY")
default_serper_key = get_secret_or_env("SERPER_API_KEY")

google_api_key = st.sidebar.text_input(
    "Google Gemini API Key",
    value=default_google_key,
    type="password",
    help="Get a key at https://aistudio.google.com/app/apikey",
)

serper_api_key = st.sidebar.text_input(
    "Serper.dev API Key",
    value=default_serper_key,
    type="password",
    help="Get a key at https://serper.dev/api-keys",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**How this works**\n\n"
    "1. A *Market Researcher* agent searches the web for the latest "
    "info on your topic.\n"
    "2. A *Content Writer* agent turns that research into a polished "
    "blog post.\n\n"
    "Built with [CrewAI](https://www.crewai.com/) + Gemini + Serper."
)

# --- Main page ---
st.title("📊 Autonomous Market Analyst")
st.caption("AI agents that research the web and write a blog post — automatically.")

topic = st.text_input(
    "What topic should the agents research and write about?",
    value="Latest trends in the AI industry",
    placeholder="e.g. Latest trends in renewable energy storage",
)

run_button = st.button("🚀 Run Market Analysis", type="primary", use_container_width=True)

if "blog_post" not in st.session_state:
    st.session_state.blog_post = None

if run_button:
    if not google_api_key or not serper_api_key:
        st.error(
            "Please provide both a Google Gemini API key and a Serper.dev "
            "API key in the sidebar before running."
        )
    elif not topic.strip():
        st.error("Please enter a topic to research.")
    else:
        with st.spinner(
            "Agents are researching and writing... this can take a minute or two."
        ):
            try:
                blog_post = run_market_analysis(
                    topic=topic.strip(),
                    google_api_key=google_api_key,
                    serper_api_key=serper_api_key,
                )
                st.session_state.blog_post = blog_post
                st.success("Done! Your blog post is ready below.")
            except Exception as e:
                st.session_state.blog_post = None
                st.error(f"Something went wrong while running the crew: {e}")
                with st.expander("Show technical details"):
                    st.code(traceback.format_exc())

if st.session_state.blog_post:
    st.markdown("---")
    st.subheader("📝 Generated Blog Post")
    st.markdown(st.session_state.blog_post)

    st.download_button(
        label="⬇️ Download as Markdown",
        data=st.session_state.blog_post,
        file_name="blog_post.md",
        mime="text/markdown",
        use_container_width=True,
    )