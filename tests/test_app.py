import pytest
from dash import Dash

from dash_file_uploader import (
    UploaderConfig,
    UploadLimits,
    configure_uploader,
    get_uploader_config,
)


def test_configuration_is_scoped_to_each_dash_app() -> None:
    first = Dash(__name__)
    second = Dash(__name__)
    first_config = UploaderConfig(
        limits=UploadLimits(max_file_size_bytes=1024, max_request_size_bytes=512)
    )
    second_config = UploaderConfig(
        limits=UploadLimits(max_file_size_bytes=2048, max_request_size_bytes=1024)
    )

    configure_uploader(first, first_config)
    configure_uploader(second, second_config)

    assert get_uploader_config(first) is first_config
    assert get_uploader_config(second) is second_config


def test_configuration_is_not_implicitly_overwritten() -> None:
    app = Dash(__name__)
    configure_uploader(app)

    with pytest.raises(ValueError, match="already has"):
        configure_uploader(app)


def test_reading_unconfigured_app_fails_explicitly() -> None:
    with pytest.raises(LookupError, match="has not been set up"):
        get_uploader_config(Dash(__name__))
