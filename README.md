# dash-file-uploader

A secure file-upload component for Plotly Dash. The repository currently
contains the Python package foundation and callback data contracts; it does not
yet expose upload endpoints or transfer files.

## Foundation API

Uploader configuration is immutable and scoped to a single Dash app:

```python
from dash import Dash

from dash_file_uploader import configure_uploader

app = Dash(__name__)
configure_uploader(app)
```

The approved first-release limits are available through `UploadLimits`. An
application may lower the limits, but cannot raise them above the policy
baseline. Configuration currently stores policy only; it does not register
routes or provide authorization, storage, or a transfer implementation.

The `UploadEvent` and `CompletedFile` values describe the callback payload
contract in the blueprint. Completion references are identifiers, not
credentials, and are not currently issued or resolved by this foundation.

## Development

Requires Python 3.11–3.14 and `uv`:

```powershell
uv sync --locked --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv build
```

See [the blueprint](blueprint/README.md) for the architecture, security
requirements, remaining transport/deployment decisions, and implementation
roadmap. Upload protocol and deployment-specific storage/auth integrations are
intentionally not implemented until the required decisions are finalized.
