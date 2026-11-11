import streamlit as st

from src.langgarphagenticai.ui.streamlit.loadui import LoadStreamlitUi
from src.langgarphagenticai.LLMs.groqllm import GroqLLM
from src.langgarphagenticai.graph.graph_builder import GraphBuilder
from src.langgarphagenticai.ui.streamlit.display_result import DisplayResultStreamlit
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
    
    if st.session_state.IsFetchButtonClicked:
        user_message = st.session_state.timeframe
    else:
        user_message = st.chat_input("Enter your message :")

    
    if user_message:
        try:
            ##configure the llm's
            obj_llm_config = GroqLLM(user_controls_input=user_input)
            model = obj_llm_config.get_llm_model()

            if not model:
                st.error("Error :LLM model could not be initialized")
                return
    
            
            ##Graph Builder
            graph_builder = GraphBuilder(model)
            try:
                graph = graph_builder.setup_graph(usecase)
                print(user_message)
                DisplayResultStreamlit(usecase,graph,user_message).display_result_on_ui()
            except Exception as e:
                st.error(f"Error: Graph setup failed - {e}")
                return

        except Exception as e:
            st.error(f"Error: Graph setup failed - {e}")
            return