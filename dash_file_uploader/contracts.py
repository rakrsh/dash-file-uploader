"""Typed values for the public Dash callback contract."""

from dataclasses import dataclass
from enum import StrEnum


class UploadEventStatus(StrEnum):
    ACCEPTED = "accepted"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class UploadErrorCode(StrEnum):
    INVALID_REQUEST = "INVALID_REQUEST"
    UNAUTHENTICATED = "UNAUTHENTICATED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    LIMIT_EXCEEDED = "LIMIT_EXCEEDED"
    INVALID_STATE = "INVALID_STATE"
    UPLOAD_EXPIRED = "UPLOAD_EXPIRED"
    UPLOAD_CANCELLED = "UPLOAD_CANCELLED"
    INTEGRITY_FAILED = "INTEGRITY_FAILED"
    STORAGE_UNAVAILABLE = "STORAGE_UNAVAILABLE"
    TRANSFER_FAILED = "TRANSFER_FAILED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


def _validate_identifier(name: str, value: str) -> None:
    if not value or len(value) > 256 or any(ord(char) < 32 for char in value):
        raise ValueError(f"{name} must be a non-empty, printable string of at most 256 characters")


@dataclass(frozen=True, slots=True)
class UploadEvent:
    """A per-file lifecycle event suitable for a Dash callback."""

    event_id: str
    batch_id: str
    file_id: str
    status: UploadEventStatus
    code: UploadErrorCode | None = None
    message: str | None = None
    retryable: bool = False

    def __post_init__(self) -> None:
        _validate_identifier("event_id", self.event_id)
        _validate_identifier("batch_id", self.batch_id)
        _validate_identifier("file_id", self.file_id)
        if not isinstance(self.status, UploadEventStatus):
            raise ValueError("status must be an UploadEventStatus")
        if self.status is UploadEventStatus.FAILED:
            if self.code is not None and not isinstance(self.code, UploadErrorCode):
                raise ValueError("code must be an UploadErrorCode")
            if self.code is None or not self.message:
                raise ValueError(
                    "Failed upload events require a public error code and safe message"
                )
        elif self.code is not None or self.message is not None or self.retryable:
            raise ValueError("Error details are only valid for failed upload events")

    def to_dict(self) -> dict[str, str | bool]:
        """Return the stable camelCase shape used by component callback props."""
        result: dict[str, str | bool] = {
            "eventId": self.event_id,
            "batchId": self.batch_id,
            "fileId": self.file_id,
            "status": self.status.value,
        }
        if self.status is UploadEventStatus.FAILED:
            result.update(
                code=self.code.value if self.code is not None else "",
                message=self.message if self.message is not None else "",
                retryable=self.retryable,
            )
        return result


@dataclass(frozen=True, slots=True)
class CompletedFile:
    """A server-confirmed uploaded file reference and safe metadata."""

    upload_ref: str
    batch_id: str
    filename: str
    size: int
    media_type: str | None

    def __post_init__(self) -> None:
        _validate_identifier("upload_ref", self.upload_ref)
        _validate_identifier("batch_id", self.batch_id)
        if not self.filename:
            raise ValueError("filename must not be empty")
        if isinstance(self.size, bool) or not isinstance(self.size, int) or self.size < 0:
            raise ValueError("size must be a non-negative integer")

    def to_dict(self) -> dict[str, str | int | None]:
        """Return the stable camelCase shape used by component callback props."""
        return {
            "uploadRef": self.upload_ref,
            "batchId": self.batch_id,
            "filename": self.filename,
            "size": self.size,
            "mediaType": self.media_type,
        }
