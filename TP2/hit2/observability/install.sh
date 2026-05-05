#!/bin/bash
set -e

# Asegurar que estamos en el directorio correcto
cd "$(dirname "$0")"

echo "============================================================"
echo "🚀 Iniciando despliegue del stack Loki + Promtail + Grafana"
echo "============================================================"

# 1. Namespace
echo "📦 Creando namespace 'observability'..."
kubectl apply -f manifests/namespace.yaml

# 2. Secret para Grafana
echo "🔐 Provisionando credenciales para Grafana..."
if [ ! -f "manifests/grafana-secret.yaml" ]; then
    echo "❌ ERROR: manifests/grafana-secret.yaml no encontrado. Revisa el README para crearlo primero."
    exit 1
fi
kubectl apply -f manifests/grafana-secret.yaml

# 3. Preparando ConfigMap con Dashboard para el Hit #5
echo "📊 Creando ConfigMap para el dashboard provisionado..."
kubectl create configmap grafana-dashboards-sip2026 \
  --namespace observability \
  --from-file=dashboards/scraper-overview.json -o yaml --dry-run=client | kubectl apply -f -

# 4. Agregando/Actualizando repositorios de Helm
echo "🔄 Configurando repositorio Helm de Grafana..."
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# 5. Instalando Loki
echo "🪵 Instalando Loki (modo single-binary, storage local)..."
helm upgrade --install loki grafana/loki \
  --version 6.16.0 \
  --namespace observability \
  --values helm/loki-values.yaml

# 6. Instalando Promtail
echo "🕷️ Instalando Promtail (DaemonSet)..."
helm upgrade --install promtail grafana/promtail \
  --version 6.16.0 \
  --namespace observability \
  --values helm/promtail-values.yaml

# 7. Instalando Grafana
echo "📈 Instalando Grafana (con datasource y dashboards as-code)..."
helm upgrade --install grafana grafana/grafana \
  --version 8.5.0 \
  --namespace observability \
  --values helm/grafana-values.yaml

# 8. Esperando a que el stack levante
echo "⏳ Esperando a que los componentes estén en estado READY..."
echo "  [1/3] Loki..."
kubectl rollout status statefulset/loki -n observability --timeout=180s || echo "Warning: timeout esperando a Loki"
echo "  [2/3] Promtail..."
kubectl rollout status daemonset/promtail -n observability --timeout=120s || echo "Warning: timeout esperando a Promtail"
echo "  [3/3] Grafana..."
kubectl rollout status deploy/grafana -n observability --timeout=120s || echo "Warning: timeout esperando a Grafana"

echo "============================================================"
echo "✅ Despliegue completado con éxito."
echo "============================================================"
echo ""
echo "Output esperado:"
echo "  ✓ Loki running         (kubectl get pod -n observability -l app=loki)"
echo "  ✓ Promtail running     (DaemonSet con 1 pod por nodo)"
echo "  ✓ Grafana running      (NodePort 30000 abierto)"
echo "  ✓ Datasource validado  (Loki disponible en Grafana)"
echo "  ✓ Dashboard 'Scraper Overview' provisionado"
echo ""

# Intentar obtener la IP del nodo principal (solo informativo)
NODE_IP=$(kubectl get nodes -o wide | awk 'NR==2 {print $6}' 2>/dev/null || echo "<node-ip>")
if [ "$NODE_IP" = "<node-ip>" ] || [ -z "$NODE_IP" ]; then
    NODE_IP=$(hostname -I | awk '{print $1}')
fi

echo "👉 Abrir Grafana: http://${NODE_IP}:30000"
echo "👉 Usuario: admin"
echo "👉 Contraseña: Ver manifests/grafana-secret.yaml (o ejecutar: kubectl get secret -n observability grafana-admin -o jsonpath=\"{.data.admin-password}\" | base64 --decode)"
echo ""
echo "Para verificar logs iniciales entra a Explore -> Loki -> query {namespace=\"observability\"}"
echo "============================================================"
