#!/usr/bin/env bash
set -euo pipefail

echo "→ Disparando job de prueba para fan-out..."
kubectl -n ml-scraper create job --from=cronjob/scraper-hourly scraper-fanout-verify 2>/dev/null || true
kubectl -n ml-scraper wait --for=condition=complete job/scraper-fanout-verify --timeout=600s

echo ""
echo "→ Esperando 10s para que los logs se procesen..."
sleep 10

echo ""
echo "✓ Job completado. Ahora verificar manualmente:"
echo ""
echo "  GRAFANA (Loki):"
echo "    1. Ir a http://$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}'):30000"
echo "    2. Explore → Loki"
echo "    3. Query: {service=\"scraper\", k8s_namespace_name=\"ml-scraper\"} | json | line_format \"{{.log_id}} {{.message}}\""
echo "    4. Copiar un log_id"
echo ""
echo "  KIBANA (Elasticsearch):"
echo "    1. Ir a http://$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}'):30001"
echo "    2. Discover → index scraper-logs-*"
echo "    3. Buscar: log_id : \"<el-log_id-copiado>\""
echo "    4. Debe aparecer el MISMO log"
echo ""
echo "  Si solo aparece en uno de los dos backends, revisar:"
kubectl -n otel logs ds/agent-collector --tail=50 | grep -i "error\|failed\|refused" || echo "    (No hay errores evidentes en los últimos 50 logs)"
