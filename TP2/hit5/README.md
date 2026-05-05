# Hit #5 — Dashboard Grafana Provisionado As-Code

Este directorio contiene la aplicación de Scraping y la configuración final de Observabilidad que provee automáticamente un Dashboard pre-construido de Grafana que responde visualmente a todas las consultas LogQL operativas.

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

> **Aviso Hit #5**: El archivo `observability/dashboards/scraper-overview.json` ya contiene el Dashboard definitivo. El script `install.sh` se encarga de crear el `ConfigMap` requerido, y `grafana-values.yaml` lo monta automáticamente dentro del contenedor para que Grafana lo lea ("Dashboard Provisioning as-code").

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
> **IMPORTANTE HIT #4**: Modificamos el código interno de la aplicación (`extractors.py`, `retry.py` y `scraper.py`) para que los logs emitidos coincidan milimétricamente con el string-matching pedido en la consigna (`delay_ms`, `"Filtro .* no disponible"`, `"intento de backoff"`, `"Scrape completado"`). **¡Debes recompilar la imagen para que impacten!**

*(Ejemplo usando k3s)*:
```bash
docker build -t ml-scraper:latest .
docker save ml-scraper:latest -o /tmp/ml-scraper.tar
sudo k3s ctr images import /tmp/ml-scraper.tar && rm /tmp/ml-scraper.tar
```

#### 3. Aplicar manifiestos en el namespace ml-scraper
Levantamos los recursos indicando que deben ir al namespace exclusivo de la aplicación:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/ -n ml-scraper
```

Esperamos a que la base de datos PostgreSQL inicie por completo:
```bash
kubectl wait --for=condition=ready pod -l app=postgres -n ml-scraper --timeout=120s
```

#### 4. Disparar tráfico y validar labels en Grafana
Creamos un Job manual para que Promtail lo capture:
```bash
kubectl -n ml-scraper create job --from=cronjob/scraper-hourly scraper-test-1
kubectl -n ml-scraper wait --for=condition=complete job/scraper-test-1 --timeout=600s
```

Ve a **Grafana → Explore → Loki**, y prueba esta query para parsear automáticamente el JSON:
```logql
{namespace="ml-scraper", app="scraper"} |~ "^{" | json
```

#### 📸 Consigna obligatoria (Hit #5): Dashboard As-Code
Una vez que hayas aplicado el Job manual (`scraper-test-1`), dirígete a Grafana:
1. Menú izquierdo -> **Dashboards**.
2. Entra a la carpeta **SIP 2026**.
3. Abre el panel **Scraper Overview**.

Ahí vas a ver un Dashboard súper completo con:
- **Stat panels**: Total de scrapes, top errores, y tasa de advertencias.
- **Time series**: Gráficas de las advertencias dinámicas y de la duración del backoff (Hit 4).
- **Tables**: Listado directo de los top errores y las últimas corridas.

**Tomale una captura a TODO este Dashboard funcionando** y guardala en `observability/screenshots/hit5-dashboard.png`.

![Hit 5 Dashboard](observability/screenshots/hit5-dashboard.png)

Si igual quieres ver la ejecución por consola local:
```bash
kubectl logs -n ml-scraper -l job-type=one-off -c scraper -f
```

#### 5. Consultar histórico almacenado en PostgreSQL
Puedes conectarte a la BD para validar que los datos extraídos fueron procesados:
```bash
kubectl exec -n ml-scraper -it $(kubectl get pod -n ml-scraper -l app=postgres -o jsonpath='{.items[0].metadata.name}') \
  -- psql -U scraper -d scraper_db -c \
  "SELECT producto, MIN(precio), MAX(precio), COUNT(*) FROM scrape_results GROUP BY producto;"
```

#### 6. Limpieza general
Para eliminar la aplicación del cluster:
```bash
kubectl delete namespace ml-scraper
```
