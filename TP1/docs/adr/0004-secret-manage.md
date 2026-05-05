# 0004. Gestión de Secretos en Hit #8 (PostgreSQL)

## Estado

Aceptado

## Contexto

Con la introducción de PostgreSQL en el Hit #8 para el almacenamiento histórico, surgió la necesidad de manejar credenciales sensibles (usuario, contraseña y nombre de la base de datos). Estos datos no deben ser expuestos en el código fuente ni en el historial de Git por motivos de seguridad.

El problema principal es cómo proveer estas credenciales tanto al despliegue de la base de datos como al Scraper que corre dentro de Kubernetes, manteniendo la confidencialidad.

## Decisión

Se adopta el uso de **Kubernetes Secrets** para la gestión de credenciales, siguiendo estas directrices:

1.  **Desacoplamiento**: Las credenciales se definen en un manifiesto `postgres-secret.yaml` de tipo `Opaque`.
2.  **Seguridad en Git**: El archivo `hit8/k8s/postgres-secret.yaml` se ha agregado al archivo `.gitignore` para prevenir su subida accidental al repositorio.
3.  **Inyección por Entorno**: Tanto el `StatefulSet` de Postgres como el `Job`/`CronJob` del Scraper consumen estos secretos y los inyectan como variables de entorno (`POSTGRES_USER`, `POSTGRES_PASSWORD`, etc.).
4.  **Validación con Gitleaks**: Se integra `gitleaks` en los hooks de pre-commit como una capa adicional de seguridad para detectar si algún secreto llegara a filtrarse en otros archivos.

Para entornos de CI/CD (GitHub Actions), los secretos deben ser inyectados mediante "GitHub Secrets" en lugar de utilizar archivos físicos.

## Consecuencias

### Positivas
- **Seguridad**: Las credenciales sensibles no residen en el repositorio.
- **Flexibilidad**: Permite cambiar las contraseñas sin necesidad de recompilar la imagen de Docker o modificar el código del Scraper.
- **Estándar**: Sigue las mejores prácticas de Kubernetes para el manejo de información sensible.

### Negativas
- **Configuración Manual**: Requiere un paso adicional de configuración manual para el desarrollador (crear el Secret localmente antes de aplicar los manifiestos).
- **Riesgo de Pérdida**: Al no estar en Git, si no hay un backup de la configuración de CI o del manifiesto local, las credenciales deben ser regeneradas.
