"""Validated, conservative server-side upload policy defaults."""

from dataclasses import dataclass

GIB = 1024**3
MIB = 1024**2
HOUR = 60 * 60
DAY = 24 * HOUR


@dataclass(frozen=True, slots=True)
class UploadLimits:
    """Upload limits from the approved first-release policy.

    Applications may lower these values, but cannot raise them beyond the
    project-wide policy. Enforcement at the HTTP/storage boundary is part of
    the future protocol implementation.
    """

    max_file_size_bytes: int = 5 * GIB
    max_request_size_bytes: int = 64 * MIB
    max_files_per_batch: int = 10
    max_batch_size_bytes: int = 10 * GIB
    max_concurrent_transfers_per_user: int = 3
    max_staging_size_bytes_per_user: int = 10 * GIB
    idle_timeout_seconds: int = DAY
    max_session_age_seconds: int = 7 * DAY

    def __post_init__(self) -> None:
        values = {
            "max_file_size_bytes": (self.max_file_size_bytes, 5 * GIB),
            "max_request_size_bytes": (self.max_request_size_bytes, 64 * MIB),
            "max_files_per_batch": (self.max_files_per_batch, 10),
            "max_batch_size_bytes": (self.max_batch_size_bytes, 10 * GIB),
            "max_concurrent_transfers_per_user": (
                self.max_concurrent_transfers_per_user,
                3,
            ),
            "max_staging_size_bytes_per_user": (
                self.max_staging_size_bytes_per_user,
                10 * GIB,
            ),
            "idle_timeout_seconds": (self.idle_timeout_seconds, DAY),
            "max_session_age_seconds": (self.max_session_age_seconds, 7 * DAY),
        }
        for name, (value, maximum) in values.items():
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
            if value > maximum:
                raise ValueError(f"{name} cannot exceed the approved maximum of {maximum}")

        if self.max_request_size_bytes > self.max_file_size_bytes:
            raise ValueError("max_request_size_bytes cannot exceed max_file_size_bytes")
        if self.max_file_size_bytes > self.max_batch_size_bytes:
            raise ValueError("max_file_size_bytes cannot exceed max_batch_size_bytes")
        if self.idle_timeout_seconds > self.max_session_age_seconds:
            raise ValueError("idle_timeout_seconds cannot exceed max_session_age_seconds")


@dataclass(frozen=True, slots=True)
class UploaderConfig:
    """Immutable configuration for one Dash app."""

    limits: UploadLimits = UploadLimits()
