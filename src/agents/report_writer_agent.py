import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


def generate_ai_summary(
    question: str,
    snippets: list[dict],
) -> str:
    """Generate a research summary with consistent source references."""

    if not api_key:
        return "Gemini API key not found. Please check your .env file."

    if not snippets:
        return "No research snippets available for summarization."

    try:
        client = genai.Client(api_key=api_key)

        source_blocks = []

        for source in snippets[:10]:
            source_blocks.append(
                f"[Source {source['index']}]\n"
                f"Title: {source['title']}\n"
                f"URL: {source['url']}\n"
                f"Snippet: {source['snippet']}"
            )

        research_text = "\n\n".join(source_blocks)

        prompt = f"""
You are a research assistant for the AgentVerse platform.

Research question:
{question}

Collected research sources:
{research_text}

Write a concise, professional research summary that:
- Answers the research question using the supplied sources.
- Highlights the main findings.
- Adds citations such as [Source 1] or [Source 2]
  to the claims supported by those sources.
- Uses only source numbers explicitly provided above.
- Never renumbers sources.
- Never invents facts or unsupported claims.
- Clearly states when the available evidence is insufficient.

Treat all snippets as unverified source material.
Do not claim that a source is factually verified.
Write in clear, professional English.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        summary = (response.text or "").strip()

        if not summary:
            return "Gemini returned an empty summary."

        return summary

    except Exception as exc:
        print(f"Gemini summary generation failed: {exc}")
        return (
            "AI summary unavailable. Please check the API key, "
            "model access, quota, or network."
        )


def report_writer_agent(state: dict) -> dict:
    """Generate a structured research report from checked sources."""

    question = state.get(
        "question",
        "No research question provided",
    )
    checked_results = state.get("checked_results", [])

    # Calculate source quality statistics
    total_sources = len(checked_results)

    valid_urls = sum(
        1 for item in checked_results
        if item.get("valid_url", False)
    )

    sources_with_evidence = sum(
        1 for item in checked_results
        if item.get("has_evidence", False)
    )

    good_sources = sum(
        1 for item in checked_results
        if item.get("quality_status") == "Good"
    )

    needs_review = sum(
        1 for item in checked_results
        if item.get("quality_status") == "Needs Review"
    )

    poor_sources = sum(
        1 for item in checked_results
        if item.get("quality_status") == "Poor"
    )

    # Keep the original source numbering for the entire report.
    # Sources without snippets are skipped for AI summarization,
    # but their original source numbers are preserved.
    summary_sources = []

    for index, item in enumerate(checked_results, start=1):
        snippet = item.get("snippet", "").strip()

        if not snippet:
            continue

        summary_sources.append({
            "index": index,
            "title": item.get("title") or "Untitled",
            "url": item.get("url") or "N/A",
            "snippet": snippet,
        })

    # Generate the AI summary using the original source numbers.
    findings_summary = generate_ai_summary(
        question,
        summary_sources,
    )

    # Create report overview
    report_lines = [
        "# AgentVerse Research Report",
        "",
        "## Research Overview",
        "",
        f"**Research Question:** {question}",
        (
            f"**Generated At:** "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ),
        f"**Total Sources:** {total_sources}",
        f"**Valid URLs:** {valid_urls}",
        f"**Good Quality Sources:** {good_sources}",
        "",
        "## Research Findings Summary",
        "",
        findings_summary,
        "",
        "## Detailed Research Findings",
        "",
    ]

    # Add details for each source using the same numbering.
    if not checked_results:
        report_lines.append(
            "No research sources were available."
        )
    else:
        for index, item in enumerate(checked_results, start=1):
            report_lines.extend([
                f"### Source {index}: {item.get('title') or 'Untitled'}",
                "",
                f"- **Query:** {item.get('query', 'N/A')}",
                f"- **URL:** {item.get('url') or 'N/A'}",
                f"- **Valid URL:** {item.get('valid_url', False)}",
                f"- **Evidence Available:** {item.get('has_evidence', False)}",
                f"- **Verified:** {item.get('verified', False)}",
                (
                    f"- **Quality Status:** "
                    f"{item.get('quality_status', 'Not Available')}"
                ),
                "",
                item.get("snippet") or "No snippet available.",
                "",
            ])

    # Add source quality summary
    report_lines.extend([
        "## Source Quality Summary",
        "",
        f"- **Total Sources:** {total_sources}",
        f"- **Valid URLs:** {valid_urls}",
        f"- **Sources with Evidence:** {sources_with_evidence}",
        f"- **Good Sources:** {good_sources}",
        f"- **Needs Review:** {needs_review}",
        f"- **Poor Sources:** {poor_sources}",
        "",
        (
            "**Note:** Quality status checks URL format and "
            "snippet availability only. It does not confirm "
            "the factual accuracy of a source."
        ),
        "",
    ])

    report = "\n".join(report_lines)

    return {"report": report}