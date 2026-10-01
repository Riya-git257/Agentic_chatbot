from typing_extensions import TypedDict,List
from langgraph.graph.message import add_messages
from typing import Annotated

class State(TypedDict):
    """
    Represent the state used in the graph
    """
    message: Annotated[list,add_messages]