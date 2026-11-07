import pytest

from dash_file_uploader import (
    CompletedFile,
    UploadErrorCode,
    UploadEvent,
    UploadEventStatus,
)


def test_failed_event_serializes_public_error_fields() -> None:
    event = UploadEvent(
        event_id="event-1",
        batch_id="batch-1",
        file_id="file-1",
        status=UploadEventStatus.FAILED,
        code=UploadErrorCode.TRANSFER_FAILED,
        message="The transfer could not be completed.",
        retryable=True,
    )

    assert event.to_dict() == {
        "eventId": "event-1",
        "batchId": "batch-1",
        "fileId": "file-1",
        "status": "failed",
        "code": "TRANSFER_FAILED",
        "message": "The transfer could not be completed.",
        "retryable": True,
    }


def test_non_failure_event_does_not_expose_error_fields() -> None:
    event = UploadEvent(
        event_id="event-1",
        batch_id="batch-1",
        file_id="file-1",
        status=UploadEventStatus.ACCEPTED,
    )

    assert event.to_dict() == {
        "eventId": "event-1",
        "batchId": "batch-1",
        "fileId": "file-1",
        "status": "accepted",
    }


def test_failed_event_requires_error_details() -> None:
    with pytest.raises(ValueError, match="require a public error code"):
        UploadEvent(
            event_id="event-1",
            batch_id="batch-1",
            file_id="file-1",
            status=UploadEventStatus.FAILED,
        )


def test_completed_file_serializes_only_safe_public_metadata() -> None:
    uploaded = CompletedFile(
        upload_ref="opaque-reference",
        batch_id="batch-1",
        filename="report.pdf",
        size=42,
        media_type="application/pdf",
    )

    assert uploaded.to_dict() == {
        "uploadRef": "opaque-reference",
        "batchId": "batch-1",
        "filename": "report.pdf",
        "size": 42,
        "mediaType": "application/pdf",
    }


@pytest.mark.parametrize("size", [-1, True])
def test_completed_file_rejects_invalid_size(size: int) -> None:
    with pytest.raises(ValueError, match="size must be"):
        CompletedFile("ref", "batch", "file.dat", size, None)
