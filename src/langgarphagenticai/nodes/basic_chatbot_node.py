from src.langgarphagenticai.state.state import State

class BasicChatbotNode:
    """
    Chatbot implementation function that connects in graph builder / 
    State graph pipeline
    """
    def __init__(self,model):
        self.llm = model

    def process(self,state:State) -> dict:
        """
        Response send back to the graph builder
        """
        return {"messages":self.llm.invoke(state["messages"])}
