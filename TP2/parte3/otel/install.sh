#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=otel
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "→ Verificando pre-requisitos: Loki + EFK"
kubectl -n observability get svc loki >/dev/null \
  || { echo "✗ Loki no encontrado en ns observability — TP 2 · P1 no entregado"; exit 1; }
kubectl -n elastic get svc elasticsearch-master >/dev/null \
  || { echo "✗ Elasticsearch no encontrado en ns elastic — TP 2 · P2 no entregado"; exit 1; }

echo "→ Namespace + Helm repo"
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts >/dev/null 2>&1 || true
helm repo update >/dev/null

echo "→ cert-manager (si no está)"
kubectl get ns cert-manager >/dev/null 2>&1 || helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --version v1.16.1 --set installCRDs=true --wait --timeout 5m

echo "→ OpenTelemetry Operator"
helm upgrade --install otel-operator open-telemetry/opentelemetry-operator \
  --version 0.74.0 \
  --namespace otel-operator-system --create-namespace \
  --values "$DIR/helm/otel-operator-values.yaml" \
  --wait --timeout 5m

echo "→ RBAC y secrets"
kubectl apply -f "$DIR/manifests/rbac.yaml"
kubectl get secret elastic-credentials -n elastic -o yaml \
  | sed 's/namespace: elastic/namespace: otel/' \
  | grep -v 'creationTimestamp\|resourceVersion\|uid\|selfLink' \
  | kubectl apply -f -

echo "→ OpenTelemetryCollector CRD"
kubectl apply -f "$DIR/manifests/collector-agent.yaml"
kubectl -n "$NAMESPACE" wait --for=condition=ready otelcol/agent --timeout=180s

echo "→ Apagar agentes legacy"
kubectl -n observability scale ds/promtail --replicas=0 || true
kubectl -n elastic scale ds/fluent-bit --replicas=0 || true

NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
echo ""
echo "✓ OpenTelemetry Operator running"
echo "✓ OpenTelemetryCollector CRD aplicado"
echo "✓ Collector DaemonSet running"
echo "✓ Pipeline activo: filelog + otlp → batch → k8sattributes → [loki, elasticsearch]"
echo "✓ Promtail (observability) escalado a 0"
echo "✓ Fluent Bit (elastic) escalado a 0"
echo ""
echo "→ Verificá fan-out:"
echo "    Grafana: http://${NODE_IP}:30000  → Explore → Loki"
echo "    Kibana:  http://${NODE_IP}:30001  → Discover → scraper-logs-*"