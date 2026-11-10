# LangGraph Agentic AI: Chatbot with Web Search

An agentic chatbot built with **LangGraph**, **Groq** and **Streamlit**. The main use case is a **chatbot with web search**: the LLM decides on its own when it needs fresh information, calls a search tool, reads the results, and then writes the final answer. A **Basic Chatbot** mode is included for plain conversation.

## Table of contents

- [Features](#features)
- [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Usage](#usage)
- [Code walkthrough](#code-walkthrough)
- [Extending the project](#extending-the-project)
- [Tech stack](#tech-stack)

## Features

- **Chatbot with Web Search**: an agent loop where the LLM chooses whether to call the search tool, so questions about current events or recent facts get live results.
- **Basic Chatbot**: a single-node graph for normal LLM conversation with no tools.
- **Streamlit UI**: pick the use case and Groq model, enter your API key in the sidebar, and chat.
- **Fast inference** through Groq-hosted models.
- **Modular design**: UI, LLM, graph, nodes, tools and state live in separate modules.

## How it works

### Chatbot with Web Search (main use case)

```
                 +------------------+
 START --------> |     chatbot      | ----(no tool call)----> END
                 +------------------+
                    |            ^
          (tool call requested)  |
                    v            |
                 +------------------+
                 |      tools       |
                 |  (web search)    |
                 +------------------+
```

1. The user's message enters the graph and goes to the **chatbot** node.
2. The chatbot node calls the LLM, which has the search tool bound to it (`llm.bind_tools(tools)`).
3. If the model requests a tool call, `tools_condition` routes to the **tools** node, which runs the web search.
4. The search results are added to the message history and control returns to the **chatbot** node.
5. The model reads the results and either searches again or writes the final answer. When no tool call is requested, the graph ends.

### Basic Chatbot

```
START -> chatbot -> END
```

## Project structure

```
.
├── app.py                              # entry point
├── requirements.txt
├── .env                                # API keys (never commit)
└── src/
    └── langgarphagenticai/
        ├── main.py                     # load_langgraph_agenticai_app(): wires UI, LLM and graph
        ├── LLMs/
        │   └── groqllm.py              # builds the ChatGroq model from UI input
        ├── graph/
        │   └── graph_builder.py        # builds and compiles the graphs per use case
        ├── nodes/
        │   ├── basic_chatbot_node.py   # node for the Basic Chatbot
        │   └── chatbot_with_tool_node.py  # node for the chatbot with tools
        ├── state/
        │   └── state.py                # shared graph State
        ├── tools/
        │   └── search_tool.py          # get_tools() and create_tools_node()
        └── ui/
            └── streamlit/
                ├── loadui.py           # sidebar controls and user input
                └── display_result.py   # renders graph output as chat messages
```

> The package folder is spelled `langgarphagenticai` in the imports. If you rename it, update every import.

## Getting started

### Prerequisites

- Python 3.10 or newer
- A [Groq API key](https://console.groq.com/keys)
- A [Tavily API key](https://tavily.com/) for web search (or whichever search provider your `search_tool.py` uses)

### Installation

```bash
git clone <your-repo-url>
cd <your-repo-folder>

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Suggested `requirements.txt`:

```
streamlit
langgraph
langchain
langchain-core
langchain-community
langchain-groq
tavily-python
python-dotenv
```

### Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Load it at the top of `app.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

The Groq key can also be typed into the sidebar. The app uses the sidebar value first and falls back to the `GROQ_API_KEY` environment variable. The search key is read from the environment.

> **Never commit `.env` or any API key.** Add `.env` to `.gitignore`.

### Run

```bash
streamlit run app.py
```

Open the URL Streamlit prints, usually `http://localhost:8501`.

## Usage

1. In the sidebar, choose **Chatbot with Web tool**.
2. Select a Groq model and enter your API key (or rely on the environment variable).
3. Type a message in the chat box.

Example prompts that trigger a web search:

- "What are the latest developments in LangGraph?"
- "Who won the most recent cricket match between India and Australia?"
- "What is the weather forecast for this weekend in Pune?"

Example prompts that don't need search (the model answers directly):

- "Explain what a Python decorator is."
- "Write a haiku about monsoon rain."

## Code walkthrough

### State

The graph shares one state object. Messages are appended, not overwritten, using the `add_messages` reducer:

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]
```

### Tools

`get_tools()` returns a **list** of tools and `create_tools_node()` wraps them in a `ToolNode`:

```python
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode

def get_tools():
    return [TavilySearchResults(max_results=2)]

def create_tools_node(tools):
    return ToolNode(tools=tools)
```

### Chatbot node with tools

`create_chatbot` returns a **function**, which LangGraph calls with the state:

```python
class ChatbotWithToolNode:
    def __init__(self, model):
        self.llm = model

    def create_chatbot(self, tools):
        llm_with_tools = self.llm.bind_tools(tools)

        def chatbot_node(state: State):
            return {"messages": [llm_with_tools.invoke(state["messages"])]}

        return chatbot_node
```

### Graph builder

```python
def chatbot_with_tools_build(self):
    tools = get_tools()
    tool_node = create_tools_node(tools)

    chatbot_node = ChatbotWithToolNode(self.llm).create_chatbot(tools)

    self.graph_builder.add_node("chatbot", chatbot_node)
    self.graph_builder.add_node("tools", tool_node)

    self.graph_builder.add_edge(START, "chatbot")
    self.graph_builder.add_conditional_edges("chatbot", tools_condition)
    self.graph_builder.add_edge("tools", "chatbot")
```

`tools_condition` already sends the flow to `END` when there is no tool call, so do not add a direct `chatbot -> END` edge here, or the tool loop will never run.

### Use case routing

```python
def setup_graph(self, usecase: str):
    if usecase == "Basic Chatbot":
        self.basic_chatbot_build_graph()
    elif usecase == "Chatbot with Web tool":
        self.chatbot_with_tools_build()
    else:
        raise ValueError(f"Invalid usecase: {usecase}")
    return self.graph_builder.compile()
```

The strings here must match the options in `loadui.py` exactly.

## Extending the project

To add a new use case:

1. Create a node class in `nodes/` that returns a function taking `State` and returning `{"messages": [...]}`.
2. Add a build method in `graph/graph_builder.py` that registers the nodes and edges.
3. Add a branch for it in `setup_graph()`.
4. Add the use case name to the options in `ui/streamlit/loadui.py`.

To add more tools, append them to the list in `get_tools()`. The model sees every tool in that list and chooses between them.


## Tech stack

- [LangGraph](https://langchain-ai.github.io/langgraph/) for graph-based agent workflows
- [LangChain](https://python.langchain.com/) and `langchain-groq` for the LLM interface
- [Groq](https://groq.com/) for fast LLM inference
- [Tavily](https://tavily.com/) for web search
- [Streamlit](https://streamlit.io/) for the UI

## License

Add your license here (for example MIT).