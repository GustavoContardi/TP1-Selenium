# Hit #8 — Kubernetes con PostgreSQL y Estadísticas Avanzadas

Este último Hit extiende el despliegue en Kubernetes agregando capacidades de persistencia en una base de datos **PostgreSQL**, así como lógica avanzada para paginar resultados y calcular estadísticas de los productos extraídos.

## Nuevas capacidades

| Capacidad | Descripción |
|---|---|
| **Paginación** | Extrae hasta 30 resultados por producto (por defecto navegando 3 páginas). |
| **Estadísticas** | Genera una tabla de min/max/mediana/promedio/desvío que se imprime en consola (`stdout`) y se exporta a `output/stats.json`. |
| **Histórico** | Almacena y acumula los resultados extraídos por las corridas del CronJob directamente en una base de datos PostgreSQL en el cluster. |

## Variables de entorno soportadas

El scraper acepta configuración mediante variables de entorno (definidas en los manifiestos `.yaml` de Kubernetes o pasadas directamente localmente):

| Variable | Descripción | Default |
|---|---|---|
| `BROWSER` | Motor a utilizar: `chrome` \| `firefox` | `chrome` |
| `HEADLESS` | Ejecución sin interfaz gráfica: `true` \| `false` | `true` |
| `MAX_PAGES` | Cantidad de páginas de MercadoLibre a iterar por cada producto | `3` |
| `PRODUCTS` | Lista de productos a buscar, separados por saltos de línea | 3 productos predefinidos |
| `POSTGRES_HOST` | Host de la BD. Si **no** está definido, se omite la escritura a PostgreSQL | — |

---

## Guía de Despliegue en Kubernetes

### 1. Crear el Secret con credenciales

Para que la BD de PostgreSQL se levante correctamente y el scraper se pueda conectar, necesitas crear un **Secret** de Kubernetes con las credenciales.
> **NOTA**: El archivo `postgres-secret.yaml` se encuentra en `.gitignore` intencionalmente. Nunca debes commitear contraseñas reales.

Ejecuta el siguiente bloque para generarlo localmente:

```bash
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
  POSTGRES_PASSWORD: mimagnificapassword
EOF
```
*(Puedes reemplazar `mimagnificapassword` por la que desees)*

### 2. Construir la imagen e importarla al cluster

Construimos la imagen en base al Dockerfile de la carpeta actual y la importamos.

*(Ejemplo usando k3s)*:
```bash
docker build -t ml-scraper:latest hit8/
docker save ml-scraper:latest -o /tmp/ml-scraper.tar
sudo k3s ctr images import /tmp/ml-scraper.tar && rm /tmp/ml-scraper.tar
```
*(Si usas k3d, haz `k3d image import ml-scraper:latest -c <tu-cluster>`)*

### 3. Aplicar manifiestos y esperar a que la BD esté lista

Desplegamos el servicio, el deployment de Postgres, el Secret y los Jobs:

```bash
kubectl apply -f hit8/k8s/
```

Esperamos a que la base de datos PostgreSQL se levante por completo:

```bash
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s
```

Una vez que la BD esté lista, podemos ver la ejecución del scraper. Para evitar warnings de Kubernetes sobre múltiples contenedores, especificamos `-c scraper`:

```bash
kubectl logs -l job-type=one-off -c scraper -f
```

### 4. Consultar histórico almacenado en PostgreSQL

Si el job finalizó exitosamente, puedes conectarte directamente a la base de datos dentro del Pod de Postgres y correr una query SQL de prueba para verificar los datos cacheados:

```bash
kubectl exec -it $(kubectl get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}') \
  -- psql -U scraper -d scraper_db -c \
  "SELECT producto, MIN(precio), MAX(precio), COUNT(*) FROM scrape_results GROUP BY producto;"
```

### 5. Limpieza general

Para eliminar todos los recursos asociados de tu cluster, no olvides borrar los manifiestos creados y el secret generado:

```bash
kubectl delete -f hit8/k8s/
kubectl delete secret postgres-credentials
```
