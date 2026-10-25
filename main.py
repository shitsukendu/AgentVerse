from pathlib import Path
from datetime import datetime

from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from src.agents.planner_agent import planner_agent
from src.agents.research_agent import research_agent
from src.agents.fact_checker_agent import fact_checker_agent
from src.agents.report_writer_agent import report_writer_agent


class ResearchState(TypedDict, total=False):
    question: str
    tasks: list[str]
    research_results: list[dict]
    checked_results: list[dict]
    report: str
    agent_status: dict[str, str]


def build_workflow():
    """Build the AgentVerse LangGraph workflow."""

    graph = StateGraph(ResearchState)

    # Register agents
    graph.add_node("planner", planner_agent)
    graph.add_node("researcher", research_agent)
    graph.add_node("fact_checker", fact_checker_agent)
    graph.add_node("report_writer", report_writer_agent)

    # Define execution order
    graph.add_edge(START, "planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "fact_checker")
    graph.add_edge("fact_checker", "report_writer")
    graph.add_edge("report_writer", END)

    return graph.compile()


def run_research_workflow(question: str, progress_callback=None) -> dict:
    """Execute the AgentVerse research workflow."""

    workflow = build_workflow()

    result = {
        "question": question,
        "tasks": [],
        "research_results": [],
        "checked_results": [],
        "report": "",
        "agent_status": {
            "planner": "Pending",
            "researcher": "Pending",
            "fact_checker": "Pending",
            "report_writer": "Pending",
        },
    }

    try:
        for event in workflow.stream(
            {"question": question},
            stream_mode="updates",
        ):
            for node_name, node_output in event.items():
                if not isinstance(node_output, dict):
                    continue

                result.update(node_output)

                if node_name in result["agent_status"]:
                    result["agent_status"][node_name] = "Completed"

                print(f"\n[PROGRESS] {node_name} completed")

                if progress_callback:
                    try:
                        progress_callback(node_name)
                    except Exception as callback_error:
                        print(
                            f"[WARNING] Progress callback failed: "
                            f"{callback_error}"
                        )

    except Exception as workflow_error:
        print(
            f"\n[ERROR] Workflow failed: {workflow_error}"
        )

        result["error"] = str(workflow_error)
        result["success"] = False

        for agent_name, status in result["agent_status"].items():
            if status == "Pending":
                result["agent_status"][agent_name] = "Failed or Not Started"

        return result

    result["success"] = True

    print("\n" + "=" * 60)
    print("       AGENTVERSE LANGGRAPH WORKFLOW")
    print("=" * 60)

    # Planner Agent
    print("\n[1] Planner Agent")

    for task in result.get("tasks", []):
        print("-", task)

    # Research Agent
    print("\n[2] Research Agent")

    for research in result.get("research_results", []):
        print("\nQuery:", research.get("query", ""))

        for source in research.get("sources", []):
            print("Title:", source.get("title", ""))
            print("URL:", source.get("url", ""))
            

    # Fact Checker Agent
    print("\n[3] Fact Checker Agent")

    for item in result.get("checked_results", []):
        print("\nTitle:", item.get("title", ""))
        print("URL:", item.get("url", ""))
        print("Valid URL:", item.get("valid_url", False))
        print("Has evidence:", item.get("has_evidence", False))
        print("Verified:", item.get("verified", False))

    # Report Writer Agent
    print("\n[4] Report Writer Agent")
    print("\n" + "=" * 60)

    report = result.get("report", "")

    if report:
        print(report)

        # Create outputs folder if it does not exist
        output_dir = Path("outputs")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save report as a Markdown file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = output_dir / f"research_report_{timestamp}.md"

        report_path.write_text(report, encoding="utf-8")

        print(f"\nReport saved successfully: {report_path}")
    else:
        print("No report generated.")

    if report:
        print(report)
    else:
        print("No report generated.")
        print(
            "Check report_writer_agent.py and the workflow state."
        )

    print("=" * 60)
    print("\nWorkflow completed successfully.")

    return result


if __name__ == "__main__":
    question = input(
        "\nEnter your research question: "
    ).strip()

    if question:
        run_research_workflow(question)
    else:
        print("Please enter a research question.")