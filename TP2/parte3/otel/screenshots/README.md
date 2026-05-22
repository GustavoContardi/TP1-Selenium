# Capturas de Pantalla de Validación

Este directorio almacena las capturas de pantalla que validan el correcto funcionamiento de la infraestructura de observabilidad.

## Hit #2 - Validación del Debug Exporter

Para completar la entrega del **Hit #2**, debes capturar una pantalla que demuestre que el colector está enriqueciendo y depurando logs de manera exitosa:

1. **Captura Requerida**:
   - Capturar la salida en terminal del comando:
     ```bash
     kubectl -n otel logs ds/agent-collector | grep -A 25 "ResourceLog"
     ```
2. **Debe Visualizarse en la Imagen**:
   - El bloque `ResourceLog` que contenga atributos del Pod como:
     - `k8s.namespace.name: ml-scraper`
     - `k8s.pod.name` (que empiece con `scraper-otel-test-1-*`)
     - `service: scraper` (inyectado por el procesador de atributos)
   - El `Body` del registro mostrando la cadena JSON con el log original estructurado por el scraper.
   - El `Timestamp` y `ObservedTimestamp` con marcas temporales coherentes.

3. **Nombre del Archivo**:
   - Guardar como: `hit2-debug-output.png`

---

## Hit #3 - Fan-out (BLOQUEANTE)

Para completar la entrega del **Hit #3**, debes capturar las siguientes pantallas demostrando el flujo simultáneo de logs enriquecidos con UUID:

### hit3-fanout-loki.png
- **Ruta**: Grafana → Explore → Loki
- **Query**: `{service="scraper", k8s_namespace_name="ml-scraper"} | json | line_format "{{.log_id}} {{.message}}"`
- **Detalle**: Debe mostrarse CLARAMENTE el campo `log_id` (UUID completo visible), el timestamp y el mensaje del log.

### hit3-fanout-elastic.png  
- **Ruta**: Kibana → Discover → index `scraper-logs-*`
- **Query / Búsqueda**: `log_id : "<el-mismo-uuid-de-loki>"`
- **Detalle**: Debe mostrarse el **MISMO** `log_id` que en Loki, el timestamp y campos relevantes (`k8s.*`, `service`, etc.).

> [!WARNING]
> **CRÍTICO**: Ambos screenshots deben mostrar el **MISMO** log_id UUID. Si los UUIDs no coinciden o faltan screenshots, el Hit #3 = 0 puntos.
