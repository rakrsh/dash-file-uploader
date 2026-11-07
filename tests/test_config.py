import pytest

from dash_file_uploader import UploaderConfig, UploadLimits
from dash_file_uploader.config import GIB, MIB


def test_default_limits_match_approved_policy() -> None:
    limits = UploadLimits()

    assert limits.max_file_size_bytes == 5 * GIB
    assert limits.max_request_size_bytes == 64 * MIB
    assert limits.max_files_per_batch == 10
    assert limits.max_batch_size_bytes == 10 * GIB
    assert limits.max_concurrent_transfers_per_user == 3
    assert limits.max_staging_size_bytes_per_user == 10 * GIB
    assert limits.idle_timeout_seconds == 24 * 60 * 60
    assert limits.max_session_age_seconds == 7 * 24 * 60 * 60


def test_applications_can_lower_but_not_raise_limits() -> None:
    config = UploaderConfig(limits=UploadLimits(max_file_size_bytes=2 * GIB))

    assert config.limits.max_file_size_bytes == 2 * GIB
    with pytest.raises(ValueError, match="approved maximum"):
        UploadLimits(max_file_size_bytes=6 * GIB)


@pytest.mark.parametrize(
    "override",
    [
        {"max_file_size_bytes": 0},
        {"max_file_size_bytes": True},
        {"max_file_size_bytes": 6 * GIB},
        {"max_request_size_bytes": 65 * MIB},
        {"max_files_per_batch": 11},
        {"max_concurrent_transfers_per_user": 4},
        {"idle_timeout_seconds": 7 * 24 * 60 * 60 + 1},
    ],
)
def test_invalid_or_excessive_limits_are_rejected(override: dict[str, int]) -> None:
    with pytest.raises(ValueError):
        UploadLimits(**override)


def test_inconsistent_limits_are_rejected() -> None:
    with pytest.raises(ValueError, match="max_file_size_bytes cannot exceed"):
        UploadLimits(max_file_size_bytes=5 * GIB, max_batch_size_bytes=4 * GIB)

    with pytest.raises(ValueError, match="idle_timeout_seconds cannot exceed"):
        UploadLimits(idle_timeout_seconds=2 * 24 * 60 * 60)
