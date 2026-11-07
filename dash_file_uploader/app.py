"""Dash-app-scoped uploader configuration."""

from dash import Dash

from dash_file_uploader.config import UploaderConfig

_CONFIG_ATTRIBUTE = "_dash_file_uploader_config"


def configure_uploader(
    app: Dash,
    config: UploaderConfig | None = None,
) -> UploaderConfig:
    """Attach immutable uploader configuration to one Dash app.

    This foundation does not register upload routes or provide a transfer
    implementation; those depend on the protocol and deployment decisions.
    """
    if _CONFIG_ATTRIBUTE in vars(app):
        raise ValueError("This Dash app already has uploader configuration")

    configured = config if config is not None else UploaderConfig()
    setattr(app, _CONFIG_ATTRIBUTE, configured)
    return configured


def get_uploader_config(app: Dash) -> UploaderConfig:
    """Return configuration previously attached to this Dash app."""
    configured = vars(app).get(_CONFIG_ATTRIBUTE)
    if not isinstance(configured, UploaderConfig):
        raise LookupError("Uploader configuration has not been set up for this Dash app")
    return configured
