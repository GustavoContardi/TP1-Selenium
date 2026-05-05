# EFK — Elasticsearch + Fluent Bit + Kibana

Stack de logging centralizado con full-text search, desplegado en paralelo al stack Loki (namespace `observability`).

## Estructura

```
efk/
├── README.md                       ← este archivo
├── helm/
│   ├── eck-operator-values.yaml    ← values del ECK Operator
│   └── fluent-bit-values.yaml      ← values de Fluent Bit
├── manifests/
│   ├── namespace.yaml              ← namespaces elastic + elastic-system
│   ├── elasticsearch.yaml          ← CR Elasticsearch (ECK CRD)
│   ├── kibana.yaml                 ← CR Kibana (ECK CRD)
│   ├── kibana-nodeport.yaml        ← Service NodePort 30001
│   └── ilm-policy.json             ← Index Lifecycle Management policy
├── dashboards/
│   └── scraper-overview.ndjson     ← dashboard exportado (Hit #5)
├── queries/
│   └── kql-cookbook.md              ← 6 queries KQL documentadas (Hit #4)
├── screenshots/                    ← evidencia visual por hit
└── install.sh                      ← script idempotente
```

## Pre-requisitos

- Cluster k3s/k3d con **8 GB de RAM libre** + **15 GB de disco**.
- Helm 3 (≥ 3.16) y kubectl (≥ 1.30).
- Stack Loki de Parte 1 corriendo en namespace `observability`.
- `vm.max_map_count >= 262144` en el host:
  ```bash
  sudo sysctl -w vm.max_map_count=262144
  # Persistir: echo "vm.max_map_count=262144" | sudo tee /etc/sysctl.d/99-elastic.conf
  ```

## Levantar el stack

```bash
cd efk && ./install.sh
```

El script es idempotente (usa `helm upgrade --install` y `kubectl apply`). Al terminar muestra la IP y credenciales para acceder a Kibana.

## Acceder a Kibana

```bash
# Password del usuario elastic (generado por ECK, nunca commiteado):
kubectl -n elastic get secret scraper-es-elastic-user -o jsonpath='{.data.elastic}' | base64 -d

# Abrir en el browser:
# https://<node-ip>:30001
# Usuario: elastic
# Password: el que devolvió el comando anterior
```

## Versiones pinneadas

| Componente | Versión |
|---|---|
| ECK Operator | 2.16.0 |
| Elasticsearch | 8.17.3 |
| Kibana | 8.17.3 |
| Fluent Bit | 3.2.4 (chart 0.48.5) |

## Resources del stack

| Componente | Requests | Limits | Storage |
|---|---|---|---|
| ECK Operator | 50m CPU, 128Mi RAM | 100m CPU, 256Mi RAM | — |
| Elasticsearch (1 nodo) | 500m CPU, 1Gi RAM | 1000m CPU, 2Gi RAM | 10Gi PVC |
| Kibana | 200m CPU, 512Mi RAM | 500m CPU, 1Gi RAM | — |
| Fluent Bit (DaemonSet) | 50m CPU, 64Mi RAM | 200m CPU, 128Mi RAM | — |

## Nota sobre RAM en cluster local

Si el cluster no soporta Loki + EFK simultáneamente, durante el desarrollo se puede bajar uno de los dos stacks temporalmente. Para la entrega final ambos deben estar corriendo al mismo tiempo.

## Variables de entorno

- `DISCORD_WEBHOOK_URL` (opcional, solo Hit #6 bonus): URL del webhook de Discord para alertas.

No se necesita configurar la password de Elasticsearch manualmente — ECK la genera automáticamente.
