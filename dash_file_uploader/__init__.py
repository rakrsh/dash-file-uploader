"""Python foundations for the Dash file uploader."""

from dash_file_uploader.app import configure_uploader, get_uploader_config
from dash_file_uploader.config import UploaderConfig, UploadLimits
from dash_file_uploader.contracts import (
    CompletedFile,
    UploadErrorCode,
    UploadEvent,
    UploadEventStatus,
)

__all__ = [
    "CompletedFile",
    "UploadErrorCode",
    "UploadEvent",
    "UploadEventStatus",
    "UploadLimits",
    "UploaderConfig",
    "configure_uploader",
    "get_uploader_config",
]

__version__ = "0.0.0"
