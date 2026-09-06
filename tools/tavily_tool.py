from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

client = TavilyClient(
    api_key= os.getenv("TAVILY_API_KEY")
)

def tavily_serach(query : str):
    response = client.search(
        query = query,
        max_results= 5,
    )

    results = []

    for i, r in enumerate(response['results'], 1):
        title = r.get("title", "unknown")
        url = r.get("url","")
        snippet = r.get("content", "").strip()
        snippet = f"{snippet[:300]}..."

        results.append(
            f"{i}. **{title}**\n {url}\n {snippet}\n"
        )

    return "\n\n".join(results)