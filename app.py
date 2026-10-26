import re
import uuid
from datetime import datetime

from database import (save_research, get_all_research, get_collections, update_research_collection)

import streamlit as st

from io import BytesIO
from reportlab.lib.pagesizes import A4

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from xml.sax.saxutils import escape


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="AgentVerse | AI Research Intelligence",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# SESSION STATE
# ==================================================

if "research_history" not in st.session_state:
    st.session_state.research_history = get_all_research()

if "active_report_id" not in st.session_state:
    st.session_state.active_report_id = None

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

if "page" not in st.session_state:
    st.session_state.page = "dashboard"


# ==================================================
# PREMIUM THEME-AWARE CSS
# ==================================================

st.markdown(
    """
    <style>
    :root {
        --av-blue: #4285F4;
        --av-violet: #8B5CF6;
        --av-cyan: #06B6D4;
    }

    /* Main page spacing */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 3rem;
        max-width: 1500px;
    }

    /* Reduce the top header space */
    [data-testid="stHeader"] {
        height: 2.5rem;
        background: transparent;
    }

    /* Keep the toolbar compact */
    [data-testid="stToolbar"] {
        top: 0.25rem;
        right: 0.5rem;
    }

    /* Hero section spacing */
    .av-hero {
        margin-top: 0rem;
        padding: 28px 30px;
        border-radius: 22px;
        margin-bottom: 22px;
        background: linear-gradient(
            125deg,
            #0891B2 0%,
            #2563EB 48%,
            #7653B9 100%
        );
        color: #FFFFFF;
        box-shadow: 0 12px 35px rgba(55, 80, 160, 0.20);
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid var(--st-border-color);
    }

    .av-hero {
        padding: 28px 30px;
        border-radius: 22px;
        margin-bottom: 22px;
        background: linear-gradient(
            125deg,
            #173B73 0%,
            #4059AD 48%,
            #7653B9 100%
        );
        color: #FFFFFF;
        box-shadow: 0 12px 35px rgba(55, 80, 160, 0.20);
    }

    .av-hero h1 {
        color: #FFFFFF !important;
        font-size: clamp(2rem, 4vw, 3rem);
        font-weight: 800;
        letter-spacing: -1.2px;
        margin: 0 0 8px 0;
    }

    .av-hero p {
        color: #F2F5FF !important;
        font-size: 1rem;
        line-height: 1.7;
        margin: 0;
    }

    .av-chip {
        display: inline-block;
        padding: 5px 11px;
        margin-bottom: 13px;
        border: 1px solid rgba(255,255,255,0.4);
        border-radius: 100px;
        background: rgba(255,255,255,0.12);
        color: #FFFFFF !important;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.4px;
    }

    .av-card {
        padding: 19px;
        border: 1px solid var(--st-border-color);
        border-radius: 16px;
        background: var(--st-secondary-background-color);
        min-height: 135px;
        margin-bottom: 12px;
    }

    .av-card-icon {
        font-size: 1.55rem;
        margin-bottom: 8px;
    }

    .av-card h3 {
        color: var(--st-text-color) !important;
        font-size: 1.05rem;
        margin: 0 0 7px 0;
    }

    .av-card p {
        color: var(--st-text-color) !important;
        opacity: 0.82;
        font-size: 0.9rem;
        line-height: 1.65;
        margin: 0;
    }

    .av-section-title {
        font-size: 1.3rem;
        font-weight: 750;
        color: var(--st-text-color);
        margin-bottom: 4px;
    }

    .av-muted {
        color: var(--st-text-color);
        opacity: 0.78;
        line-height: 1.7;
    }

    /* Common button styling */
    div.stButton > button,
    div.stDownloadButton > button,
    div.stFormSubmitButton > button {
        border-radius: 10px !important;
        font-weight: 650 !important;
        min-height: 2.7rem;
        transition: all 0.2s ease;
    }

    /* Cyan: New Research and other primary buttons */
    .stButton button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background: #0891B2 !important;
        background-color: #0891B2 !important;
        border: 1px solid #0891B2 !important;
        color: #FFFFFF !important;
    }

    /* Cyan: Initiate Research form submit button */
    [data-testid="stFormSubmitButton"] button,
    .stFormSubmitButton button {
        background: #0891B2 !important;
        background-color: #0891B2 !important;
        border: 1px solid #0891B2 !important;
        color: #FFFFFF !important;
    }

    /* Hover effects */
    .stButton button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover,
    [data-testid="stFormSubmitButton"] button:hover,
    .stFormSubmitButton button:hover {
        background: #0E7490 !important;
        background-color: #0E7490 !important;
        border-color: #0E7490 !important;
        color: #FFFFFF !important;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 12px;
        line-height: 1.7;
    }

    div[data-testid="stMetric"] {
        padding: 16px;
        border: 1px solid var(--st-border-color);
        border-radius: 14px;
        background: var(--st-secondary-background-color);
    }

    div[data-testid="stExpander"] {
        border-radius: 12px;
    }

    .stMarkdown,
    .stMarkdown p,
    .stMarkdown li {
        line-height: 1.75;
    }

    a {
        overflow-wrap: anywhere;
    }

    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .av-hero {
            padding: 21px;
            border-radius: 16px;
        }

        .av-card {
            padding: 14px;
        }
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)

DEFAULT_COLLECTIONS = [
    "General",
    "AI & Machine Learning",
    "Scientific Research",
    "Technology",
]


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def extract_section(report: str, heading: str) -> str:
    pattern = (
        rf"^##\s+{re.escape(heading)}\s*\n"
        rf"(.*?)(?=^##\s+|\Z)"
    )

    match = re.search(
        pattern,
        report,
        flags=re.MULTILINE | re.DOTALL,
    )

    return match.group(1).strip() if match else ""


def extract_sources(report: str) -> list[dict]:
    pattern = (
        r"^### Source (\d+):\s*(.*?)\n"
        r"(.*?)(?=^### Source \d+:|^## |\Z)"
    )

    sources = []

    for match in re.finditer(
        pattern,
        report,
        flags=re.MULTILINE | re.DOTALL,
    ):
        number, title, body = match.groups()

        url_match = re.search(
            r"^- \*\*URL:\*\*\s*(\S+)",
            body,
            flags=re.MULTILINE,
        )

        query_match = re.search(
            r"^- \*\*Query:\*\*\s*(.+)$",
            body,
            flags=re.MULTILINE,
        )

        snippet_parts = re.split(r"\n\n", body, maxsplit=1)

        sources.append({
            "number": number,
            "title": title.strip(),
            "url": url_match.group(1) if url_match else "",
            "query": (
                query_match.group(1).strip()
                if query_match else ""
            ),
            "details": (
                snippet_parts[1].strip()
                if len(snippet_parts) > 1 else ""
            ),
        })

    return sources


def get_active_report():
    active_id = st.session_state.active_report_id

    for item in st.session_state.research_history:
        if item["id"] == active_id:
            return item

    return None


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.markdown("## 🔬 AgentVerse")
    st.caption("RESEARCH INTELLIGENCE PLATFORM")
    st.divider()

    if st.button(
        "＋  New Research",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.page = "dashboard"
        st.session_state.active_report_id = None
        st.session_state.question_input = ""
        st.rerun()

    if st.button(
        "⚖️ Research Comparison",
        use_container_width=True,
    ):
        st.session_state.page = "comparison"
        st.rerun()

    # Collection Filter
    collection_filter = st.selectbox(
        "Filter by Collection",
        options=["All Collections"] + sorted(
            set(DEFAULT_COLLECTIONS + get_collections())
        ),
        key="history_collection_filter",
    )

    st.markdown("### 🕘 Research History")

    # Filter history according to selected collection
    filtered_history = [
        item
        for item in st.session_state.research_history
        if (
            collection_filter == "All Collections"
            or item.get("collection", "General") == collection_filter
        )
    ]

    if not filtered_history:
        st.caption("No research reports in this collection.")
    else:
        for item in reversed(filtered_history):
            label = item["question"]

            if len(label) > 32:
                label = label[:32] + "…"

            active = (
                item["id"] == st.session_state.active_report_id
            )

            if st.button(
                ("🔹 " if active else "📄 ") + label,
                key=f"history_{item['id']}",
                use_container_width=True,
                type="primary" if active else "secondary",
                help=item["question"],
            ):
                st.session_state.active_report_id = item["id"]
                st.rerun()

    st.divider()

    st.markdown("**WORKFLOW PIPELINE**")
    st.caption("🧠 Planner Agent")
    st.caption("🔎 Research Agent")
    st.caption("🛡️ Fact Checker")
    st.caption("📝 Report Writer")

    st.divider()
    st.caption("Theme: use Streamlit Settings to switch modes.")
    st.caption("AgentVerse • Built with LangGraph + Streamlit")


# ==================================================
# HERO HEADER
# ==================================================

st.markdown(
    """
    <div class="av-hero">
        <div class="av-chip">✦ MULTI-AGENT AI RESEARCH</div>
        <h1>AgentVerse</h1>
        <p>
            From research questions to evidence-backed reports.
            Explore ideas with an autonomous multi-agent workflow.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# RESEARCH COMPARISON PAGE
# ==================================================

if st.session_state.get("page") == "comparison":

    st.markdown("## ⚖️ Research Comparison")
    st.caption(
        "Compare two saved research reports side by side."
    )

    reports = get_all_research()

    if len(reports) < 2:
        st.info(
            "At least two saved research reports are required "
            "to use Research Comparison."
        )

    else:
        report_options = {
            f"{item['question'][:70]} — {item['id'][:8]}": item
            for item in reports
        }

        selected_labels = list(report_options.keys())

        col1, col2 = st.columns(2)

        with col1:
            first_label = st.selectbox(
                "Select First Report",
                selected_labels,
                index=0,
                key="comparison_report_1",
            )

        with col2:
            second_label = st.selectbox(
                "Select Second Report",
                selected_labels,
                index=1,
                key="comparison_report_2",
            )

        if first_label == second_label:
            st.warning("Please select two different reports.")

        else:
            first_report = report_options[first_label]
            second_report = report_options[second_label]

            # Comparison Metrics
            import re
            from urllib.parse import urlparse

            def extract_source_urls(report_text):
                """Extract unique HTTP/HTTPS URLs from a report."""
                urls = re.findall(
                    r'https?://[^\s<>"\'`]+',
                    str(report_text),
                    flags=re.IGNORECASE,
                )

                cleaned_urls = set()

                for url in urls:
                    url = url.rstrip(".,;:!?)]}")

                    if url.startswith(("http://", "https://")):
                        cleaned_urls.add(url)

                return cleaned_urls

            first_urls = extract_source_urls(first_report["report"])
            second_urls = extract_source_urls(second_report["report"])

            common_urls = first_urls & second_urls
            first_only_urls = first_urls - second_urls
            second_only_urls = second_urls - first_urls

            st.markdown("### 📊 Comparison Metrics")
            metric_col1, metric_col2 = st.columns(2)

            with metric_col1:
                st.markdown("**Report 1**")
                st.metric(
                    "Report Length",
                    f"{len(first_report.get('report', '')):,} characters",
                )

            with metric_col2:
                st.markdown("**Report 2**")
                st.metric(
                    "Report Length",
                    f"{len(second_report.get('report', '')):,} characters",
                )

            st.markdown("### 🔗 Source Comparison")
            source_col1, source_col2, source_col3 = st.columns(3)
            source_col1.metric("Report 1 Sources", len(first_urls))
            source_col2.metric("Report 2 Sources", len(second_urls))
            source_col3.metric("Common URLs", len(common_urls))

            with st.expander(f"🔁 Common Sources ({len(common_urls)})"):
                if common_urls:
                    for url in sorted(common_urls):
                        st.markdown(f"- [{url}]({url})")
                else:
                    st.info("No identical URLs found in both reports.")

            with st.expander(f"📘 Only in Report 1 ({len(first_only_urls)})"):
                if first_only_urls:
                    for url in sorted(first_only_urls):
                        st.markdown(f"- [{url}]({url})")
                else:
                    st.caption("No unique URLs found in Report 1.")

            with st.expander(f"📗 Only in Report 2 ({len(second_only_urls)})"):
                if second_only_urls:
                    for url in sorted(second_only_urls):
                        st.markdown(f"- [{url}]({url})")
                else:
                    st.caption("No unique URLs found in Report 2.")

            # Create PDF
            pdf_buffer = BytesIO()
            pdf_doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                rightMargin=0.65 * inch,
                leftMargin=0.65 * inch,
                topMargin=0.65 * inch,
                bottomMargin=0.65 * inch,
            )

            pdf_styles = getSampleStyleSheet()
            story = []

            from reportlab.lib.enums import TA_LEFT

            pdf_styles.add(ParagraphStyle(
                name="ReportBody",
                parent=pdf_styles["BodyText"],
                fontSize=9,
                leading=13,
                spaceAfter=6,
                alignment=TA_LEFT,
                wordWrap="CJK",
            ))

            pdf_styles.add(ParagraphStyle(
                name="ReportHeading",
                parent=pdf_styles["Heading2"],
                fontSize=13,
                leading=17,
                spaceBefore=10,
                spaceAfter=7,
            ))

            def clean_markdown_line(line):
                line = line.strip()

                # Remove Markdown heading markers
                line = re.sub(r"^#{1,6}\s*", "", line)

                # Convert bold and italic Markdown to ReportLab tags
                line = re.sub(
                    r"\*\*(.+?)\*\*",
                    r"<b>\1</b>",
                    line,
                )
                line = re.sub(
                    r"(?<!\*)\*([^*]+)\*(?!\*)",
                    r"<i>\1</i>",
                    line,
                )

                # Remove Markdown bullet markers
                line = re.sub(r"^\s*[-*+]\s+", "• ", line)

                return line

            story.append(Paragraph(
                "Research Comparison Report",
                pdf_styles["Title"],
            ))
            story.append(Spacer(1, 12))

            def add_report_to_pdf(report_number, report_item):
                story.append(Paragraph(
                    f"Report {report_number}",
                    pdf_styles["Heading1"],
                ))
                story.append(Paragraph(
                    f"Question: {escape(str(report_item['question']))}",
                    pdf_styles["Heading2"],
                ))
                story.append(Spacer(1, 8))

                for line in str(report_item.get("report", "")).splitlines():
                    cleaned_line = clean_markdown_line(line)

                    if not cleaned_line:
                        story.append(Spacer(1, 5))
                        continue

                    # Escape HTML while preserving safe bold/italic tags
                    parts = re.split(r"(<b>.*?</b>|<i>.*?</i>)", cleaned_line)
                    formatted_parts = []

                    for part in parts:
                        if part.startswith("<b>") and part.endswith("</b>"):
                            formatted_parts.append(
                                "<b>" + escape(part[3:-4]) + "</b>"
                            )
                        elif part.startswith("<i>") and part.endswith("</i>"):
                            formatted_parts.append(
                                "<i>" + escape(part[3:-4]) + "</i>"
                            )
                        else:
                            formatted_parts.append(escape(part))

                    formatted_line = "".join(formatted_parts)
                    is_heading = line.lstrip().startswith("#")

                    style = (
                        pdf_styles["ReportHeading"]
                        if is_heading
                        else pdf_styles["ReportBody"]
                    )

                    story.append(Paragraph(formatted_line or " ", style))

            add_report_to_pdf(1, first_report)
            story.append(PageBreak())
            add_report_to_pdf(2, second_report)

            story.append(PageBreak())
            story.append(Paragraph(
                "Source Comparison",
                pdf_styles["Heading1"],
            ))

            story.append(Paragraph(
                f"Report 1 sources: {len(first_urls)}",
                pdf_styles["BodyText"],
            ))
            story.append(Paragraph(
                f"Report 2 sources: {len(second_urls)}",
                pdf_styles["BodyText"],
            ))
            story.append(Paragraph(
                f"Common sources: {len(common_urls)}",
                pdf_styles["BodyText"],
            ))

            def add_url_section(title, urls):
                story.append(Spacer(1, 10))
                story.append(Paragraph(
                    escape(title),
                    pdf_styles["Heading2"],
                ))

                if urls:
                    for url in sorted(urls):
                        safe_url = escape(url)
                        story.append(Paragraph(
                            f'<link href="{safe_url}" color="blue">{safe_url}</link>',
                            pdf_styles["BodyText"],
                        ))
                        story.append(Spacer(1, 4))
                else:
                    story.append(Paragraph(
                        "None found.",
                        pdf_styles["BodyText"],
                    ))

            add_url_section("Common Sources", common_urls)
            add_url_section("Only in Report 1", first_only_urls)
            add_url_section("Only in Report 2", second_only_urls)

            def add_page_number(canvas, doc):
                canvas.saveState()
                canvas.setFont("Helvetica", 9)
                canvas.setFillColor(colors.grey)
                canvas.drawCentredString(
                    A4[0] / 2,
                    0.35 * inch,
                    f"Page {doc.page}",
                )
                canvas.restoreState()

            pdf_doc.build(
                story,
                onFirstPage=add_page_number,
                onLaterPages=add_page_number,
            )
            pdf_bytes = pdf_buffer.getvalue()
            pdf_buffer.close()

            st.download_button(
                label="Download Comparison Report (PDF)",
                data=pdf_bytes,
                file_name="research_comparison_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.stop()


# ==================================================
# ACTIVE REPORT
# ==================================================

selected_report = get_active_report()


# ==================================================
# HOME / RESEARCH WORKSPACE
# ==================================================

if selected_report is None:

    st.markdown(
        '<div class="av-section-title">Research Workspace</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="av-muted">'
        'Enter a question to start a new research workflow.'
        '</p>',
        unsafe_allow_html=True,
    )

    with st.form("research_form"):
        question = st.text_area(
            "Research Question",
            key="question_input",
            placeholder=(
                "Example: How can multi-agent AI systems "
                "improve scientific research?"
            ),
            height=125,
        )

        collection_options = sorted(
            set(DEFAULT_COLLECTIONS + get_collections())
        )

        selected_collection = st.selectbox(
            "Research Collection",
            options=collection_options,
            index=0,
        )

        submitted = st.form_submit_button(
            "Initiate Research",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        cleaned_question = question.strip()

        if not cleaned_question:
            st.warning("Please enter a research question.")
        else:
            try:
                with st.spinner(
                    "Agents are planning, researching, "
                    "checking evidence and writing your report..."
                ):
                    from main import run_research_workflow

                    progress_placeholder = st.empty()

                    def show_progress(node_name):
                        agent_names = {
                            "planner": "Planner Agent",
                            "researcher": "Research Agent",
                            "fact_checker": "Fact Checker Agent",
                            "report_writer": "Report Writer Agent",
                        }

                        agent_name = agent_names.get(node_name, node_name)

                        progress_placeholder.info(
                            f"🔄 Completed: {agent_name}"
                        )

                    result = run_research_workflow(
                        cleaned_question,
                        progress_callback=show_progress,
                    )

                    if not isinstance(result, dict):
                        progress_placeholder.empty()
                        st.error("Unexpected workflow response.")
                        st.stop()

                    if not result.get("success", True):
                        progress_placeholder.empty()

                        error_message = result.get(
                            "error",
                            "An unknown workflow error occurred.",
                        )

                        st.error(
                            f"❌ Research workflow failed: {error_message}"
                        )

                        st.info(
                            "Please check the Terminal logs and try again."
                        )
                        st.stop()

                    progress_placeholder.success(
                        "✅ All agents completed successfully!"
                    )

                    if not isinstance(result, dict):
                        st.error("Unexpected workflow response.")
                        st.stop()

                    report = result.get("report", "")

                    if not isinstance(report, str) or not report.strip():
                        st.error(
                            "No report was generated. "
                            "Check the Terminal for details."
                        )
                        st.stop()

                    history_item = {
                        "id": str(uuid.uuid4()),
                        "question": cleaned_question,
                        "created_at": datetime.now().strftime(
                            "%d %b %Y, %I:%M %p"
                        ),
                        "report": report,
                        "collection": selected_collection,
                        "agent_status": result.get("agent_status", {}),
                    }

                    save_research(
                        report_id=history_item["id"],
                        question=history_item["question"],
                        report=history_item["report"],
                        collection=history_item["collection"],
                        agent_status=result.get("agent_status", {}),
                    )

                    # Refresh history from the database
                    st.session_state.research_history = get_all_research()

                    st.session_state.active_report_id = history_item["id"]

                st.rerun()

            except Exception as exc:
                st.error("The research workflow failed.")
                st.caption(
                    "Check your API configuration and Terminal output."
                )
                st.code(str(exc))

    st.write("")
    st.markdown("### ✨ Platform Capabilities")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="av-card">
                <div class="av-card-icon">🧠</div>
                <h3>Intelligent Planning</h3>
                <p>
                    Break a broad research question into
                    manageable research tasks.
                </p>
            </div>
            <div class="av-card">
                <div class="av-card-icon">🛡️</div>
                <h3>Source Quality Checks</h3>
                <p>
                    Inspect URLs and evidence availability
                    before building the report.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="av-card">
                <div class="av-card-icon">🔎</div>
                <h3>Web Research</h3>
                <p>
                    Collect useful source snippets from
                    web search results.
                </p>
            </div>
            <div class="av-card">
                <div class="av-card-icon">📊</div>
                <h3>Structured Reports</h3>
                <p>
                    Generate a research summary with
                    numbered source references.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "Source quality checks do not guarantee factual accuracy. "
        "Verify important claims independently."
    )


# ==================================================
# RESULTS DASHBOARD
# ==================================================

else:
    report = selected_report["report"]
    question = selected_report["question"]

    # Change Collection of Existing Report
    st.markdown("### 📁 Research Collection")

    current_collection = selected_report.get(
        "collection", "General"
    )

    collection_options = sorted(
        set(DEFAULT_COLLECTIONS + get_collections())
    )

    current_index = (
        collection_options.index(current_collection)
        if current_collection in collection_options
        else 0
    )

    new_collection = st.selectbox(
        "Move this report to",
        options=collection_options,
        index=current_index,
        key=f"report_collection_{selected_report['id']}",
    )

    if st.button(
        "💾 Save Collection",
        key=f"save_collection_{selected_report['id']}",
    ):
        updated = update_research_collection(
            selected_report["id"],
            new_collection,
        )

        if updated:
            st.session_state.research_history = get_all_research()
            st.success("Collection updated successfully!")
            st.rerun()
        else:
            st.error("Could not update the collection.")

    st.markdown("### 📊 Research Dashboard")

    # Agent Execution Status
    st.markdown("### 🤖 Agent Execution Status")

    agent_status = selected_report.get("agent_status", {})

    agent_names = {
        "planner": "🧠 Planner Agent",
        "researcher": "🔎 Research Agent",
        "fact_checker": "🛡️ Fact Checker",
        "report_writer": "📝 Report Writer",
    }

    status_columns = st.columns(4)

    completed_agents = 0
    total_agents = len(agent_names)

    for column, (agent_key, agent_label) in zip(
        status_columns, agent_names.items()
    ):
        with column:
            status = agent_status.get(
                agent_key, "Not Recorded"
            )

            st.markdown(f"**{agent_label}**")

            if status == "Completed":
                completed_agents += 1
                st.success("Completed")
            else:
                st.warning(status)

    completion_rate = (
        completed_agents / total_agents * 100
        if total_agents
        else 0
    )

    st.divider()

    st.markdown("### 📊 Agent Performance Analytics")

    performance_col1, performance_col2 = st.columns(2)

    with performance_col1:
        st.metric(
            "Agents Completed",
            f"{completed_agents}/{total_agents}",
        )

    with performance_col2:
        st.metric(
            "Completion Rate",
            f"{completion_rate:.0f}%",
        )

    st.progress(completion_rate / 100)

    if completed_agents == total_agents:
        st.success(
            "All agents completed their tasks successfully."
        )
    else:
        st.info(
            "Some agent statuses are pending or not recorded."
        )

    st.markdown(f"**Research Question:** {question}")
    st.caption(f"Created: {selected_report['created_at']}")

    summary = extract_section(
        report,
        "Research Findings Summary",
    )

    sources = extract_sources(report)

    quality_summary = extract_section(
        report,
        "Source Quality Summary",
    )

    total_match = re.search(
        r"\*\*Total Sources:\*\*\s*(\d+)",
        report,
    )
    valid_match = re.search(
        r"\*\*Valid URLs:\*\*\s*(\d+)",
        report,
    )
    good_match = re.search(
        r"\*\*Good Sources:\*\*\s*(\d+)",
        quality_summary,
    )

    total_sources = (
        int(total_match.group(1))
        if total_match else len(sources)
    )

    valid_urls = (
        int(valid_match.group(1))
        if valid_match else 0
    )

    good_sources = (
        int(good_match.group(1))
        if good_match else 0
    )

    metric1, metric2, metric3 = st.columns(3)

    metric1.metric("Sources Collected", total_sources)
    metric2.metric("Valid URLs", valid_urls)
    metric3.metric("Good Quality", good_sources)

    st.divider()

    st.markdown("### 📈 Research Analytics")

    analytics_col1, analytics_col2 = st.columns(2)

    with analytics_col1:
        st.markdown("**Source Quality Overview**")

        st.bar_chart(
            {
                "Count": {
                    "Total Sources": total_sources,
                    "Valid URLs": valid_urls,
                    "Good Quality": good_sources,
                }
            }
        )

    with analytics_col2:
        st.markdown("**Research Statistics**")

        st.metric(
            "Invalid or Unverified URLs",
            max(total_sources - valid_urls, 0),
        )

        st.metric(
            "Sources Needing Review",
            max(total_sources - good_sources, 0),
        )

    st.divider()

    st.markdown("### ✨ AI-Generated Summary")

    if summary:
        st.markdown(summary)
    else:
        st.warning("No separate summary section was detected.")

    st.divider()

    st.markdown("### 🔗 Research Sources")

    if sources:
        for source in sources:
            with st.expander(
                f"Source {source['number']}: {source['title']}"
            ):
                if source["query"]:
                    st.caption(f"Research query: {source['query']}")

                if source["url"]:
                    st.markdown(f"[Open source]({source['url']})")

                if source["details"]:
                    st.write(source["details"])
    else:
        st.caption("No structured source entries were detected.")

    with st.expander("📚 Full Research Report"):
        st.markdown(report)


    pdf_buffer = BytesIO()

    def draw_pdf_header_footer(canvas, doc):
        canvas.saveState()

        page_width, page_height = A4

        # Header
        canvas.setFillColor(colors.HexColor("#163A5F"))
        canvas.rect(
            0,
            page_height - 0.48 * inch,
            page_width,
            0.48 * inch,
            fill=1,
            stroke=0,
        )

        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawString(
            0.65 * inch,
            page_height - 0.30 * inch,
            "AGENTVERSE",
        )

        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(
            page_width - 0.65 * inch,
            page_height - 0.30 * inch,
            "RESEARCH & INTELLIGENCE",
        )

        # Footer divider
        canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
        canvas.setLineWidth(0.6)
        canvas.line(
            0.65 * inch,
            0.52 * inch,
            page_width - 0.65 * inch,
            0.52 * inch,
        )

        # Footer text
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.setFont("Helvetica", 8)
        canvas.drawString(
            0.65 * inch,
            0.32 * inch,
            "AgentVerse | Research Intelligence Report",
        )

        canvas.drawRightString(
            page_width - 0.65 * inch,
            0.32 * inch,
            f"Page {doc.page}",
        )

        canvas.restoreState()

    pdf_doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.75 * inch,
        title="AgentVerse Research Intelligence Report",
        author="AgentVerse",
        subject="Autonomous Multi-Agent Research Report",
    )

    pdf_styles = getSampleStyleSheet()

    pdf_styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=pdf_styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=28,
            textColor=colors.HexColor("#163A5F"),
            alignment=TA_CENTER,
            spaceAfter=12,
        )
    )

    pdf_styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=pdf_styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#64748B"),
            alignment=TA_CENTER,
            spaceAfter=18,
        )
    )

    pdf_styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=pdf_styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=19,
            textColor=colors.HexColor("#163A5F"),
            spaceBefore=14,
            spaceAfter=7,
            keepWithNext=True,
        )
    )

    pdf_story = []

    pdf_story.append(Spacer(1, 18))

    pdf_story.append(
        Paragraph(
            "AGENTVERSE",
            pdf_styles["ReportTitle"],
        )
    )

    pdf_story.append(
        Paragraph(
            "Autonomous Multi-Agent Research &amp; Intelligence Platform",
            pdf_styles["ReportSubtitle"],
        )
    )

    pdf_story.append(
        Paragraph(
            "RESEARCH INTELLIGENCE REPORT",
            pdf_styles["ReportSubtitle"],
        )
    )

    pdf_story.append(Spacer(1, 12))

    pdf_story.append(
        Paragraph(
            f"<b>Research Question:</b> {escape(str(question))}",
            pdf_styles["Normal"],
        )
    )

    pdf_story.append(Spacer(1, 8))

    pdf_story.append(
        Paragraph(
            f"<b>Generated Date:</b> {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            pdf_styles["Normal"],
        )
    )

    pdf_story.append(Spacer(1, 18))

    for line in report.splitlines():
        line = line.strip()

        if not line:
            pdf_story.append(Spacer(1, 6))
            continue

        # Remove Markdown heading markers
        if line.startswith("# "):
            heading = escape(line[2:].strip())
            pdf_story.append(
                Paragraph(heading, pdf_styles["SectionHeading"])
            )
            pdf_story.append(Spacer(1, 4))
            continue

        elif line.startswith(("## ", "### ")):
            heading = escape(line.lstrip("#").strip())
            pdf_story.append(
                Paragraph(heading, pdf_styles["SectionHeading"])
            )
            continue

        # Handle every line, including bullets, with Markdown formatting
        is_bullet = line.startswith(("- ", "* "))

        if is_bullet:
            line = line[2:].strip()

        safe_line = escape(line)

        # Convert Markdown bold to PDF bold
        safe_line = re.sub(
            r"\*\*(.+?)\*\*",
            r"<b>\1</b>",
            safe_line,
        )

        # Convert Markdown italic to PDF italic
        safe_line = re.sub(
            r"(?<!\*)\*([^*]+)\*(?!\*)",
            r"<i>\1</i>",
            safe_line,
        )

        # Style URL lines in blue
        if "https://" in safe_line or "http://" in safe_line:
            safe_line = re.sub(
                r"(https?://[^\s&lt;]+)",
                r'<font color="#2563EB">\1</font>',
                safe_line,
            )

        if is_bullet:
            safe_line = f"&bull; {safe_line}"

        pdf_story.append(
            Paragraph(safe_line, pdf_styles["Normal"])
        )

    pdf_doc.build(
        pdf_story,
        onFirstPage=draw_pdf_header_footer,
        onLaterPages=draw_pdf_header_footer,
    )
    pdf_data = pdf_buffer.getvalue()

    download1, download2, download3 = st.columns(3)

    with download1:
        st.download_button(
            "Download Markdown",
            data=report,
            file_name="agentverse_research_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with download2:
        st.download_button(
            "Download TXT",
            data=report,
            file_name="agentverse_research_report.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with download3:
        st.download_button(
            "Download PDF",
            data=pdf_data,
            file_name="agentverse_research_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.info(
        "Quality labels indicate basic URL and evidence checks, "
        "not independent verification of factual claims."
    )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "🔬 AgentVerse • Autonomous Multi-Agent Research Platform"
)
st.caption(
    "Powered by LangGraph, Python, Streamlit and Gemini. "
    "Research findings should be independently verified."
)