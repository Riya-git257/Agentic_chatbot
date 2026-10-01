import streamlit as st

from src.langgarphagenticai.ui.streamlit.loadui import LoadStreamlitUi


def load_langgraph_agenticai_app():
    """
    loads and runs the applications woth streamlit ui,
    initialozes the ui, handles user input , etc.

    """

    #load ui

    ui = LoadStreamlitUi()
    user_input = ui.load_streamlit_ui()

    if not user_input:
        st.error("Error : Failed to load user input")
        return
    
    usecase = user_input.get("selected_usecases")
    if not usecase:
        st.error("Error : No use case selected")
        return
    
    user_message = st.chat_input("Enter your message :")
