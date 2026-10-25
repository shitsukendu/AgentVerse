from src.tools.web_search import web_search


def research_agent(state: dict) -> dict:
    """Collect, validate, and clean web search results safely."""

    tasks = state.get("tasks", [])
    research_results = []
    seen_urls = set()

    if not tasks:
        print("No research tasks were provided.")
        return {"research_results": []}

    for task in tasks:
        print(f"\nSearching the web for: {task}")

        clean_sources = []

        try:
            sources = web_search(task, max_results=5)

            if not isinstance(sources, list):
                print("Search returned an unexpected result format.")
                sources = []

        except Exception as exc:
            print(f"Search failed for task '{task}': {exc}")
            sources = []

        for source in sources:
            if not isinstance(source, dict):
                continue

            title = str(source.get("title") or "").strip()
            url = str(source.get("url") or "").strip()
            snippet = str(source.get("snippet") or "").strip()

            # Skip failed or invalid search results
            if title.lower() == "search unavailable":
                continue

            if not url.startswith(("http://", "https://")):
                continue

            # Require a title and evidence snippet
            if not title or not snippet:
                continue

            # Remove duplicate URLs
            if url in seen_urls:
                continue

            seen_urls.add(url)

            clean_sources.append({
                "title": title,
                "url": url,
                "snippet": snippet,
            })

        research_results.append({
            "query": task,
            "sources": clean_sources,
        })

        if not clean_sources:
            print(
                f"No usable search results found for task: {task}"
            )

    print(
        f"\nResearch completed. "
        f"Collected {len(seen_urls)} unique sources."
    )

    return {"research_results": research_results}