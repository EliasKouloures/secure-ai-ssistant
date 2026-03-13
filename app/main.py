from __future__ import annotations

import streamlit as st

from app.components import render_copy_button
from app.styles import load_styles
from core.config import load_config
from core.errors import AppError
from core.models import AnalysisPayload, ErrorCode, FileUpload
from core.storage import Repository
from services.case_service import CaseService

st.set_page_config(
    page_title="Sekretariat-Copilot",
    page_icon="SC",
    layout="wide",
    initial_sidebar_state="collapsed",
)


@st.cache_resource
def get_service() -> CaseService:
    config = load_config()
    repository = Repository(config.storage.database_path)
    return CaseService(config=config, repository=repository)


def main() -> None:
    service = get_service()
    config = service.config
    st.markdown(load_styles(), unsafe_allow_html=True)

    if "case_id" not in st.session_state:
        st.session_state.case_id = None
    if "analysis" not in st.session_state:
        st.session_state.analysis = None
    if "outputs" not in st.session_state:
        st.session_state.outputs = None
    if "error_message" not in st.session_state:
        st.session_state.error_message = None

    health = service.health_check()
    today_count = service.repository.count_cases_today()

    hero_left, hero_right = st.columns([3, 1])
    with hero_left:
        st.markdown('<div class="sc-hero">', unsafe_allow_html=True)
        st.markdown('<div class="sc-headline">Sekretariat-Copilot</div>', unsafe_allow_html=True)
        status_label = "Local backend ready" if health.reachable else "Backend offline"
        st.markdown(
            f'<div class="sc-status-pill">{status_label}</div>',
            unsafe_allow_html=True,
        )
        if health.warnings:
            for warning in health.warnings:
                st.markdown(f'<div class="sc-warning">{warning}</div>', unsafe_allow_html=True)
        st.markdown(
            '<p class="sc-muted">Privacy-first administrative support for school office workflows.</p>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    with hero_right:
        st.markdown(
            f"""
            <div class="sc-kpi">
              <div class="sc-panel-title">Cases processed today</div>
              <div class="sc-kpi-value">{today_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    left_col, right_col = st.columns(2, gap="large")
    with left_col:
        st.markdown('<div class="sc-panel">', unsafe_allow_html=True)
        st.markdown('<div class="sc-panel-title">Workflow and Inputs</div>', unsafe_allow_html=True)
        workflow = st.selectbox(
            "Workflow",
            options=["auto", "absence", "reply", "schedule", "triage"],
            format_func=lambda item: "Auto-detect"
            if item == "auto"
            else item.replace("_", " ").title(),
        )
        text_input = st.text_area(
            "Pasted text", height=180, placeholder="Paste a parent message, email, or note."
        )
        note_input = st.text_area(
            "Manual note", height=140, placeholder="Type a phone note or admin summary."
        )
        uploaded_files = st.file_uploader(
            "Upload supporting files",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )
        action_col, reset_col = st.columns([2, 1])
        with action_col:
            process = st.button("Process locally", type="primary", width="stretch")
        with reset_col:
            reset = st.button("Reset case", width="stretch")

        if reset and st.session_state.case_id:
            try:
                service.reset_case(st.session_state.case_id)
            except AppError:
                pass
            st.session_state.case_id = None
            st.session_state.analysis = None
            st.session_state.outputs = None
            st.session_state.error_message = None
            st.rerun()

        if process:
            st.session_state.error_message = None
            uploads = [
                FileUpload(name=item.name, content=item.getvalue(), content_type=item.type)
                for item in uploaded_files or []
            ]
            payload = AnalysisPayload(
                workflow_hint=None if workflow == "auto" else workflow,
                text_input=text_input,
                note_input=note_input,
                files=uploads,
                locale=config.locale,
            )
            try:
                with st.spinner("Processing locally..."):
                    analysis = service.analyse_case(payload)
                    outputs = service.generate_outputs(analysis.case.id)
                st.session_state.case_id = analysis.case.id
                st.session_state.analysis = analysis
                st.session_state.outputs = outputs
            except AppError as exc:
                st.session_state.analysis = None
                st.session_state.outputs = None
                if exc.code == ErrorCode.BACKEND_UNREACHABLE:
                    st.session_state.error_message = "The local model backend is unavailable. Start LM Studio or another compatible local server and try again."
                else:
                    st.session_state.error_message = exc.message

        if st.session_state.error_message:
            st.markdown(
                f'<div class="sc-error">{st.session_state.error_message}</div>',
                unsafe_allow_html=True,
            )
        elif st.session_state.analysis is None:
            st.markdown(
                '<p class="sc-muted">Choose a workflow or leave it on auto-detect, then add text, a note, or files.</p>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="sc-panel">', unsafe_allow_html=True)
        st.markdown('<div class="sc-panel-title">Outputs</div>', unsafe_allow_html=True)
        analysis = st.session_state.analysis
        outputs = st.session_state.outputs
        if analysis and outputs:
            if analysis.case.status.value == "blocked":
                st.markdown(
                    '<div class="sc-warning">Unsupported input. Review the guidance below and ask for a clearer single-child case.</div>',
                    unsafe_allow_html=True,
                )
            elif analysis.case.confidence and analysis.case.confidence.value == "low":
                st.markdown(
                    '<div class="sc-warning">Low confidence. Review carefully before using any output.</div>',
                    unsafe_allow_html=True,
                )

            for warning in analysis.warnings:
                st.markdown(f'<div class="sc-warning">{warning}</div>', unsafe_allow_html=True)

            st.subheader("Structured facts")
            edited_facts = st.text_area(
                "Structured facts",
                value="\n".join(
                    f"{key.replace('_', ' ').title()}: {value}"
                    for key, value in analysis.extracted_record.as_display_dict().items()
                ),
                height=220,
                label_visibility="collapsed",
            )
            render_copy_button("Copy structured facts", edited_facts)

            st.subheader("Internal case brief")
            brief_text = st.text_area(
                "Internal case brief",
                value=outputs.case_brief.summary,
                height=160,
                label_visibility="collapsed",
            )
            render_copy_button("Copy internal brief", brief_text)

            if outputs.reply_set:
                st.subheader("Subject lines")
                subjects_text = st.text_area(
                    "Subject lines",
                    value="\n".join(outputs.reply_set.subject_lines),
                    height=120,
                    label_visibility="collapsed",
                )
                render_copy_button("Copy subject lines", subjects_text)
                variants = [
                    ("Hemingway-style", outputs.reply_set.variant_hemingway),
                    ("Corporate", outputs.reply_set.variant_corporate),
                    ("Educator-first", outputs.reply_set.variant_educator),
                ]
                for label, value in variants:
                    st.subheader(label)
                    variant_text = st.text_area(
                        label, value=value, height=160, label_visibility="collapsed"
                    )
                    render_copy_button(f"Copy {label}", variant_text)

            if outputs.clarifying_questions:
                st.subheader("Clarifying questions")
                questions_text = st.text_area(
                    "Clarifying questions",
                    value="\n".join(
                        f"- {item.question_text}" for item in outputs.clarifying_questions
                    ),
                    height=120,
                    label_visibility="collapsed",
                )
                render_copy_button("Copy clarifying questions", questions_text)

            with st.expander("Exports", expanded=False):
                for export_format in ("text", "json", "csv"):
                    content, filename = service.export_case(analysis.case.id, export_format)
                    st.download_button(
                        label=f"Download {export_format.upper()}",
                        data=content,
                        file_name=filename,
                        width="stretch",
                    )
        else:
            st.markdown(
                '<p class="sc-muted">Processed results will appear here once the case is ready for review.</p>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    chart_col, list_col = st.columns(2, gap="large")
    with chart_col:
        st.markdown('<div class="sc-panel">', unsafe_allow_html=True)
        st.markdown(
            '<div class="sc-panel-title">Cases by Workflow (7 Days)</div>', unsafe_allow_html=True
        )
        chart_rows = [
            {"day": item.day.isoformat(), "workflow": item.task_type.value, "count": item.count}
            for item in service.repository.workflow_counts(7)
        ]
        if chart_rows:
            st.vega_lite_chart(
                {
                    "data": {"values": chart_rows},
                    "mark": {"type": "bar", "cornerRadiusTopLeft": 4, "cornerRadiusTopRight": 4},
                    "encoding": {
                        "x": {"field": "day", "type": "ordinal", "title": None},
                        "y": {"field": "count", "type": "quantitative", "title": None},
                        "color": {
                            "field": "workflow",
                            "type": "nominal",
                            "scale": {"range": ["#003399", "#2E8B57", "#708090", "#D4AF37"]},
                        },
                    },
                    "height": 280,
                },
                width="stretch",
            )
        else:
            st.markdown('<p class="sc-muted">No cases yet.</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with list_col:
        st.markdown('<div class="sc-panel">', unsafe_allow_html=True)
        st.markdown('<div class="sc-panel-title">Recent cases</div>', unsafe_allow_html=True)
        recent = service.repository.list_recent_cases(7)
        if recent:
            for item in recent:
                confidence = item.confidence.value if item.confidence else "pending"
                st.markdown(
                    f"**{item.id}**  \n"
                    f"{item.task_type.value.title()} | {confidence.title()} | {item.status.value.replace('_', ' ').title()}  \n"
                    f"<span class='sc-muted'>{item.created_at.strftime('%d %b %Y %H:%M UTC')}</span>",
                    unsafe_allow_html=True,
                )
                st.divider()
        else:
            st.markdown('<p class="sc-muted">No recent cases yet.</p>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Diagnostics", expanded=False):
        st.write(
            {
                "reachable": health.reachable,
                "backend_name": health.backend_name,
                "base_url": health.base_url,
                "model_id": health.model_id,
                "recent_errors": service.repository.recent_errors(),
            }
        )
        if config.features.show_privacy_panel:
            st.markdown(
                "Processing happens locally by default. The app binds to `127.0.0.1` unless you deliberately enable intranet mode, "
                "stores only minimal audit metadata, and does not log raw source content by default."
            )
        if config.bind_host != "127.0.0.1":
            st.markdown(
                '<div class="sc-warning">Intranet mode is enabled. Confirm that access is restricted to your trusted local network.</div>',
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
