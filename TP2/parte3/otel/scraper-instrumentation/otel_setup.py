import logging
import os
import socket

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_otel(service_name: str = "scraper") -> None:
    """
    Configura logging + tracing OTel.

    Lee OTEL_EXPORTER_OTLP_ENDPOINT (default: http://localhost:4317).
    Si la app está en un Pod, este env var se inyecta via ConfigMap apuntando
    al collector DaemonSet en el mismo nodo (ver scraper-otlp-config.yaml).
    """
    endpoint = os.environ.get(
        "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"
    )

    # Resource: metadata adjunta a todas las señales
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": os.environ.get("APP_VERSION", "dev"),
            "host.name": socket.gethostname(),
            "deployment.environment": os.environ.get("ENV", "tp"),
        }
    )

    # === Tracing ===
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint, insecure=True))
    )
    trace.set_tracer_provider(tracer_provider)

    # === Logging ===
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=endpoint, insecure=True))
    )
    set_logger_provider(logger_provider)

    # Bridge: redirigí el módulo `logging` standard a OTel.
    # Esto significa que todos los `logger.info(...)` del scraper salen via OTLP
    # SIN cambiar ni una línea de los call-sites.
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.basicConfig(level=logging.INFO, handlers=[handler])