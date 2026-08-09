import os
import time

import streamlit as st

from agents import build_reader_agent, build_search_agent, critic_chain, writer_chain


st.set_page_config(page_title="ResearchMind", page_icon="R", layout="wide")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');
    .stApp { background: #fafafa; color: #171717; }
    .block-container { max-width: 900px; padding: 4.5rem 1.5rem 3rem; }
    h1, h2, h3 { font-family: 'DM Sans', sans-serif; letter-spacing: -0.04em; color: #171717; }
    h1 { font-size: clamp(2.5rem, 7vw, 4.5rem); font-weight: 700; margin-bottom: 0; }
    p, label, [data-testid='stCaptionContainer'] { font-family: 'DM Sans', sans-serif; }
    [data-testid='stForm'] { border: 1px solid #dedede; border-radius: 14px; padding: 0.7rem; background: #ffffff; }
    [data-testid='stTextInput'] input { border-radius: 9px; border-color: #d7d7d7; background: #ffffff; }
    .stButton button, [data-testid='stFormSubmitButton'] button, [data-testid='stDownloadButton'] button {
        border-radius: 9px; border: 0; background: #171717; color: #ffffff; font-family: 'DM Sans', sans-serif; font-weight: 600;
    }
    .stButton button:hover, [data-testid='stFormSubmitButton'] button:hover, [data-testid='stDownloadButton'] button:hover { background: #3a3a3a; color: #ffffff; }
    [data-testid='stTabs'] button { font-family: 'DM Sans', sans-serif; font-weight: 600; }
    .eyebrow { color: #6b6b6b; font-family: 'DM Mono', monospace; font-size: 0.74rem; letter-spacing: 0.12em; text-transform: uppercase; }
    .divider { border-top: 1px solid #e3e3e3; margin: 2.5rem 0; }
    .report-meta { color: #737373; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_message_content(result):
    return result["messages"][-1].content


def run_research(topic):
    results = {}
    with st.status("Researching", expanded=True) as status:
        status.write("Finding reliable sources")
        search_agent = build_search_agent()
        search_result = search_agent.invoke(
            {"messages": [("user", f"Find recent, reliable information about: {topic}")]}
        )
        results["search"] = get_message_content(search_result)

        status.write("Reading a source")
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Based on these search results about '{topic}', select the most relevant URL "
                        f"and scrape it for deeper content.\n\nSearch Results:\n{results['search'][:800]}",
                    )
                ]
            }
        )
        results["reader"] = get_message_content(reader_result)

        status.write("Writing the report")
        research = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SOURCE CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({"topic": topic, "research": research})

        status.write("Reviewing the report")
        results["critic"] = critic_chain.invoke({"report": results["writer"]})
        status.update(label="Research complete", state="complete", expanded=False)
    return results


if "results" not in st.session_state:
    st.session_state.results = None

st.markdown('<div class="eyebrow">Multi-agent research</div>', unsafe_allow_html=True)
st.title("Research, made clear.")
st.caption("One question in. A sourced report and critical review out.")

with st.form("research_form"):
    topic = st.text_input(
        "What would you like to research?",
        placeholder="For example: the latest advances in fusion energy",
        max_chars=200,
    )
    submitted = st.form_submit_button("Run research", use_container_width=True)

if submitted:
    missing = [key for key in ("MISTRAL_API_KEY", "TAVILY_API_KEY") if not os.getenv(key)]
    if not topic.strip():
        st.warning("Enter a research topic to continue.")
    elif missing:
        st.error(f"Add {', '.join(missing)} to your app secrets before running research.")
    else:
        try:
            st.session_state.results = run_research(topic.strip())
        except Exception:
            st.session_state.results = None
            st.error("Research could not be completed. Check your API keys and available quota.")

results = st.session_state.results

if results:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.subheader("Your research")
    st.markdown('<div class="report-meta">Generated from web search and source analysis.</div>', unsafe_allow_html=True)
    report_tab, review_tab, sources_tab = st.tabs(["Report", "Review", "Research notes"])

    with report_tab:
        st.markdown(results["writer"])
        st.download_button(
            "Download report",
            data=results["writer"],
            file_name=f"research-report-{int(time.time())}.md",
            mime="text/markdown",
        )

    with review_tab:
        st.markdown(results["critic"])

    with sources_tab:
        st.caption("Search output")
        st.code(results["search"], language=None)
        st.caption("Source analysis")
        st.code(results["reader"], language=None)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.caption("ResearchMind · powered by Mistral, Tavily, and LangChain")
