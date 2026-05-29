"""
metrics.py – Prometheus metrik yapılandırması.

prometheus-fastapi-instrumentator kütüphanesi kullanılarak:
- İstek süresi (latency) histogramı
- İstek sayısı sayacı
- /metrics endpoint'i (Prometheus'un scrape ettiği yer)

otomatik olarak eklenir.
"""

from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app) -> None:
    """
    FastAPI uygulamasına Prometheus instrumentasyonu ekler.
    /metrics endpoint'i Prometheus tarafından scrape edilir.
    """
    Instrumentator(
        # Her HTTP status kodunu ayrı label olarak tut
        should_group_status_codes=False,
        # Health check ve metrics endpoint'ini ölçümün dışında tut
        excluded_handlers=["/health", "/metrics"],
    ).instrument(app).expose(app)
