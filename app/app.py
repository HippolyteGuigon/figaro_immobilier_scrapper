import streamlit as st
import awesome_streamlit as ast
import sys

from src import analysis, home, filter_home

st.set_page_config(
    page_title="Figaro Immobilier scrapper",
)
ast.core.services.other.set_logging_format()

# List of pages available for display
PAGES = {
    "Home": home,
    "Filter": filter_home,
    "Analysis": analysis,
}


def main():
    """Core of the app - switches between 'tabs' thanks to the sidebar"""
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Visit", list(PAGES.keys()))

    page = PAGES[selection]

    with st.spinner("Loading {} ...".format(selection)):
        ast.shared.components.write_page(page)


if __name__ == "__main__":
    main()
