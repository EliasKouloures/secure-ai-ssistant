from __future__ import annotations

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from app.components import render_copy_button
from app.state import apply_reset, queue_reset
from app.styles import load_styles
from core.config import load_config
from core.errors import AppError
from core.models import AnalysisPayload, AnalysisResult, ErrorCode, FileUpload, GeneratedOutputs
from core.storage import Repository
from core.text import normalise_whitespace
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


def _initialise_state() -> None:
    defaults = {
        "case_id": None,
        "analysis": None,
        "outputs": None,
        "error_message": None,
        "pending_payload": None,
        "pending_analysis": None,
        "pending_case_id": None,
        "show_clarification_dialog": False,
        "clarification_answers_input": "",
        "clarification_error": None,
        "pasted_text_input": "",
        "manual_note_input": "",
        "file_uploader_nonce": 0,
        "reset_requested": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _build_payload(
    *,
    text_input: str,
    note_input: str,
    uploaded_files: list[UploadedFile] | None,
    locale: str,
) -> AnalysisPayload:
    uploads = [
        FileUpload(name=item.name, content=item.getvalue(), content_type=item.type)
        for item in uploaded_files or []
    ]
    return AnalysisPayload(
        text_input=text_input,
        note_input=note_input,
        files=uploads,
        locale=locale,
    )


def _needs_clarification(analysis: AnalysisResult) -> bool:
    if analysis.case.status.value == "blocked":
        return False
    return analysis.confidence_score < 90


def _clarification_questions(analysis: AnalysisResult) -> list[str]:
    questions: list[str] = []
    for question in analysis.clarifying_questions:
        if question and question not in questions:
            questions.append(question)

    if not questions and not analysis.extracted_record.student_name:
        questions.append("Please confirm the pupil's full name.")
    if not questions and analysis.case.task_type.value == "reply":
        questions.append("What exact reply or reaction should the school office send?")
    if not questions:
        questions.append("What is the sender's main intent in one short sentence?")
    if len(questions) < 5 and analysis.warnings:
        questions.append("Please confirm any missing context, dates, or response constraints.")
    if len(questions) < 5:
        questions.append("Should the school office reply, and if so what outcome should that reply aim for?")
    deduped: list[str] = []
    for question in questions:
        if question not in deduped:
            deduped.append(question)
    return deduped[:5]


def _clear_pending_review(service: CaseService, *, remove_pending_case: bool) -> None:
    pending_case_id = st.session_state.pending_case_id
    if remove_pending_case and pending_case_id:
        try:
            service.reset_case(pending_case_id)
        except AppError:
            pass
    st.session_state.pending_payload = None
    st.session_state.pending_analysis = None
    st.session_state.pending_case_id = None
    st.session_state.show_clarification_dialog = False
    st.session_state.clarification_answers_input = ""
    st.session_state.clarification_error = None


def _perform_reset(service: CaseService) -> None:
    if st.session_state.case_id:
        try:
            service.reset_case(st.session_state.case_id)
        except AppError:
            pass
    _clear_pending_review(service, remove_pending_case=True)
    apply_reset(st.session_state)


def _handle_app_error(exc: AppError) -> str:
    if exc.code == ErrorCode.BACKEND_UNREACHABLE:
        return (
            "The local model backend could not be reached. Please confirm that LM Studio is open, "
            "the local server is running, and the configured model is loaded."
        )
    if exc.code == ErrorCode.MODEL_TIMEOUT:
        return (
            "The local model is running, but this request took too long to finish. "
            "Please try again, shorten the request, or increase the backend timeout in `config.toml`."
        )
    return exc.message


def _store_completed_case(analysis: AnalysisResult, outputs: GeneratedOutputs) -> None:
    st.session_state.case_id = analysis.case.id
    st.session_state.analysis = analysis
    st.session_state.outputs = outputs
    st.session_state.error_message = None


def _analyse_and_maybe_generate(
    service: CaseService,
    payload: AnalysisPayload,
    *,
    allow_clarification: bool,
) -> None:
    with st.spinner("Processing locally..."):
        analysis = service.analyse_case(payload)
    if allow_clarification and _needs_clarification(analysis):
        st.session_state.case_id = None
        st.session_state.analysis = None
        st.session_state.outputs = None
        st.session_state.pending_payload = payload
        st.session_state.pending_analysis = analysis
        st.session_state.pending_case_id = analysis.case.id
        st.session_state.show_clarification_dialog = True
        return
    with st.spinner("Drafting responses locally..."):
        outputs = service.generate_outputs(analysis.case.id, operator_note=payload.note_input)
    _store_completed_case(analysis, outputs)


@st.dialog("Need a bit more clarity")
def render_clarification_dialog(service: CaseService) -> None:
    analysis = st.session_state.pending_analysis
    payload = st.session_state.pending_payload
    if analysis is None or payload is None:
        return

    st.markdown(
        """
        <div class="sc-dialog-card">
          <div class="sc-dialog-title">I want to make sure the draft is accurate before I continue.</div>
          <div class="sc-dialog-copy">Some parts of the message are still unclear, incomplete, or below the 90% confidence threshold. Please answer the questions below, or cancel and adjust the inputs.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    issues: list[str] = []
    if analysis.warnings:
        issues.extend(analysis.warnings)
    if analysis.missing_fields:
        issues.append(
            "Important details are still missing: "
            + ", ".join(field.replace("_", " ") for field in analysis.missing_fields)
            + "."
        )
    if issues:
        for issue in issues[:5]:
            st.markdown(f'<div class="sc-warning">{issue}</div>', unsafe_allow_html=True)

    st.markdown('<div class="sc-dialog-questions">Clarifying questions</div>', unsafe_allow_html=True)
    for index, question in enumerate(_clarification_questions(analysis), start=1):
        st.markdown(f"**{index}.** {question}")

    answers = st.text_area(
        "Clarifying answers",
        key="clarification_answers_input",
        height=150,
        placeholder="Type any missing names, dates, intent, response goals, or constraints here.",
    )

    if st.session_state.clarification_error:
        st.markdown(
            f'<div class="sc-error">{st.session_state.clarification_error}</div>',
            unsafe_allow_html=True,
        )

    cancel_col, submit_col = st.columns(2)
    with cancel_col:
        if st.button("Cancel process", width="stretch"):
            _clear_pending_review(service, remove_pending_case=True)
            st.session_state.error_message = "The process was cancelled. You can adjust the inputs and try again."
            st.rerun()
    with submit_col:
        if st.button("Submit answers", type="primary", width="stretch"):
            if not answers.strip():
                st.session_state.clarification_error = (
                    "Please add at least one clarification before submitting."
                )
                st.rerun()

            amended_note = normalise_whitespace(
                "\n\n".join(
                    filter(
                        None,
                        [
                            payload.note_input,
                            "Clarification answers:\n" + answers.strip(),
                        ],
                    )
                )
            )
            updated_payload = AnalysisPayload(
                text_input=payload.text_input,
                note_input=amended_note,
                files=payload.files,
                locale=payload.locale,
            )
            st.session_state.manual_note_input = amended_note
            _clear_pending_review(service, remove_pending_case=True)
            try:
                _analyse_and_maybe_generate(service, updated_payload, allow_clarification=True)
            except AppError as exc:
                st.session_state.error_message = _handle_app_error(exc)
            st.rerun()


def main() -> None:
    service = get_service()
    config = service.config
    st.markdown(load_styles(), unsafe_allow_html=True)
    _initialise_state()

    if st.session_state.reset_requested:
        _perform_reset(service)

    if st.session_state.show_clarification_dialog:
        render_clarification_dialog(service)

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
        st.markdown('<div class="sc-panel-title">Inputs</div>', unsafe_allow_html=True)
        text_input = st.text_area(
            "Paste the message you received into here",
            key="pasted_text_input",
            height=280,
            placeholder="Paste the message you received into here",
        )
        note_input = st.text_area(
            "Paste and/or write a reaction and/or response to above message",
            key="manual_note_input",
            height=140,
            placeholder="Paste and/or write a reaction and/or response to above message",
        )
        uploader_key = f"supporting_files_input_{st.session_state.file_uploader_nonce}"
        uploaded_files = st.file_uploader(
            "Upload additional context for your reaction and/or response to above message",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key=uploader_key,
        )
        action_col, reset_col = st.columns([2, 1])
        with action_col:
            process = st.button("Process locally", type="primary", width="stretch")
        with reset_col:
            reset = st.button("Reset case", width="stretch")

        if reset:
            queue_reset(st.session_state)
            st.rerun()

        if process:
            st.session_state.error_message = None
            payload = _build_payload(
                text_input=text_input,
                note_input=note_input,
                uploaded_files=uploaded_files,
                locale=config.locale,
            )
            try:
                _analyse_and_maybe_generate(service, payload, allow_clarification=True)
                if st.session_state.show_clarification_dialog:
                    st.rerun()
            except AppError as exc:
                st.session_state.analysis = None
                st.session_state.outputs = None
                st.session_state.error_message = _handle_app_error(exc)

        if st.session_state.error_message:
            st.markdown(
                f'<div class="sc-error">{st.session_state.error_message}</div>',
                unsafe_allow_html=True,
            )
        elif st.session_state.analysis is None and st.session_state.pending_analysis is None:
            st.markdown(
                '<p class="sc-muted">Paste the inbound message, add your intended reaction if needed, upload supporting context if useful, then process locally.</p>',
                unsafe_allow_html=True,
            )

    with right_col:
        st.markdown('<div class="sc-panel-title">Ready-to-use outputs</div>', unsafe_allow_html=True)
        analysis = st.session_state.analysis
        outputs = st.session_state.outputs
        if analysis and outputs:
            st.markdown(
                '<p class="sc-muted">Pick the version that fits best, edit if needed, and copy it into your school email or admin system.</p>',
                unsafe_allow_html=True,
            )
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
                st.subheader("Subject line options")
                subjects_text = st.text_area(
                    "Subject line options",
                    value=outputs.copy_blocks["Subject lines"],
                    height=120,
                    label_visibility="collapsed",
                )
                render_copy_button("Copy subject line options", subjects_text)
                variants = [
                    ("Hemingway response", outputs.reply_set.variant_hemingway),
                    ("Corporate response", outputs.reply_set.variant_corporate),
                    ("Empathic response", outputs.reply_set.variant_educator),
                ]
                for label, value in variants:
                    st.subheader(label)
                    variant_text = st.text_area(
                        label, value=value, height=160, label_visibility="collapsed"
                    )
                    render_copy_button(f"Copy {label.lower()}", variant_text)

            with st.expander("Download case files", expanded=False):
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
                '<p class="sc-muted">Your structured facts, internal brief, subject lines, and draft responses will appear here once the case is ready.</p>',
                unsafe_allow_html=True,
            )

    chart_col, list_col = st.columns(2, gap="large")
    with chart_col:
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

    with list_col:
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
