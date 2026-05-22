# Guía de Validación - Hit #2 (Pipeline de OpenTelemetry)

Esta guía detalla el funcionamiento del pipeline del colector desplegado para el Hit #2, cómo validar que esté capturando y procesando logs correctamente, y soluciones a problemas comunes.

## Funcionamiento del Pipeline

El pipeline configurado en `manifests/collector-agent.yaml` realiza el siguiente flujo de observabilidad local:

```text
[var/log/pods] ──> [filelog receiver] ──> [k8sattributes] ──> [attributes] ──> [debug exporter (stdout)]
```

1. **Recepción (`filelog`)**: Lee en tiempo real todos los logs generados por los contenedores del scraper en el path `/var/log/pods/ml-scraper_*/*/*.log`.
2. **Procesamiento y Enriquecimiento**:
   - **`k8sattributes`**: Consulta la API de Kubernetes para inyectar metadatos asociados al Pod que originó el log (Namespace, Nombre del Pod, UID, Job/CronJob que lo disparó, Nodo, etc.).
   - **`attributes`**: Inserta el atributo estándar `service` mapeando el valor desde la etiqueta `app` para lograr compatibilidad vendor-neutral.
3. **Exportación (`debug`)**: Vuelca la señal formateada en detalle a la salida estándar (`stdout`) del colector.

---

## Cómo interpretar el output del debug exporter

Al ejecutar `kubectl -n otel logs ds/agent-collector`, el exportador de depuración (debug) mostrará estructuras en formato de árbol que detallan la metadata y el cuerpo del log.

### Ejemplo de Log Enriquecido con Éxito:

```text
ResourceLog #0
Resource SchemaURL: https://opentelemetry.io/schemas/1.26.0
Resource attributes:
     -> host.name: Str(k3s-node-1)
     -> k8s.namespace.name: Str(ml-scraper)
     -> k8s.pod.name: Str(scraper-otel-test-1-abcde)
     -> k8s.pod.uid: Str(42bac3e5-44c3-4f80-a0c2-78538e23d495)
     -> k8s.cronjob.name: Str(scraper-hourly)
     -> k8s.job.name: Str(scraper-otel-test-1)
     -> service: Str(scraper)
ScopeLogs #0
ScopeLogs SchemaURL: 
InstrumentationScope 
LogRecord #0
ObservedTimestamp: 2026-05-22 18:52:08.513 +0000 UTC
Timestamp: 2026-05-22 18:52:08.512 +0000 UTC
SeverityText: INFO
SeverityNumber: Info(9)
Body: Str({"message": "Iniciando scraping de productos...", "level": "info", "logger": "scraper"})
Attributes:
     -> log.file.path: Str(/var/log/pods/ml-scraper_scraper-otel-test-1-abcde_42bac3e5-44c3-4f80-a0c2-78538e23d495/postgres/0.log)
```

**Puntos clave a validar en la salida:**
- **`Resource attributes`**: Debe contener obligatoriamente `k8s.namespace.name: ml-scraper`, `k8s.pod.name`, y `k8s.cronjob.name`.
- **`service`**: Debe contener el valor `scraper`.
- **`Body`**: Debe contener el mensaje estructurado de la aplicación (en este caso, el JSON del logger del scraper).

---

## Troubleshooting Común (Resolución de Problemas)

### 1. No aparecen logs (`ResourceLog` está vacío o no imprime nada)
- **Causa**: El path del archivo de logs no coincide o no hay contenedores activos escribiendo logs.
- **Solución**:
  - Asegúrate de que disparaste tráfico de prueba creando un job:
    ```bash
    kubectl -n ml-scraper create job --from=cronjob/scraper-hourly scraper-otel-test-1
    ```
  - Comprueba que el Pod se ejecutó e imprimió logs en su consola:
    ```bash
    kubectl -n ml-scraper logs -l job-name=scraper-otel-test-1
    ```
  - Verifica que los archivos físicos existan en el nodo del cluster:
    ```bash
    ls -la /var/log/pods/ml-scraper_*
    ```

### 2. Los logs aparecen en el colector pero NO tienen los atributos `k8s.*`
- **Causa**: El procesador `k8sattributes` no puede asociar el log con el pod debido a problemas de RBAC o porque la asociación de IPs de red no está funcionando.
- **Solución**:
  - Verifica que los permisos ClusterRole definidos en `manifests/rbac.yaml` estén aplicados:
    ```bash
    kubectl get clusterrolebinding otel-collector
    ```
  - Asegúrate de que el colector esté corriendo con la ServiceAccount `otel-collector` (verifica `serviceAccount` en el pod del colector).
  - Revisa que en el pipeline de `k8sattributes` esté habilitado `pod_association` por `k8s.pod.uid` y `connection`.

### 3. El colector falla al arrancar o se queda en CrashLoopBackOff
- **Causa**: Generalmente es un error sintáctico en el YAML de configuración o se está usando la imagen oficial "core" de OpenTelemetry, la cual no incluye los receptores y procesadores avanzados de contrib.
- **Solución**:
  - Confirma que estás usando la versión `contrib` en `collector-agent.yaml`:
    ```yaml
    image: otel/opentelemetry-collector-contrib:0.110.0
    ```
  - Revisa la sintaxis del YAML y verifica los logs del contenedor del colector buscando errores de parsing:
    ```bash
    kubectl -n otel logs ds/agent-collector --tail=100
    ```
