from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate

class AINewsNode:
    def __init__(self, llm):
        """Initializes the AI News Node with a TAVILY client and a chat prompt template."""
        self.travily = TavilyClient()
        self.llm = llm
        # this is used to capture various stepsin this file so that later can be use for steps shown
        self.state ={}

    def fetch_news(self, state: dict) -> dict:
        """ 
        Fetch AI news based n the specified frequency.

        Args:
            state (dict): A dictionary containing 'frequency' .

        Returns:
            dict: updated state with "news_data" key containing fetched news.
        """
        frequency = state['messages'][0].content.lower()
        self.state['frequency'] = frequency

        time_range_map = {
            "daily": "d",
            "weekly": "w",
            "monthly": "m",
            "year":'y'
        }
        days_map = {
            "daily": 1,
            "weekly": 7,
            "monthly": 30,
            "year": 365
        }

        response = self.travily.search(
            query = "Top AI news globally",
            topic = "news",
            time_range = time_range_map[frequency],
            include_answer = "advanced",
            max_results = 20,
            days = days_map[frequency],
            #include_domain = Here we can add domain if needed
        )

        state["news_data"] = response.get("results", [])
        self.state['news_data'] = state["news_data"]
        return state
    
    def summarize_news(self, state: dict) -> dict:

        # Get news articles
        news_items = self.state["news_data"]

        # Convert dictionary into string
        news_text = ""

        for item in news_items:

            news_text += item["title"] + "\n"
            news_text += item["content"] + "\n\n"

        # Create prompt template
        prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant that summarizes news articles."),
                ("user", "Please summarize the following news articles:\n{news}")
            ]
        )

        # Send news to LLM
        chain = prompt_template | self.llm

        response = chain.invoke({"news": news_text})

        state["summary"] = response.content
        self.state["summary"] = response.content

        return state


    def save_result(self,state):
        frequency = self.state['frequency']
        summary = self.state['summary']
        filename = f"./ai_news_summary/{frequency}_summary.md"
        with open(filename, "w") as f:
            f.write(f"#{frequency.capitalize()} AI News Summary\n\n")
            f.write(summary)
        self.state['filename'] = filename
        return self.state    