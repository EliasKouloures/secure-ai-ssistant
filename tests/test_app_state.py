from __future__ import annotations

from app.state import apply_reset, queue_reset


def test_queue_reset_only_marks_reset_request() -> None:
    state: dict[str, object] = {
        "pasted_text_input": "Parent email",
        "manual_note_input": "Reply kindly",
        "file_uploader_nonce": 2,
    }

    queue_reset(state)

    assert state["reset_requested"] is True
    assert state["pasted_text_input"] == "Parent email"
    assert state["manual_note_input"] == "Reply kindly"
    assert state["file_uploader_nonce"] == 2


def test_apply_reset_clears_inputs_and_advances_uploader_nonce() -> None:
    state: dict[str, object] = {
        "case_id": "case_123",
        "analysis": object(),
        "outputs": object(),
        "error_message": "broken",
        "pasted_text_input": "Parent email",
        "manual_note_input": "Reply kindly",
        "file_uploader_nonce": 2,
        "reset_requested": True,
    }

    apply_reset(state)

    assert state["case_id"] is None
    assert state["analysis"] is None
    assert state["outputs"] is None
    assert state["error_message"] is None
    assert state["pasted_text_input"] == ""
    assert state["manual_note_input"] == ""
    assert state["file_uploader_nonce"] == 3
    assert state["reset_requested"] is False
