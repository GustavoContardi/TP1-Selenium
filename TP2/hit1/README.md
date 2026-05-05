# Hit #1 y Aplicación Base — Stack de Observabilidad + Scraper en Kubernetes

Este directorio contiene tanto el código de la aplicación de Scraping (estado base) como la implementación del **Hit #1** (Infraestructura de Observabilidad con Loki, Promtail y Grafana).

Para un flujo de trabajo ideal, se recomienda primero levantar el Stack de Observabilidad (Hit #1) y luego desplegar la aplicación base para que sus logs sean recolectados automáticamente por Promtail.

---

## Parte 1: Stack de Observabilidad (Hit #1)

Todo lo declarativo y reproducible para desplegar Loki, Promtail y Grafana está en la carpeta `observability/`.

### Prerrequisitos
- Clúster local de Kubernetes (ej: `k3s`, `kIND`).
- Herramientas `kubectl` configuradas y `helm` instalado.

### Despliegue del Stack

#### 1. Crear el Secret de Grafana
Antes de ejecutar el script, debes generar el archivo con las contraseñas de acceso al dashboard de Grafana.
> **NOTA**: Los archivos terminados en `-secret.yaml` están en `.gitignore` para no subir contraseñas al repositorio.

```bash
cat > observability/manifests/grafana-secret.yaml <<'EOF'
apiVersion: v1
kind: Secret
metadata:
  name: grafana-admin
  namespace: observability
type: Opaque
stringData:
  admin-user: admin
  admin-password: "grafana_admin_password_123"
EOF
```

#### 2. Ejecutar script de instalación
El script provee una instalación idempotente que levanta el namespace `observability`, aplica los manifiestos base, provisiona el dashboard as-code y despliega los componentes vía Helm.

```bash
cd observability
./install.sh
cd ..
```

### Verificación del Stack

Verifica el estado de los componentes con:
```bash
kubectl -n observability get pods
```

**Output esperado:**
```text
NAME                       READY   STATUS    RESTARTS   AGE
loki-0                     1/1     Running   0          3m
promtail-7d5fb             1/1     Running   0          3m
grafana-69b8f8c4d4-xxxxx   1/1     Running   0          2m
```

Verifica los servicios:
```bash
kubectl -n observability get svc
```

**Output esperado:**
```text
NAME       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)
grafana    NodePort    10.43.x.x       <none>        80:30000/TCP
loki       ClusterIP   10.43.x.x       <none>        3100/TCP,9095/TCP
```

### Acceso a Grafana y Validación End-to-End

1. Abre `http://<node-ip>:30000` en tu navegador.
2. Inicia sesión con el usuario `admin`.
   - La contraseña está configurada en `manifests/grafana-secret.yaml`. Si no la cambiaste, puedes obtenerla ejecutando:
     ```bash
     kubectl get secret -n observability grafana-admin -o jsonpath="{.data.admin-password}" | base64 --decode
     ```
3. Ve al menú **Explore**, selecciona el datasource **Loki** y ejecuta la query `{namespace="observability"}`. Tienen que aparecer logs del propio stack. Eso prueba que el pipeline Promtail → Loki → Grafana está cerrado end-to-end.

---

## Parte 2: Aplicación Scraper (Hit Base)

Este scraper extrae información de productos de MercadoLibre. Actualmente tiene capacidades de paginación, cálculo de estadísticas y almacenamiento persistente en PostgreSQL.

### Variables de Entorno de la Aplicación

| Variable | Descripción | Default |
|---|---|---|
| `BROWSER` | Motor a utilizar: `chrome` \| `firefox` | `chrome` |
| `HEADLESS` | Ejecución sin interfaz gráfica: `true` \| `false` | `true` |
| `MAX_PAGES` | Cantidad de páginas de MercadoLibre a iterar por cada producto | `3` |
| `PRODUCTS` | Lista de productos a buscar, separados por saltos de línea | 3 productos predefinidos |
| `POSTGRES_HOST` | Host de la BD. Si **no** está definido, se omite la escritura a PostgreSQL | — |

### Guía de Despliegue de la Aplicación en Kubernetes

#### 1. Crear el Secret con credenciales
Genera las contraseñas necesarias para que la BD de PostgreSQL se levante y el scraper se pueda conectar.
> **NOTA**: `postgres-secret.yaml` se encuentra en `.gitignore`. Nunca commitees credenciales.

```bash
cat > k8s/postgres-secret.yaml <<'EOF'
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

#### 2. Construir la imagen e importarla al cluster
Debes buildear la imagen del scraper en base al Dockerfile actual:

*(Ejemplo usando k3s)*:
```bash
docker build -t ml-scraper:latest .
docker save ml-scraper:latest -o /tmp/ml-scraper.tar
sudo k3s ctr images import /tmp/ml-scraper.tar && rm /tmp/ml-scraper.tar
```

#### 3. Aplicar manifiestos
Levantamos los recursos:

```bash
kubectl apply -f k8s/
```

Esperamos a que la base de datos PostgreSQL inicie por completo:
```bash
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s
```

> **¡Magia de la Observabilidad!** 🪄  
> Como ya desplegaste Promtail en el paso anterior, este detectará automáticamente la creación del Job del scraper y capturará sus registros. Entra a tu Grafana y podrás ver el Dashboard pre-cargado de "Scraper Overview" mostrando los logs de esta ejecución sin necesidad de usar `kubectl logs`.

Si igual quieres ver la ejecución por consola local:
```bash
kubectl logs -l job-type=one-off -c scraper -f
```

#### 4. Consultar histórico almacenado en PostgreSQL
Puedes conectarte a la BD para validar que los datos extraídos fueron procesados:
```bash
kubectl exec -it $(kubectl get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}') \
  -- psql -U scraper -d scraper_db -c \
  "SELECT producto, MIN(precio), MAX(precio), COUNT(*) FROM scrape_results GROUP BY producto;"
```

#### 5. Limpieza general
Para eliminar la aplicación del cluster:
```bash
kubectl delete -f k8s/
kubectl delete secret postgres-credentials
```
