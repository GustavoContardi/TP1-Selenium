"""
Setup de OpenTelemetry SDK: TracerProvider + LoggerProvider con OTLP exporter.
Reemplaza logging_setup.py del TP 2 · Parte 1.
"""

import atexit
import logging
import os
import socket

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_otel(service_name: str = "scraper") -> None:
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

    resource = Resource.create({
        "service.name": service_name,
        "service.version": os.environ.get("APP_VERSION", "dev"),
        "host.name": socket.gethostname(),
        "deployment.environment": os.environ.get("ENV", "tp"),
    })

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

    # Bridge: redirige el módulo logging estándar a OTel sin tocar los call-sites
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.basicConfig(level=logging.INFO, handlers=[handler])

    # Flush garantizado al salir — evita perder los últimos logs en el buffer del batch
    atexit.register(logger_provider.shutdown)
    atexit.register(tracer_provider.shutdown)
