from duckduckgo_search import DDGS
from modules.ui import console

def perform_search(query):
    """DuckDuckGo se search karke snippets laata hai."""
    try:
        console.print(f"[bold cyan]🌍 Searching Web for:[/bold cyan] {query}")
        # max_results=3 kaafi hai context ke liye
        results = DDGS().text(query, max_results=3)
        
        if not results:
            return "No results found."
        
        summary = "WEB SEARCH RESULTS:\n"
        for res in results:
            summary += f"Title: {res['title']}\nLink: {res['href']}\nSummary: {res['body']}\n---\n"
            
        return summary
    except Exception as e:
        console.print(f"[red]Search Error:[/red] {e}")
        return "Search failed."