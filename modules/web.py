from duckduckgo_search import DDGS
import wikipedia

def perform_search(query: str) -> str:
    """
    Performs a live web search using DuckDuckGo to find real-time answers, docs, news, or solutions.
    Args:
        query (str): The search query (e.g. 'latest python 3.12 features', 'cve 2024 vulnerability').
    """
    try:
        results = DDGS().text(query, max_results=4)
        if not results:
            return f"No search results found for query: '{query}'"
        
        summary = f"WEB SEARCH RESULTS FOR '{query}':\n\n"
        for idx, res in enumerate(results, start=1):
            title = res.get('title', 'No Title')
            link = res.get('href', '')
            body = res.get('body', '')
            summary += f"[{idx}] {title}\nLink: {link}\nSummary: {body}\n\n"
        return summary
    except Exception as e:
        return f"Web search failed: {e}"

def search_wikipedia(query: str, sentences: int = 3) -> str:
    """
    Searches Wikipedia for a topic summary (useful for science, technology, concepts, history).
    Args:
        query (str): The topic to look up.
        sentences (int): Number of sentences to retrieve (default 3).
    """
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(query, sentences=sentences, auto_suggest=True)
        return f"WIKIPEDIA EXCERPT ({query}):\n{summary}"
    except wikipedia.exceptions.PageError:
        return f"Could not find a Wikipedia page matching '{query}', Sir."
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple Wikipedia entries found for '{query}': {', '.join(e.options[:4])}. Please be more specific, Sir."
    except Exception as e:
        return f"Wikipedia lookup error: {e}"