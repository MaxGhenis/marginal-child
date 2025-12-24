"""Modal deployment for The Marginal Child API."""

import modal

app = modal.App("marginal-child-api")

# Create image with all dependencies - Python 3.13 required for policyengine-uk >= 2.55
image = (
    modal.Image.debian_slim(python_version="3.13")
    .pip_install(
        "fastapi==0.115.0",
        "pydantic==2.12.0",
        "pydantic-settings==2.6.0",
        "pandas>=2.1.0",
        "numpy>=2.1.0",
        "policyengine-us>=1.428.0",
        "policyengine-uk>=2.55.0",
    )
    .add_local_dir("../marginal_child", "/root/marginal_child")
    .add_local_dir("app", "/root/app")
)


@app.function(
    image=image,
    cpu=2.0,
    memory=4096,
    timeout=300,
)
@modal.concurrent(max_inputs=10)
@modal.asgi_app()
def fastapi_app():
    """Serve the FastAPI app."""
    import sys
    sys.path.insert(0, "/root")

    from app.main import app as api
    return api
