# 0010 — Adopción de OpenTelemetry para instrumentación vendor-neutral

- Date: 2026-05-22
- Status: Accepted
- Deciders: Gustavo

## Contexto

En las entregas anteriores implementamos dos pipelines de logging independientes que operaban en paralelo:
1. **Loki + Promtail + Grafana** (en el namespace `observability`): para consultas ágiles del día a día y bajo footprint.
2. **Elasticsearch + Fluent Bit + Kibana** (en el namespace `elastic`): para búsquedas de texto completo estructuradas e indexadas.

Esta arquitectura presentaba los siguientes inconvenientes y limitaciones:
- **Duplicación de Agentes en los Nodos**: Promtail y Fluent Bit corrían como DaemonSets simultáneos leyendo el mismo path de logs en `/var/log/pods`. Esto duplicaba el overhead de CPU/RAM en los nodos del cluster k3s local.
- **Acoplamiento Fuerte (Vendor Lock-in)**: El scraper de Python estaba atado a escribir en formato JSON compatible con expresiones parser específicas en la configuración de cada agente. Cualquier cambio de backend de logging requería reconfigurar y reinstalar el agente colector correspondiente.
- **Falta de Estandarización**: No existía un formato unificado para la correlación de logs y trazas distribuidas (tracing), lo que dificultaba unificar las señales en el futuro.
- **Escalabilidad y Flexibilidad**: Si en el futuro quisiéramos enviar los logs a un tercer backend o un proveedor SaaS (como Datadog, Dynatrace, Grafana Cloud, New Relic, etc.), tendríamos que agregar otro agente específico o modificar significativamente el pipeline existente.

## Decisión

Se decide adoptar **OpenTelemetry (OTel)** como estándar unificado y neutro de observabilidad para todo el proyecto, implementando los siguientes cambios:

1. **Reemplazar Promtail y Fluent Bit** por un único DaemonSet de **OpenTelemetry Collector Contrib** corriendo en el namespace `otel`.
2. **Instrumentar el scraper de Python** directamente con el **OpenTelemetry SDK** (usando `opentelemetry-sdk` y `opentelemetry-exporter-otlp`), exportando logs y trazas de forma nativa a través del protocolo **OTLP (gRPC/HTTP)**.
3. **Configurar el colector OTel en modo Fan-out**:
   - Recibir logs locales de `/var/log/pods` (vía receiver `filelog`) y señales directas por red del scraper (vía receiver `otlp`).
   - Procesar y enriquecer las señales con metadata de Kubernetes (procesador `k8sattributes`).
   - Exportar en paralelo hacia **Loki** (vía `otlphttp`) y **Elasticsearch** (vía exporter nativo).
4. **Escalar a 0 replicas y desactivar** los agentes legacy Promtail y Fluent Bit en el cluster.

## Consecuencias

### Positivas

- **Eliminación del Lock-in de Proveedor**: La aplicación utiliza librerías de OpenTelemetry que son un estándar de la CNCF. El backend de destino se decide 100% en la configuración del colector OTel, sin modificar el código de la aplicación.
- **Reducción de Recursos en el Nodo**: Al consolidar Promtail y Fluent Bit en un único colector OTel DaemonSet, reducimos el consumo de memoria RAM y CPU en el cluster k3s.
- **Soporte de Industria y SaaS**: OTLP es soportado de forma nativa por prácticamente todos los proveedores de observabilidad modernos (Datadog, Dynatrace, New Relic, Honeycomb, AWS ADOT, etc.). Migrar o hacer mirror a estos servicios es cuestión de añadir un exporter en el YAML del colector.
- **Correlación Nativa de Señales**: Al usar OTel SDK, podemos inyectar `trace_id` y `span_id` directamente en los logs, permitiendo saltar de un trace a sus logs asociados en un solo click dentro de Grafana o Kibana.
- **Idempotencia de Pipeline**: El colector abstrae el procesamiento (batching, formateo, estructuración) permitiendo que cada backend reciba los datos en su formato nativo óptimo.

### Negativas

- **Curva de Aprendizaje**: Configurar el pipeline del colector de OpenTelemetry (`receivers`, `processors`, `exporters`) añade una capa de complejidad técnica inicial comparado con configuraciones más simples como la de Promtail.
- **Overhead de Librerías OTel**: La instrumentación nativa en Python añade dependencias externas adicionales en `requirements.txt` y requiere inicializar los providers en el código de entrada del scraper.

## Referencias

- OpenTelemetry Collector Contrib: https://github.com/open-telemetry/opentelemetry-collector-contrib
- Especificación de OTLP: https://opentelemetry.io/docs/specs/otlp/
- Soporte de OTLP en Loki: https://grafana.com/docs/loki/latest/send-data/otel/
- Soporte de OTLP en Elasticsearch: https://www.elastic.co/guide/en/observability/current/open-telemetry.html
