from __future__ import annotations

import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile

from app.components import render_copy_button
from app.styles import load_styles
from core.config import load_config
from core.errors import AppError
from core.models import AssistantRun, ErrorCode, FileUpload
from core.storage import Repository
from services.case_service import CaseService

APP_NAME = "Secure Secr-AI-tery"
APP_CLAIM = "Your Free, Private & Offline AI Assistant."
ADD_NEW_PROMPT = "Add new Prompt"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="SS",
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
        "context_input": "",
        "prompt_editor_input": "",
        "prompt_choice": ADD_NEW_PROMPT,
        "loaded_prompt_choice": None,
        "pending_prompt_choice": None,
        "output_text": "",
        "output_editor_input": "",
        "pending_output_sync": None,
        "flash_message": None,
        "error_message": None,
        "file_uploader_nonce": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _uploaded_file(item: UploadedFile | None) -> list[FileUpload]:
    if item is None:
        return []
    return [FileUpload(name=item.name, content=item.getvalue(), content_type=item.type)]


def _handle_error(exc: AppError) -> str:
    if exc.code == ErrorCode.EMPTY_INPUT:
        return "Add some context, information, 2do's, or an uploaded file before running the prompt."
    if exc.code == ErrorCode.INSUFFICIENT_CONTEXT:
        return "Select or write a prompt before you run it."
    if exc.code == ErrorCode.MODEL_TIMEOUT:
        return (
            "The local model is running, but this request took too long to finish. "
            "Try again, shorten the context, or use a shorter prompt."
        )
    if exc.code == ErrorCode.BACKEND_UNREACHABLE:
        return (
            "LM Studio could not be reached. Please confirm that the local server is running and "
            "that the configured model is loaded."
        )
    return exc.message


def _load_prompt_into_state(service: CaseService, title: str) -> None:
    prompt = service.get_prompt_template(title)
    if prompt is None:
        st.session_state.prompt_editor_input = ""
        st.session_state.loaded_prompt_choice = ADD_NEW_PROMPT
        return
    st.session_state.loaded_prompt_choice = prompt.title
    st.session_state.prompt_editor_input = prompt.body


def _load_history_into_state(service: CaseService, run: AssistantRun) -> None:
    st.session_state.context_input = run.context_text
    st.session_state.output_text = run.output_text
    st.session_state.output_editor_input = run.output_text
    st.session_state.error_message = None
    st.session_state.flash_message = f"Loaded: {run.title}"
    st.session_state.prompt_editor_input = run.prompt_body
    if service.get_prompt_template(run.prompt_title):
        st.session_state.prompt_choice = run.prompt_title
        st.session_state.loaded_prompt_choice = run.prompt_title
    else:
        st.session_state.prompt_choice = ADD_NEW_PROMPT
        st.session_state.loaded_prompt_choice = ADD_NEW_PROMPT


def _apply_pending_prompt_choice(prompt_options: list[str]) -> None:
    pending_choice = st.session_state.pending_prompt_choice
    if pending_choice and pending_choice in prompt_options:
        st.session_state.prompt_choice = pending_choice
        st.session_state.loaded_prompt_choice = None
    st.session_state.pending_prompt_choice = None
    if st.session_state.prompt_choice not in prompt_options:
        st.session_state.prompt_choice = ADD_NEW_PROMPT
        st.session_state.loaded_prompt_choice = None


def _apply_pending_output_sync() -> None:
    pending_output = st.session_state.pending_output_sync
    if pending_output is None:
        return
    st.session_state.output_editor_input = pending_output
    st.session_state.output_text = pending_output
    st.session_state.pending_output_sync = None


def _history_button_label(run: AssistantRun) -> str:
    return run.title[:42] + ("..." if len(run.title) > 42 else "")


def main() -> None:
    service = get_service()
    _initialise_state()

    prompt_templates = service.list_prompt_templates()
    prompt_options = [ADD_NEW_PROMPT, *[item.title for item in prompt_templates]]
    _apply_pending_prompt_choice(prompt_options)
    _apply_pending_output_sync()

    st.markdown(load_styles(), unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ssa-topbar">
          <div class="ssa-brand-line">
            <span class="ssa-brand">{APP_NAME}</span>
            <span class="ssa-claim">{APP_CLAIM}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_col, middle_col, right_col = st.columns([1.0, 3.15, 1.3], gap="large")

    with left_col:
        st.markdown('<div class="ssa-section-title">History</div>', unsafe_allow_html=True)
        with st.container(border=True, height=760):
            history_items = service.list_history(limit=18)
            if not history_items:
                st.markdown(
                    '<p class="ssa-muted">Past chats will appear here once you have run a prompt.</p>',
                    unsafe_allow_html=True,
                )
            else:
                for item in history_items:
                    if st.button(
                        _history_button_label(item),
                        key=f"history_{item.id}",
                        width="stretch",
                        help=item.preview,
                    ):
                        _load_history_into_state(service, item)
                        st.rerun()

    with middle_col:
        st.markdown('<div class="ssa-section-title">Context, Info & 2do\'s</div>', unsafe_allow_html=True)
        context_text = st.text_area(
            "Context, Info & 2do's",
            key="context_input",
            height=180,
            label_visibility="collapsed",
            placeholder="Type or paste the details for this task here.",
        )

        action_left, action_right = st.columns(2, gap="medium")
        with action_left:
            uploaded_file = st.file_uploader(
                "Upload File",
                type=["pdf", "png", "jpg", "jpeg"],
                accept_multiple_files=False,
                key=f"workspace_file_{st.session_state.file_uploader_nonce}",
                label_visibility="collapsed",
            )
        with action_right:
            run_prompt = st.button("Run Prompt", type="primary", width="stretch")

        if run_prompt:
            st.session_state.flash_message = None
            st.session_state.error_message = None
            current_choice = st.session_state.prompt_choice
            selected_prompt_title = (
                current_choice if current_choice != ADD_NEW_PROMPT else ""
            )
            try:
                run = service.run_prompt(
                    context_text=context_text,
                    prompt_title=selected_prompt_title,
                    prompt_body=st.session_state.prompt_editor_input,
                    files=_uploaded_file(uploaded_file),
                )
                st.session_state.output_text = run.output_text
                st.session_state.output_editor_input = run.output_text
                st.session_state.flash_message = "Prompt completed locally."
            except AppError as exc:
                st.session_state.error_message = _handle_error(exc)

        if st.session_state.error_message:
            st.markdown(
                f'<div class="ssa-error">{st.session_state.error_message}</div>',
                unsafe_allow_html=True,
            )
        elif st.session_state.flash_message:
            st.markdown(
                f'<div class="ssa-message">{st.session_state.flash_message}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="ssa-section-title ssa-section-title-output">AI Output</div>', unsafe_allow_html=True)
        output_text = st.text_area(
            "AI Output",
            key="output_editor_input",
            height=250,
            label_visibility="collapsed",
            placeholder="The local model output will appear here.",
        )
        st.session_state.output_text = output_text

        output_left, output_right = st.columns(2, gap="medium")
        with output_left:
            if st.button("Delete Output", width="stretch"):
                st.session_state.pending_output_sync = ""
                st.session_state.error_message = None
                st.session_state.flash_message = "Output deleted."
                st.rerun()
        with output_right:
            render_copy_button("Copy Output", output_text)

    with right_col:
        st.markdown('<div class="ssa-section-title">Prompts</div>', unsafe_allow_html=True)
        choice = st.selectbox(
            "Prompts",
            options=prompt_options,
            key="prompt_choice",
            label_visibility="collapsed",
        )
        if choice != st.session_state.loaded_prompt_choice:
            if choice == ADD_NEW_PROMPT:
                st.session_state.prompt_editor_input = ""
                st.session_state.loaded_prompt_choice = ADD_NEW_PROMPT
            else:
                _load_prompt_into_state(service, choice)

        prompt_body = st.text_area(
            "Selected Prompt",
            key="prompt_editor_input",
            height=520,
            label_visibility="collapsed",
            placeholder="Select a prompt from the menu above, or choose Add new Prompt and write one here.",
        )
        if st.button("Save Prompt", width="stretch"):
            saved_prompt = service.save_prompt_template(
                prompt_body,
                selected_title=None if choice == ADD_NEW_PROMPT else choice,
            )
            st.session_state.pending_prompt_choice = saved_prompt.title
            st.session_state.loaded_prompt_choice = None
            st.session_state.flash_message = f"Prompt saved: {saved_prompt.title}"
            st.session_state.error_message = None
            st.rerun()


if __name__ == "__main__":
    main()
