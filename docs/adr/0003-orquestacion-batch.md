# 0003 — Kubernetes Job/CronJob para orquestación batch

- **Date:** 2026-05-01
- **Status:** Accepted
- **Deciders:** Mateo y equipo

## Contexto

El scraper necesita ejecutarse periódicamente (cada hora) y también de forma one-off.
Alternativas evaluadas:
- `docker-compose` + cron del host: simple pero atado a una máquina, sin retry nativo, sin historial.
- Deployment con sidecar cron: sobreingeniería para un workload batch, el Pod correría idle entre ejecuciones.
- Kubernetes Job + CronJob: retry nativo via backoffLimit, historial de ejecuciones, PVC compartido, integrable con CI.

## Decisión

Usamos `batch/v1.Job` para ejecuciones one-off y `batch/v1.CronJob` para el schedule horario.
`concurrencyPolicy: Forbid` previene escrituras simultáneas al PVC ReadWriteOnce.

## Consecuencias

- Más fácil: retry a nivel de infraestructura independiente del código, observabilidad con `kubectl logs`, schedule declarativo.
- Más difícil: requiere cluster k3s/k3d local, imagen importada manualmente al cluster.
- Riesgo: si el scraping tarda más de 1 hora, `concurrencyPolicy: Forbid` omite la siguiente corrida. Mitigado con `activeDeadlineSeconds: 600`.
