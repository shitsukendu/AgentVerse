from urllib.parse import urlparse


def fact_checker_agent(state: dict) -> dict:
    """Perform basic URL, title, and evidence quality checks."""

    research_results = state.get("research_results", [])
    checked_results = []

    for research in research_results:
        query = str(research.get("query") or "").strip()

        for source in research.get("sources", []):
            if not isinstance(source, dict):
                continue

            title = str(source.get("title") or "").strip()
            url = str(source.get("url") or "").strip()
            snippet = str(source.get("snippet") or "").strip()

            # Validate URL structure
            try:
                parsed_url = urlparse(url)

                valid_url = (
                    parsed_url.scheme in {"http", "https"}
                    and bool(parsed_url.netloc)
                    and "." in parsed_url.netloc
                    and not any(
                        char.isspace() for char in url
                    )
                )
            except ValueError:
                valid_url = False

            # Check whether useful source information exists
            has_title = bool(title)
            has_evidence = bool(snippet)

            # Assign a basic quality status
            if valid_url and has_title and has_evidence:
                quality_status = "Good"
            elif valid_url and (has_title or has_evidence):
                quality_status = "Needs Review"
            else:
                quality_status = "Poor"

            checked_results.append({
                "query": query,
                "title": title or "Untitled",
                "url": url,
                "snippet": snippet,
                "valid_url": valid_url,
                "has_title": has_title,
                "has_evidence": has_evidence,
                "quality_status": quality_status,
                "verified": False,
            })

    return {"checked_results": checked_results}