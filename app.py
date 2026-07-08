import os
import traceback
import streamlit as st
from crew import run_market_analysis


def get_secret_or_env(key):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, "")


st.set_page_config(
    page_title="Autonomous Market Analyst",
    page_icon="📊",
    layout="centered",
)

st.sidebar.title("⚙️ Configuration")

google_api_key = st.sidebar.text_input(
    "Google Gemini API Key",
    value=get_secret_or_env("GOOGLE_API_KEY"),
    type="password",
)

serper_api_key = st.sidebar.text_input(
    "Serper.dev API Key",
    value=get_secret_or_env("SERPER_API_KEY"),
    type="password",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**How this works**\n\n"
    "1. Searches the web for latest info on your topic\n"
    "2. AI writes a polished blog post from the research\n\n"
    "Powered by Google Gemini + Serper.dev"
)

st.title("📊 Autonomous Market Analyst")
st.caption("AI agents that research the web and write a blog post — automatically.")

topic = st.text_input(
    "What topic should the agents research?",
    value="Latest trends in the AI industry",
)

run_button = st.button("🚀 Run Market Analysis", type="primary", use_container_width=True)

if "blog_post" not in st.session_state:
    st.session_state.blog_post = None

if run_button:
    if not google_api_key or not serper_api_key:
        st.error("Please provide both API keys in the sidebar.")
    elif not topic.strip():
        st.error("Please enter a topic to research.")
    else:
        with st.spinner("Agents are researching and writing... this takes 1-2 minutes."):
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
                st.error(f"Error: {e}")
                with st.expander("Technical details"):
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
