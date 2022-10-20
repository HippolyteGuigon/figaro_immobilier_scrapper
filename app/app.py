import streamlit as st
import awesome_streamlit as ast

from src import analysis,differential,filter_home,home

st.set_page_config(
        page_title="Figaro Immobilier scrapper",
    )
ast.core.services.other.set_logging_format()

# List of pages available for display
PAGES = {"Home": home,
    "Filter": filter_home,
    "Analysis": analysis,
    "Prediction": differential,
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