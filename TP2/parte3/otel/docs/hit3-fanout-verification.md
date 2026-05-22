# Hit #3 - Verificación de Fan-out

## 1. Disparar tráfico
```bash
kubectl -n ml-scraper create job --from=cronjob/scraper-hourly scraper-fanout-1
kubectl -n ml-scraper wait --for=condition=complete job/scraper-fanout-1 --timeout=600s
```

## 2. Verificar en Loki (Grafana)
- URL: http://<node-ip>:30000
- Ir a Explore → Loki
- Query: `{service="scraper", k8s_namespace_name="ml-scraper"} | json | line_format "{{.log_id}} {{.message}}"`
- Copiar un log_id ejemplo: `aa1b2c3d-4e5f-6789-abcd-ef0123456789`

## 3. Verificar en Elasticsearch (Kibana)
- URL: http://<node-ip>:30001
- Ir a Discover
- Seleccionar index pattern: `scraper-logs-*`
- Buscar: `log_id : "aa1b2c3d-4e5f-6789-abcd-ef0123456789"`
- Debe aparecer el MISMO log que en Loki

## 4. Troubleshooting

### Solo aparece en Loki:
```bash
# Verificar logs del colector buscando errores de Elasticsearch
kubectl -n otel logs ds/agent-collector | grep -i "elastic\|error"

# Verificar conectividad
kubectl -n otel exec ds/agent-collector -- curl -k https://elasticsearch-master.elastic:9200 -u elastic:$PASS

# Verificar secret
kubectl -n otel get secret elastic-credentials -o jsonpath='{.data.password}' | base64 -d
```

### Solo aparece en Elasticsearch:
```bash
# Verificar que Loki sea >= 3.0 (soporte OTLP)
kubectl -n observability logs deploy/loki | grep "version"

# Verificar endpoint OTLP de Loki
kubectl -n otel exec ds/agent-collector -- curl http://loki.observability:3100/ready

# Verificar logs del colector
kubectl -n otel logs ds/agent-collector | grep -i "loki\|otlp"
```

### No aparece en ninguno:
```bash
# Verificar que el colector esté procesando logs
kubectl -n otel logs ds/agent-collector | grep -i "ResourceLog\|exported"

# Verificar que el job del scraper haya generado logs
kubectl -n ml-scraper logs job/scraper-fanout-1
```
