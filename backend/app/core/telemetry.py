"""
telemetry.py – OpenTelemetry distributed tracing (Bonus).

Her API isteği otomatik olarak trace'lenir ve OTLP exporter aracılığıyla
Jaeger/Grafana Tempo gibi bir backend'e gönderilir.
OTEL_ENABLED=false ise hiçbir şey yapılmaz.
"""

from app.core.config import settings


def setup_tracing(app) -> None:
    """
    OpenTelemetry FastAPI instrumentasyonunu başlatır.
    settings.OTEL_ENABLED=True olmadan çağrılsa bile sessizce atlar.

    NOT: opentelemetry-exporter-otlp-proto-grpc >= 1.21.0 sürümünde
    `insecure` parametresi OTLPSpanExporter'dan kaldırıldı.
    gRPC endpoint'i http:// ile başladığında SDK otomatik olarak
    insecure kanal (credentials=None) kullanır. Kök neden buydu.
    """
    if not settings.OTEL_ENABLED:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        # Servis adını metadata olarak ekle
        resource = Resource.create({"service.name": settings.OTEL_SERVICE_NAME})
        provider = TracerProvider(resource=resource)

        # Span'ları OTLP gRPC üzerinden Jaeger'a gönder.
        # insecure=True kaldırıldı — http:// endpoint otomatik insecure kanal açar.
        exporter = OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
        provider.add_span_processor(BatchSpanProcessor(exporter))

        trace.set_tracer_provider(provider)

        # FastAPI middleware olarak otomatik instrumentasyon
        FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)

        print(f"[OTel] Tracing aktif → {settings.OTEL_EXPORTER_OTLP_ENDPOINT}")
    except ImportError as e:
        print(f"[OTel] opentelemetry paketleri bulunamadı, tracing devre dışı: {e}")
    except Exception as e:
        # TypeError veya AttributeError gibi runtime hatalarını yakala
        print(f"[OTel] Tracing başlatılamadı (runtime hata): {e}")
