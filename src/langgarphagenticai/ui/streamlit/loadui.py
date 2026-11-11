import os
import streamlit as st

from src.langgarphagenticai.ui.uiconfigfile import Config

class LoadStreamlitUi:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def load_streamlit_ui(self):
        st.set_page_config(page_title = "🧋" + self.config.get_page_title() , layout = "wide")
        st.header("🧋" + self.config.get_page_title())

        with st.sidebar:
            llm_options = self.config.get_llm_options()
            usecase_options = self.config.get_usecase_options()

            self.user_controls["selected_llm"] = st.selectbox("Select LLM",llm_options)

            if self.user_controls["selected_llm"] == 'Groq':
                model_options = self.config.get_groq_model_options()
                self.user_controls["selected_groq_model"] = st.selectbox("Select Model",model_options)
                self.user_controls["GROQ_API_KEY"]= st.session_state["GROQ_API_KEY"]=st.text_input("Api key",type="password")

                if not self.user_controls["GROQ_API_KEY"]:
                    st.warning("Please enter your model api key")

            self.user_controls["selected_usecases"] = st.selectbox("Select Usecases",usecase_options)

            if self.user_controls["selected_usecases"] == "Chatbot with Web tool" or self.user_controls["selected_usecases"] == "AI News":
                os.environ["TAVILY_API_KEY"]=self.user_controls["TAVILY_API_KEY"] = st.session_state["TAVILY_API_KEY"] = st.text_input("TAVILY_API_KEY",type = "password")

                #validate the api key
                if not self.user_controls["TAVILY_API_KEY"]:
                    st.warning("Please enter your tavily api key to proceed.")
            if self.user_controls["selected_usecases"] == "AI News":
                st.subheader("AI News Explorer")

                with st.sidebar:
                    time_frame = st.selectbox(
                        "Select Time Frame",
                        ["Daily","Weekly","Montly"],
                        index = 0
                    )
                if st.button("Fetch News"):
                    st.session_state.IsFetchNews = True
                    st.session_state.timeframe = time_frame

                    
        return self.user_controls
