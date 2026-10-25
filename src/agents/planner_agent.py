def planner_agent(state: dict) -> dict:
    """Break the user's research question into tasks."""
    question = state["question"]

    tasks = [
        f"Identify the main concepts in: {question}",
        f"Gather relevant information about: {question}",
        f"Review the findings and prepare a summary of: {question}",
    ]

    return {"tasks": tasks}