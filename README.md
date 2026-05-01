# TP1-Selenium
TP1 Selenium

## Hit #7 — Kubernetes

### Prerrequisitos
- k3s o k3d instalado y cluster activo (ver TP 0)
- Imagen Docker buildeada: `docker build -t ml-scraper:latest .`

### Importar la imagen al cluster

**k3s nativo:**
```bash
docker save ml-scraper:latest -o /tmp/ml-scraper.tar
sudo k3s ctr images import /tmp/ml-scraper.tar
rm /tmp/ml-scraper.tar
```

**k3d:**
```bash
k3d image import ml-scraper:latest -c <nombre-del-cluster>
```

### Aplicar todos los manifests
```bash
kubectl apply -f hit7/k8s/
```

### Disparar el Job one-off y seguir los logs
```bash
kubectl get jobs
kubectl wait --for=condition=complete job/scraper-once --timeout=600s
kubectl logs -l job-type=one-off -f
```

### Verificar los JSON generados en el PVC
```bash
kubectl exec -it $(kubectl get pod -l job-type=one-off -o jsonpath='{.items[0].metadata.name}') -- ls /app/output
```

### Verificar el CronJob
```bash
kubectl get cronjobs
kubectl get jobs --watch
```

### Limpiar todos los recursos
```bash
kubectl delete -f hit7/k8s/
```

---

## Hit #8 — Capacidad extendida (paginación, estadísticas, histórico Postgres)

### Nuevas capacidades

| Capacidad | Descripción |
|---|---|
| Paginación | Hasta 30 resultados navegando 3 páginas por producto (`MAX_PAGES=3`) |
| Estadísticas | Tabla de min/max/mediana/promedio/desvío impresa en stdout + `output/stats.json` |
| Histórico | Resultados persistidos en PostgreSQL para acumular corridas del CronJob |

### Prerrequisitos adicionales

- PostgreSQL desplegado en el cluster (ver sección "Despliegue de Postgres en k3s").
- `k8s/postgres-secret.yaml` creado manualmente (ver abajo, **no** se commitea).

---

### Despliegue de Postgres en k3s

#### 1. Crear el Secret (NUNCA commitear este archivo)

```bash
# El archivo k8s/postgres-secret.yaml está en .gitignore.
# Crearlo manualmente o inyectarlo desde CI como GitHub Secret.
cat > hit8/k8s/postgres-secret.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: postgres-credentials
  labels:
    app: postgres
type: Opaque
stringData:
  POSTGRES_DB: scraper_db
  POSTGRES_USER: scraper
  POSTGRES_PASSWORD: <tu-password-segura>
EOF
```

#### 2. Aplicar todos los manifests de Postgres

```bash
kubectl apply -f hit8/k8s/postgres-secret.yaml
kubectl apply -f hit8/k8s/postgres-pvc.yaml
kubectl apply -f hit8/k8s/postgres-statefulset.yaml
kubectl apply -f hit8/k8s/postgres-service.yaml
```

#### 3. Esperar a que Postgres esté listo

```bash
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s
```

#### 4. Aplicar manifests del scraper

```bash
kubectl apply -f hit8/k8s/configmap.yaml
kubectl apply -f hit8/k8s/job.yaml
kubectl apply -f hit8/k8s/cronjob.yaml
```

---

### Variables de entorno

| Variable | Descripción | Default |
|---|---|---|
| `BROWSER` | `chrome` \| `firefox` | `chrome` |
| `HEADLESS` | `true` \| `false` | `true` |
| `MAX_PAGES` | Páginas a paginar por producto | `3` |
| `PRODUCTS` | Lista de productos (newline-separated) | 3 productos por defecto |
| `POSTGRES_HOST` | Host de Postgres; si no está definido, se **omite** la escritura a la base | — |
| `POSTGRES_PORT` | Puerto de Postgres | `5432` |
| `POSTGRES_DB` | Nombre de la base de datos | `scraper_db` |
| `POSTGRES_USER` | Usuario (viene del Secret) | — |
| `POSTGRES_PASSWORD` | Contraseña (viene del Secret) | — |

> **Compatibilidad**: Si `POSTGRES_HOST` no está definido, el scraper funciona
> exactamente igual que en los Hits anteriores (solo escribe JSON locales).

---

### Verificar el histórico acumulado entre corridas

#### Query de resumen de 7 días

```sql
SELECT
    producto,
    MIN(precio)                          AS precio_min,
    MAX(precio)                          AS precio_max,
    ROUND(AVG(precio), 2)                AS precio_avg,
    COUNT(DISTINCT DATE_TRUNC('hour', scraped_at)) AS n_corridas
FROM scrape_results
WHERE scraped_at > NOW() - INTERVAL '7 days'
GROUP BY producto
ORDER BY producto;
```

#### Ejecutar desde fuera del cluster con `kubectl exec`

```bash
kubectl exec -it $(kubectl get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}') \
  -- psql -U scraper -d scraper_db -c "
SELECT producto, MIN(precio), MAX(precio), ROUND(AVG(precio),2), COUNT(*) AS n_filas
FROM scrape_results
GROUP BY producto;"
```

---

### Correr los tests (cobertura ≥ 70 %)

```bash
cd hit8
pip install -r requirements.txt
pip install pytest pytest-cov
pytest --cov=. --cov-fail-under=70
```

### Limpiar todos los recursos de hit8

```bash
kubectl delete -f hit8/k8s/
```
