import json

dashboard = {
    "title": "Scraper Overview",
    "uid": "scraper-overview-hit5",
    "schemaVersion": 39,
    "time": {"from": "now-6h", "to": "now"},
    "refresh": "10s",
    "panels": []
}

# 1. Total Scrapes Hoy (Stat)
dashboard["panels"].append({
    "id": 1, "gridPos": {"x": 0, "y": 0, "w": 8, "h": 6}, "type": "stat",
    "title": "Total de Scrapes (24h)",
    "targets": [{
        "expr": "sum(count_over_time({namespace=\"ml-scraper\", app=\"scraper\"} |~ \"^{\" | json | level=\"INFO\" | message=\"Scrape completado\" [24h]))",
        "refId": "A", "datasource": {"type": "loki", "uid": "Loki"}
    }]
})

# 2. Productos con más errores en 24h (Stat - Top Q1)
dashboard["panels"].append({
    "id": 2, "gridPos": {"x": 8, "y": 0, "w": 8, "h": 6}, "type": "stat",
    "title": "Top Errores por Producto (24h) - Q1",
    "targets": [{
        "expr": "sum by (producto) (count_over_time({namespace=\"ml-scraper\", app=\"scraper\"} |~ \"^{\" | json | level=\"ERROR\" [24h]))",
        "refId": "A", "datasource": {"type": "loki", "uid": "Loki"}
    }],
    "options": {"reduceOptions": {"calcs": ["lastNotNull"]}}
})

# 3. % de Éxito (Stat)
dashboard["panels"].append({
    "id": 3, "gridPos": {"x": 16, "y": 0, "w": 8, "h": 6}, "type": "stat",
    "title": "% de Éxito (24h)",
    "targets": [{
        "expr": "(sum(count_over_time({namespace=\"ml-scraper\", app=\"scraper\"} |~ \"^{\" | json | event=\"product_success\" [24h])) / sum(count_over_time({namespace=\"ml-scraper\", app=\"scraper\"} |~ \"^{\" | json | event=~\"product_success|product_error\" [24h]))) * 100",
        "refId": "A", "datasource": {"type": "loki", "uid": "Loki"}
    }],
    "options": {"reduceOptions": {"calcs": ["lastNotNull"]}}
})

# 4. Q3: Filtros no disponibles (Time Series)
dashboard["panels"].append({
    "id": 4, "gridPos": {"x": 0, "y": 6, "w": 12, "h": 8}, "type": "timeseries",
    "title": "Filtros Faltantes por Producto (7d) - Q3",
    "targets": [{
        "expr": "sum by (producto) (count_over_time({namespace=\"ml-scraper\", app=\"scraper\"} |~ \"^{\" | json | message =~ \"Filtro .* no disponible\" [7d]))",
        "refId": "A", "datasource": {"type": "loki", "uid": "Loki"}
    }]
})

# 5. Q2: Tasa de Advertencias (Time Series)
dashboard["panels"].append({
    "id": 5, "gridPos": {"x": 12, "y": 6, "w": 12, "h": 8}, "type": "timeseries",
    "title": "Tasa de Advertencias por Min (1h) - Q2",
    "targets": [{
        "expr": "sum by (producto) (rate({namespace=\"ml-scraper\", app=\"scraper\"} |~ \"^{\" | json | level=\"WARNING\" [1m]))",
        "refId": "A", "datasource": {"type": "loki", "uid": "Loki"}
    }]
})

# 6. Q5: Última corrida exitosa (Table)
dashboard["panels"].append({
    "id": 6, "gridPos": {"x": 0, "y": 14, "w": 12, "h": 8}, "type": "table",
    "title": "Última Corrida Exitosa (TopK) - Q5",
    "targets": [{
        "expr": "topk(1, count_over_time({namespace=\"ml-scraper\", app=\"scraper\"} |~ \"^{\" | json | level=\"INFO\" | message=\"Scrape completado\" [24h])) by (producto)",
        "refId": "A", "datasource": {"type": "loki", "uid": "Loki"}
    }]
})

# 7. Q1: Top Errores (Table)
dashboard["panels"].append({
    "id": 7, "gridPos": {"x": 12, "y": 14, "w": 12, "h": 8}, "type": "table",
    "title": "Conteo de Errores por Producto - Q1",
    "targets": [{
        "expr": "sum by (producto) (count_over_time({namespace=\"ml-scraper\", app=\"scraper\"} |~ \"^{\" | json | level=\"ERROR\" [24h]))",
        "refId": "A", "datasource": {"type": "loki", "uid": "Loki"}
    }]
})

with open("hit5/observability/dashboards/scraper-overview.json", "w") as f:
    json.dump(dashboard, f, indent=2)

