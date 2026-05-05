# LogQL Cookbook

Este documento agrupa las consultas principales (LogQL) solicitadas para el **Hit #4**. 
Aquí documentaremos las +5 queries una vez estén definidos y procesados los logs del scraper.

---

### Query 1: Errores del Scraper en la última hora
Busca cualquier registro que contenga nivel de error proveniente de los pods del scraper.
```logql
{namespace="default", pod=~"scraper-.*"} |= "ERROR"
```

### Query 2: Volumen de procesados (Placeholder)
Contar la cantidad de ítems procesados por minuto.
```logql
sum by (pod) (rate({namespace="default", pod=~"scraper-.*"} |= "item processed" [1m]))
```

*(El resto de las queries se documentarán durante el desarrollo del Hit #4...)*
