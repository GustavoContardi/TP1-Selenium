# KQL Cookbook — Queries del Scraper en Elasticsearch

> Todas las queries usan **KQL** (Kibana Query Language), el default de Kibana 8+.
> Para cada una se incluye el equivalente Lucene como referencia.

---

## Q1 — Errores por producto en las últimas 24h

**Pregunta de negocio**: ¿Qué productos están generando errores y con qué frecuencia?

**KQL**:
```
level: "ERROR" and producto: *
```

**Equivalente Lucene**:
```
level:ERROR AND producto:*
```

**Time range**: Last 24 hours (configurado en el time picker de Discover).

**Por qué está escrita así**: `producto: *` actúa como filtro de existencia — solo incluye documentos donde el campo `producto` existe. En campos `keyword`, el wildcard `*` es resuelto eficientemente por el inverted index. En campos `text`, implica un scan más costoso pero aceptable para el volumen del scraper.

**Screenshot**: `efk/screenshots/q1-errores-por-producto.png`

---

## Q2 — Top selectores faltantes (filtros no disponibles)

**Pregunta de negocio**: ¿Qué filtros del DOM están fallando consistentemente en el scraper?

**KQL**:
```
message: "Filtro * no disponible" and producto: *
```

**Equivalente Lucene**:
```
message:"Filtro * no disponible" AND producto:*
```

**Time range**: Last 7 days.

**Por qué está escrita así**: El wildcard dentro de la frase captura variantes como "Filtro color no disponible", "Filtro precio no disponible". KQL permite wildcards dentro de valores entrecomillados a diferencia de Lucene donde el wildcard rompe la frase. En volúmenes altos el wildcard en campo `text` es costoso — para producción convendría agregar un campo `keyword` específico al log.

**Screenshot**: `efk/screenshots/q2-selectores-faltantes.png`

---

## Q3 — Distribución de duración del Job

**Pregunta de negocio**: ¿Cuánto tarda cada corrida del scraper? ¿Hay outliers?

**KQL**:
```
event: "scrape_completado" and job_duration_ms >= 0
```

**Equivalente Lucene**:
```
event:scrape_completado AND job_duration_ms:>=0
```

**Time range**: Last 7 days. Visualizar como histograma sobre `job_duration_ms`.

**Por qué está escrita así**: `job_duration_ms >= 0` filtra documentos que tengan el campo numérico (excluye los que no lo emiten). `event: "scrape_completado"` restringe a los logs de fin de ejecución donde se reporta la duración total. Los rangos numéricos en KQL van directo al BKD tree de Lucene — O(log n).

**Screenshot**: `efk/screenshots/q3-distribucion-duracion.png`

---

## Q4 — Logs con timeout de Selenium

**Pregunta de negocio**: ¿Cuántos timeouts de Selenium están ocurriendo y en qué módulos?

**KQL**:
```
message: *timeout* and (logger: "selenium*" or logger: "extractors")
```

**Equivalente Lucene**:
```
message:*timeout* AND (logger:selenium* OR logger:extractors)
```

**Time range**: Last 24 hours.

**Por qué está escrita así**: `*timeout*` es un leading wildcard — el más costoso en Elasticsearch porque no puede usar el inverted index directamente y requiere un scan sobre los terms del campo. Aceptable para este volumen. En producción con millones de docs/día, conviene indexar un campo booleano `has_timeout` en el pipeline de Fluent Bit. El filtro por `logger` restringe a los módulos relevantes y reduce el scan.

**Screenshot**: `efk/screenshots/q4-timeouts-selenium.png`

---

## Q5 — Eventos de un CronJob específico (correlación por job_name)

**Pregunta de negocio**: ¿Qué pasó en una corrida específica del scraper?

**KQL**:
```
kubernetes.labels.job_name: "scraper-efk-test-1"
```

**Equivalente Lucene**:
```
kubernetes.labels.job_name:scraper\-efk\-test\-1
```

**Time range**: All time (o el rango donde se ejecutó el job).

**Por qué está escrita así**: `kubernetes.labels.job_name` es un campo `keyword` inyectado por el filtro `kubernetes` de Fluent Bit. La búsqueda exacta sobre keyword es O(1) en el inverted index — la query más rápida posible. En Lucene los guiones necesitan escape (`\-`) porque son operadores; KQL los maneja sin escape dentro de comillas.

**Screenshot**: `efk/screenshots/q5-cronjob-especifico.png`

---

## Q6 — Errores excluyendo false positives de Postgres

**Pregunta de negocio**: ¿Cuántos errores reales hay si excluimos los del módulo de conexión a Postgres (reconexiones esperadas)?

**KQL**:
```
level: "ERROR" and not logger: "psycopg*"
```

**Equivalente Lucene**:
```
level:ERROR AND NOT logger:psycopg*
```

**Time range**: Last 24 hours.

**Por qué está escrita así**: `not` en KQL es un operador de exclusión limpio. El wildcard `psycopg*` es un trailing wildcard — eficiente porque el inverted index almacena terms ordenados y puede hacer prefix scan. Esto filtra tanto `psycopg2` como `psycopg` o cualquier sublogger. En producción, si los false positives son conocidos y estables, conviene filtrarlos en el pipeline de Fluent Bit con un `[FILTER] grep Exclude` para no indexarlos.

**Screenshot**: `efk/screenshots/q6-errores-sin-postgres.png`
