# LogQL Cookbook — Scraper Observability

Este documento contiene una colección de consultas operativas (LogQL) que nos permiten monitorear y analizar el comportamiento de nuestro scraper usando las métricas extraídas desde los logs estructurados JSON.

---

### Q1 — Top errores por producto en las últimas 24h

**Pregunta de negocio:** “¿Qué producto está fallando más?” — Útil para priorizar bugfixes de selectores CSS.

```logql
sum by (producto) (
  count_over_time(
    {namespace="ml-scraper", app="scraper"} |~ "^{" | json | level="ERROR" [24h]
  )
)
```

**Explicación de la sintaxis:**
- `{namespace="ml-scraper", app="scraper"}`: Seleccionamos el stream correcto para reducir el costo de procesamiento.
- `|~ "^{"`: Filtra solo las líneas que empiezan con llave (JSON) ignorando el print_table final de `stats.py` para evitar errores de parseo.
- `| json`: Extrae los atributos del payload de log hacia campos queryables (`producto`, `level`, etc).
- `| level="ERROR"`: Nos quedamos únicamente con los eventos fatales.
- `count_over_time(... [24h])`: Queremos el **volumen absoluto** de la cantidad de veces que ocurrió el error a lo largo de toda la ventana, no una tasa (`rate`).
- `sum by (producto)`: Agrupa los errores a través de los múltiples pods que puedan estar ejecutando para darnos el total agrupado por el campo producto extraído del JSON.

---

### Q2 — Tasa de WARNINGs por minuto en la última hora

**Pregunta de negocio:** “¿Hubo un pico de errores de retry hace 30 min?” — Visual para detectar incidentes en curso.

```logql
sum by (producto) (
  rate({namespace="ml-scraper", app="scraper"} |~ "^{" | json | level="WARNING" [1m])
)
```

**Explicación de la sintaxis:**
- `rate(... [1m])`: A diferencia de `count_over_time`, la función `rate` calcula la cantidad de líneas por segundo en una ventana de 1 minuto.
- `sum by (producto)`: Nos permite tener diferentes series temporales en el dashboard, una para cada producto analizado, permitiendo detectar visualmente picos (spikes) de advertencias para un item en específico.

---

### Q3 — Conteo de filtros que no aparecieron por producto

**Pregunta de negocio:** “¿Qué productos pierden el filtro tienda_oficial (ML lo oculta dinámicamente)?”

```logql
sum by (producto) (
  count_over_time(
    {namespace="ml-scraper", app="scraper"}
      |~ "^{"
      | json
      | message =~ "Filtro .* no disponible"
    [7d]
  )
)
```

**Explicación de la sintaxis:**
- `=~ "Filtro .* no disponible"`: LogQL soporta filtrado por Regex de forma nativa (`=~`). En este caso lo usamos sobre el campo `message` extraído por el parser JSON, para atrapar cualquier advertencia de los múltiples campos que puedan faltar dinámicamente (`tienda_oficial`, `envio_gratis`, etc).
- Se utiliza `count_over_time` con un scope histórico bastante amplio (`[7d]`) para sumarizar incidencias raras a lo largo de una semana completa.

---

### Q4 — Duración media entre intentos de retry

**Pregunta de negocio:** “¿El backoff exponencial está disparando los tiempos como esperamos?”

```logql
avg_over_time(
  {namespace="ml-scraper", app="scraper"}
    |~ "^{"
    | json
    | message=~"intento.*backoff"
    | unwrap delay_ms
  [1h]
)
```

**Explicación de la sintaxis:**
- `| message=~"intento.*backoff"`: Filtramos solo los eventos específicos emitidos desde nuestro módulo de retry utilizando el mensaje estático correspondiente a este evento.
- `| unwrap delay_ms`: El parser JSON generó el label `delay_ms` de forma nativa en Loki, pero con `unwrap` forzamos a Loki a dejar de mirar los logs como simples eventos contables, y pasar a extraer el *valor numérico* subyacente para hacer una métrica de distribución.
- `avg_over_time`: Promedia la métrica expuesta a lo largo del periodo, permitiendo graficar cuantas décimas de segundo se tarda en promedio por cada intervalo temporal.

---

### Q5 — Última corrida exitosa por producto

**Pregunta de negocio:** “¿Hace cuánto que no scrapeo exitosamente cada producto?” — Base para una alerta.

```logql
topk(1,
  count_over_time(
    {namespace="ml-scraper", app="scraper"}
      |~ "^{"
      | json
      | level="INFO"
      | message="Scrape completado"
    [24h]
  )
) by (producto)
```

**Explicación de la sintaxis:**
- `topk(1, ...)`: En métricas LogQL, la función topk nos devuelve la(s) N serie(s) que tienen el valor más alto en el instante especificado. Cuando se utiliza sobre streams de texto, devuelve literalmente la última (más reciente) línea que cumple la condición.
- `by (producto)`: Como lo agrupamos por producto, nos garantiza 1 registro de log por cada uno de los productos de nuestro scraper. Fundamental para crear alertas de inactividad o fallos generalizados de CronJobs.
