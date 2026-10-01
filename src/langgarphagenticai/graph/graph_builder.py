from langgraph.graph import Stategraph
from src.langgarphagenticai.state.state import State
from langgraph.graph import START,END
from src.langgarphagenticai.nodes.basic_chatbot_node import BasicChatbotNode

class GraphBuilder:
    def __init__(self,model):
        self.llm = model
        self.graph_builder = Stategraph(State)

    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot node using langgraph nodes 
        this method initializes a chatbot node using the basichatbotnodes class and integrates it into the graph.
        """

        self.basic_chatbot_build_graph = BasicChatbotNode(self.llm)

        self.graph_builder.add_node("chatbot",self.basic_chatbot_build_graph.process)
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_edge("chatbot",END)

