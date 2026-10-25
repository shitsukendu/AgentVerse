from src.agents.fact_checker_agent import fact_checker_agent


sample_state = {
    "research_results": [
        {
            "query": "LangGraph documentation",
            "sources": [
                {
                    "title": "LangGraph Documentation",
                    "url": "https://docs.langchain.com/",
                    "snippet": "Documentation for building AI agents."
                },
                {
                    "title": "Invalid Source",
                    "url": "not-a-valid-url",
                    "snippet": ""
                }
            ]
        }
    ]
}

result = fact_checker_agent(sample_state)

for item in result["checked_results"]:
    print("\nTitle:", item["title"])
    print("URL:", item["url"])
    print("Valid URL:", item["valid_url"])
    print("Has evidence:", item["has_evidence"])
    print("Verified:", item["verified"])