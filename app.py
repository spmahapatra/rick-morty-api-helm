"""Root entrypoint proxy for Gunicorn, Docker, and legacy runners.

Delegates directly to src.app so the application can be run as either
`app:app` or `src.app:app`.
"""
from src.app import (  # noqa: F401
    FILTERS,
    DEFAULT_LIMIT,
    DEFAULT_PAGE,
    MAX_LIMIT,
    RICK_AND_MORTY_API_BASE_URL,
    RickAndMortyAPIError,
    RickAndMortyClient,
    app,
    cache_backend,
    cache_middleware,
    filter_characters_by_origin,
    handle_api_errors,
    logger,
    metrics_collector,
    paginate_characters,
    sort_characters,
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
