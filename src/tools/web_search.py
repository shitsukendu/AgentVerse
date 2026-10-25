from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web safely and return clean search results."""

    query = str(query).strip()

    if not query:
        return []

    if max_results < 1:
        return []

    try:
        results = DDGS().text(
            query,
            max_results=max_results,
        )

        if not results:
            return []

        clean_results = []

        for item in results:
            if not isinstance(item, dict):
                continue

            title = str(item.get("title") or "").strip()
            url = str(item.get("href") or "").strip()
            snippet = str(item.get("body") or "").strip()

            if not title or not url:
                continue

            clean_results.append({
                "title": title,
                "url": url,
                "snippet": snippet,
            })

        return clean_results

    except Exception as exc:
        print(f"Web search failed for query '{query}': {exc}")
        return []


if __name__ == "__main__":
    test_query = "LangGraph official documentation"

    for result in web_search(test_query, 3):
        print(f"\nTitle: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"Snippet: {result['snippet']}")

    print("\nWeb search test completed.")