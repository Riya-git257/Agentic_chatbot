from langgraph.graph import StateGraph
from src.langgarphagenticai.state.state import State
from langgraph.graph import START,END
from src.langgarphagenticai.nodes.basic_chatbot_node import BasicChatbotNode
from src.langgarphagenticai.tools.search_tool import get_tools,create_tools_node
from langgraph.prebuilt import ToolNode,tools_condition
from src.langgarphagenticai.nodes.chatbot_with_tool_node import ChatbotWithToolNode
from src.langgarphagenticai.nodes.ai_news_node import AINewsNode

class GraphBuilder:
    def __init__(self,model):
        self.llm = model
        self.graph_builder = StateGraph(State)

    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot node using langgraph nodes 
        this method initializes a chatbot node using the basichatbotnodes class and integrates it into the graph.
        """

        self.basic_chatbot_build_graph = BasicChatbotNode(self.llm)

        self.graph_builder.add_node("chatbot",self.basic_chatbot_build_graph.process)
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_edge("chatbot",END)

    def chatbot_with_tools_build(self):
        """
        Build a advanced chatbot graph with tool integration.
        This method creates a chatbot graph that includes both a chatbot node and tool node . it defines tools ,
        intialize the chatbot with tool capabilities and setup conditiotnal and direct edges between nodes
        The chatbot node is set as the entry point.
        """
        ## define the tool and tool node
        tools = get_tools()
        tool_node = create_tools_node(tools)

        #define the llm
        llm = self.llm

        #define the chatbot node
        obj_chatbot_with_node = ChatbotWithToolNode(llm)
        
        chatbot_node = obj_chatbot_with_node.create_chatbot(tools)

        #Add Node and create a graph

        self.graph_builder.add_node("chatbot",chatbot_node)
        self.graph_builder.add_node("tools",tool_node)

        #add condtional edges 
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_conditional_edges("chatbot",tools_condition)
        self.graph_builder.add_edge("tools","chatbot")
        self.graph_builder.add_edge("chatbot",END)


    def ai_news_builder_graph(self):
        """
        Build a graph for AI news usecase.
        This method creates a graph that includes both a chatbot node and tool node . it defines tools ,
        intialize the chatbot with tool capabilities and setup conditiotnal and direct edges between nodes
        The chatbot node is set as the entry point.
        """
        ai_news_node = AINewsNode(self.llm)

        self.graph_builder.add_node("fetch_news",ai_news_node.fetch_news)
        self.graph_builder.add_node("Summarize_news",ai_news_node.summarize_news)
        self.graph_builder.add_node("Save_news",ai_news_node.save_result)
        self.graph_builder.add_edge(START,"fetch_news")
        self.graph_builder.add_edge("fetch_news","Summarize_news")
        self.graph_builder.add_edge("Summarize_news","Save_news")
        self.graph_builder.add_edge("Save_news",END)


    def setup_graph(self,usecase: str):
        """
        Setup the graph for thr selected use case.
        """
        
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
        elif usecase == "Chatbot with Web tool":
            self.chatbot_with_tools_build()
        elif usecase == "AI News":
            self.ai_news_builder_graph()
        else:
            raise ValueError(f"Invalid usecase:{usecase}")
        
        return self.graph_builder.compile()
    
    