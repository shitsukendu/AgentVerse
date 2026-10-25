from src.agents.research_agent import research_agent


result = research_agent({
    "tasks": ["LangGraph official documentation"]
})

print("\n=== Research Results ===")

for research in result["research_results"]:
    print(f"\nQuery: {research['query']}")

    for source in research["sources"]:
        print(f"\nTitle: {source['title']}")
        print(f"URL: {source['url']}")
        print(f"Snippet: {source['snippet'][:200]}")