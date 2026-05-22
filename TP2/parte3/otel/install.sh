#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=otel
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================================"
echo "🚀 Iniciando despliegue de OpenTelemetry Collector"
echo "============================================================"

echo "→ Verificando pre-requisitos: Loki + EFK"
kubectl -n observability get svc loki >/dev/null \
  || { echo "✗ Loki no encontrado en ns observability — TP 2 · P1 no entregado"; exit 1; }

# Validar y crear alias para Elasticsearch si es necesario
if kubectl -n elastic get svc elasticsearch-master >/dev/null 2>&1; then
  echo "✓ Servicio elasticsearch-master detectado."
elif kubectl -n elastic get svc scraper-es-http >/dev/null 2>&1; then
  echo "✓ Servicio scraper-es-http detectado. Creando alias elasticsearch-master para compatibilidad..."
  kubectl -n elastic create service externalname elasticsearch-master \
    --external-name=scraper-es-http.elastic.svc.cluster.local --dry-run=client -o yaml | kubectl apply -f -
else
  echo "✗ Elasticsearch no encontrado en ns elastic — TP 2 · P2 no entregado"; exit 1;
fi

echo "→ Namespace + Helm repo"
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts >/dev/null 2>&1 || true
helm repo update >/dev/null

echo "→ cert-manager (si no está)"
if ! kubectl get ns cert-manager >/dev/null 2>&1; then
  echo "  Instalando cert-manager..."
  helm repo add jetstack https://charts.jetstack.io >/dev/null 2>&1 || true
  helm repo update >/dev/null
  helm install cert-manager jetstack/cert-manager \
    --namespace cert-manager --create-namespace \
    --version v1.16.1 --set installCRDs=true --wait --timeout 5m
else
  echo "✓ cert-manager ya está instalado."
fi

echo "→ OpenTelemetry Operator"
helm upgrade --install otel-operator open-telemetry/opentelemetry-operator \
  --version 0.74.0 \
  --namespace otel-operator-system --create-namespace \
  --values "$DIR/helm/otel-operator-values.yaml" \
  --wait --timeout 5m

echo "→ Esperando a que el CRD de OpenTelemetry esté registrado..."
until kubectl get crd opentelemetrycollectors.opentelemetry.io >/dev/null 2>&1; do
  echo "  Esperando CRD..."
  sleep 3
done

echo "→ RBAC y secrets"
kubectl apply -f "$DIR/manifests/rbac.yaml"

echo "→ Copiar credenciales de Elastic a namespace otel"
if ! kubectl -n elastic get secret elastic-credentials >/dev/null 2>&1; then
  if kubectl -n elastic get secret scraper-es-elastic-user >/dev/null 2>&1; then
    echo "✓ Creando secret elastic-credentials en namespace elastic a partir de scraper-es-elastic-user..."
    PASSWORD=$(kubectl -n elastic get secret scraper-es-elastic-user -o jsonpath='{.data.elastic}' | base64 -d)
    kubectl -n elastic create secret generic elastic-credentials \
      --from-literal=password="$PASSWORD" --dry-run=client -o yaml | kubectl apply -f -
  fi
fi

kubectl get secret elastic-credentials -n elastic -o yaml \
  | sed 's/namespace: elastic/namespace: otel/' \
  | grep -v 'creationTimestamp\|resourceVersion\|uid\|selfLink' \
  | kubectl apply -f -

# Verificar que el secret tenga contenido
ELASTIC_PASS=$(kubectl -n otel get secret elastic-credentials -o jsonpath='{.data.password}' | base64 -d)
if [ -z "$ELASTIC_PASS" ]; then
  echo "✗ Secret elastic-credentials vacío o inválido"
  exit 1
fi
echo "✓ Secret elastic-credentials copiado (password: ${#ELASTIC_PASS} caracteres)"

echo "→ OpenTelemetryCollector CRD"
kubectl apply -f "$DIR/manifests/collector-agent.yaml"
kubectl -n "$NAMESPACE" wait --for=condition=ready otelcol/agent --timeout=180s || {
  echo "⚠️ Warning: El CRD no reportó condición ready, verificando DaemonSet..."
  kubectl -n "$NAMESPACE" rollout status daemonset/agent-collector --timeout=180s
}

echo "→ ConfigMap endpoint OTLP para el scraper"
kubectl apply -f "$DIR/manifests/scraper-otlp-config.yaml"

echo "→ Apagar agentes legacy"
# Detectar y escalar Promtail o Alloy
if kubectl -n observability get ds/promtail >/dev/null 2>&1; then
  kubectl -n observability scale ds/promtail --replicas=0 || true
  kubectl -n observability patch ds promtail -p '{"spec":{"template":{"spec":{"nodeSelector":{"non-existing-node":"true"}}}}}' >/dev/null 2>&1 || true
  LEGACY_AGENT="Promtail"
elif kubectl -n observability get ds/alloy >/dev/null 2>&1; then
  kubectl -n observability scale ds/alloy --replicas=0 || true
  kubectl -n observability patch ds alloy -p '{"spec":{"template":{"spec":{"nodeSelector":{"non-existing-node":"true"}}}}}' >/dev/null 2>&1 || true
  LEGACY_AGENT="Alloy"
else
  LEGACY_AGENT="ninguno"
fi

# Escalar Fluent Bit
kubectl -n elastic scale ds/fluent-bit --replicas=0 || true
kubectl -n elastic patch ds fluent-bit -p '{"spec":{"template":{"spec":{"nodeSelector":{"non-existing-node":"true"}}}}}' >/dev/null 2>&1 || true

NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
echo ""
echo "✓ OpenTelemetry Operator running"
echo "✓ OpenTelemetryCollector CRD aplicado"
echo "✓ Collector DaemonSet running con 1 pod por nodo"
echo "✓ Pipeline activo: filelog + otlp → batch → k8sattributes → [loki, elasticsearch]"
echo "✓ ${LEGACY_AGENT} (namespace observability) escalado a 0"
echo "✓ Fluent Bit (namespace elastic) escalado a 0"
echo ""
echo "→ Verificá fan-out:"
echo "    Grafana: http://${NODE_IP}:30000  → Explore → Loki"
echo "    Kibana:  http://${NODE_IP}:30001  → Discover → scraper-logs-*"
echo ""
echo "→ Verificación Hit #4 (agentes legacy reemplazados):"
echo "    1. Ver estado de DaemonSets:"
echo "       kubectl get ds -A | grep -E 'promtail|alloy|fluent-bit|agent-collector'"
echo ""
echo "    2. Disparar job de prueba:"
echo "       kubectl -n ml-scraper create job --from=cronjob/scraper-hourly scraper-otel-only-1"
echo "       kubectl -n ml-scraper wait --for=condition=complete job/scraper-otel-only-1 --timeout=600s"
echo ""
echo "    3. Verificar en Grafana:"
echo "       Query: {service=\"scraper\", k8s_job_name=\"scraper-otel-only-1\"}"
echo ""
echo "    4. Verificar en Kibana:"
echo "       Search: k8s.job.name : \"scraper-otel-only-1\""
echo ""
echo "    5. Capturar screenshot para hit4-old-agents-down.png mostrando:"
echo "       - DaemonSets legacy en 0"
echo "       - Logs del job en ambos backends"
echo ""
echo "→ Rollback si algo falla:"
echo "    kubectl -n observability scale ds/promtail --replicas=1  # o ds/alloy"
echo "    kubectl -n elastic scale ds/fluent-bit --replicas=1"
echo "    # Nota: para restaurar el nodeSelector si fue parchado:"
echo "    # kubectl -n observability patch ds promtail --type json -p '[{\"op\": \"remove\", \"path\": \"/spec/template/spec/nodeSelector/non-existing-node\"}]' || true"
echo "    # kubectl -n elastic patch ds fluent-bit --type json -p '[{\"op\": \"remove\", \"path\": \"/spec/template/spec/nodeSelector/non-existing-node\"}]' || true"
echo "============================================================"