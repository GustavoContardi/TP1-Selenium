# 0009 — Evaluación de EFK como segundo stack de logging

- Date: 2026-05-05
- Status: Proposed (cierre formal en ADR 0010 de Parte 4)
- Deciders: Gustavo

## Contexto

En Parte 1 adoptamos Loki + Promtail + Grafana (namespace `observability`) como stack de logging centralizado. El modelo label-first de Loki resuelve queries operacionales (errores por producto, logs por namespace) de forma eficiente y con bajo footprint (~0.5-0.8 GiB de RAM total).

Sin embargo, Loki tiene una limitación estructural: las queries full-text (buscar una substring arbitraria en el cuerpo del log) requieren un grep lineal sobre todos los chunks del stream. Para volúmenes bajos como el scraper esto tarda segundos, pero escala linealmente con el volumen de datos.

Elasticsearch construye un inverted index sobre el contenido completo del log. La misma query full-text es O(log n) independientemente del volumen. El costo es RAM, disco y complejidad operativa.

En Parte 2 desplegamos EFK (Elasticsearch + Fluent Bit + Kibana) en paralelo (namespace `elastic`) con dos objetivos:

1. Obtener datos comparativos reales sobre el mismo workload (scraper).
2. Entender los trade-offs antes de cerrar la decisión final en Parte 4 con OTel.

### Restricciones

- Cluster k3s single-node, ~8 GB RAM totales (con Loki y EFK simultáneos: ~3.5 GiB).
- Mismos logs JSON del scraper van a ambos stacks (Promtail → Loki, Fluent Bit → ES).
- Retención 7 días en ambos (ILM en ES, `retention_period` en Loki).
- Licenciamiento: Loki es Apache 2.0; Elasticsearch es Elastic License v2 (source-available, NO OSS según OSI). En contexto académico no afecta. En empresa puede ser bloqueante si se pretende ofrecer el servicio a terceros.

## Decisión

NO se decide reemplazar Loki por EFK ni viceversa en esta Parte 2. La decisión se difiere al ADR 0010 (Parte 4) cuando se haya evaluado también OTel.

Lo que sí se decide:

- Mantener los dos stacks corriendo en paralelo durante el TP.
- Documentar las dimensiones de comparación con datos reales del cluster.
- Marcar EFK como candidato fuerte cuando el caso de uso requiera full-text search pesado.
- Marcar EFK como candidato descartado cuando el footprint o la licencia importen.

## Consecuencias

### Positivas

- Se gana visibilidad real sobre los trade-offs (datos del propio cluster, no opinión).
- Se gana experiencia con ECK Operator + ILM + KQL — útil aunque no se adopte EFK como stack principal.
- Los dos stacks leen los mismos logs, lo que permite comparación directa de latencia y ergonomía.

### Negativas

- Se consume ~3.5 GiB de RAM adicional durante el desarrollo. Mitigado bajando uno de los dos stacks durante coding y subiendo ambos para evaluación final.
- Se introduce dependencia de Elastic License v2 en el repo. Mitigado: solo se usan imágenes oficiales, no se redistribuye Elasticsearch ni se ofrece como servicio.
- Mayor complejidad operativa: dos pipelines de logging, dos UIs de visualización, dos políticas de retención.

## Métricas medidas (en NUESTRO cluster)

> Completar con datos reales después de ejecutar el stack.

| Dimensión | Loki + Promtail + Grafana | EFK (ES + Fluent Bit + Kibana) |
|---|---|---|
| RAM total stack | `<medir>` Mi | `<medir>` Mi |
| Ratio RAM | 1× | `<calcular>`× |
| Disco 7 días | `<medir>` Mi | `<medir>` Mi |
| Latency Q1 (errores por producto 24h) | `<medir>` ms | `<medir>` ms |
| Latency full-text substring 50 chars | `<medir>` seg | `<medir>` ms |

## Alternativa OSS considerada

Si la licencia ELv2 fuera bloqueante en un contexto empresarial, la alternativa directa es **OpenSearch + OpenSearch Dashboards** (fork AWS, Apache 2.0). OpenSearch es API-compatible con Elasticsearch 7.10 y cubre el mismo caso de uso de inverted index. Los dashboards divergen de Kibana a partir de la versión 7.10, pero la funcionalidad core (Discover, visualizaciones, alerting) es equivalente.

Para este TP se eligió Elasticsearch sobre OpenSearch porque:

1. ECK Operator es más maduro para Kubernetes (OpenSearch tiene su propio operator pero con menor adopción).
2. La cátedra especificó versiones 8.17.x que solo existen en el branch Elastic.
3. El objetivo pedagógico incluye entender la implicancia de la licencia ELv2, lo cual requiere usar el producto original.

## Referencias

- Tabla comparativa de la cátedra: TP 2 · Parte 2 / Material de apoyo
- Elastic License v2: https://www.elastic.co/licensing/elastic-license
- OpenSearch (alternativa OSS): https://opensearch.org/
- OSI — por qué ELv2 no es OSS: https://opensource.org/licenses
