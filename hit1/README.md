# Hit #1 — Scraper básico de MercadoLibre con Chrome

Script que abre Chrome, navega a `mercadolibre.com.ar`, busca el producto `bicicleta rodado 29` e imprime por consola el título de los primeros 5 resultados.

## Requisitos previos

- Python 3.10 o superior
- Google Chrome instalado en el sistema
- Selenium 4.6 o superior (incluye Selenium Manager, descarga `chromedriver` automáticamente)

## Instalación

Desde la raíz del proyecto (`TP1-Selenium/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r hit1/requeriments.txt
```

## Ejecución

Con el entorno virtual activo:

```bash
python hit1/scraper.py
```

## Salida esperada

Se abre una ventana de Chrome, se realiza la búsqueda y por consola se imprime el progreso detallado:

```text
2023-10-27 10:30:00 [INFO] - Iniciando el scraper...
2023-10-27 10:30:01 [INFO] - Navegando a la URL: https://www.mercadolibre.com.ar
2023-10-27 10:30:03 [INFO] - Ingresando búsqueda: 'bicicleta rodado 29'
2023-10-27 10:30:04 [INFO] - Esperando que carguen los resultados...
2023-10-27 10:30:05 [INFO] - Extrayendo los primeros 5 resultados...
2023-10-27 10:30:05 [INFO] - Resultado 1: <título producto 1>
2023-10-27 10:30:05 [INFO] - Resultado 2: <título producto 2>
2023-10-27 10:30:05 [INFO] - Resultado 3: <título producto 3>
2023-10-27 10:30:05 [INFO] - Resultado 4: <título producto 4>
2023-10-27 10:30:05 [INFO] - Resultado 5: <título producto 5>
2023-10-27 10:30:05 [INFO] - Cerrando el navegador...
2023-10-27 10:30:06 [INFO] - Scraper finalizado exitosamente.
```

## Decisiones de diseño

- **Trazabilidad (Logging)**: Se usa la librería estándar `logging` para registrar eventos (`INFO`), advertencias (`WARNING`) y errores (`ERROR`), permitiendo un seguimiento del flujo de ejecución y captura de stack traces.
- **Sincronización con explicit waits**: `WebDriverWait` + `expected_conditions.element_to_be_clickable` y `presence_of_element_located`. No se usa `time.sleep()`.
- **Timeout global**: 15 segundos. Suficiente para conexiones estándar y carga del SPA de MercadoLibre.
- **Selector del input de búsqueda**: `By.NAME, "as_word"`. Estable entre cambios de UI; identifica el campo del formulario de búsqueda.
- **Selector de resultados**: `ol.ui-search-layout li.ui-search-layout__item`. Es el contenedor canónico de la grilla de resultados; los hijos `a.poly-component__title` contienen el título de cada producto.
- **Cierre garantizado del driver**: bloque `try/finally` con `driver.quit()` para liberar recursos aun ante excepciones.
- **Selenium Manager**: a partir de Selenium 4.6 no requiere `webdriver-manager` ni descarga manual del driver.

## Limitaciones conocidas

- El DOM de MercadoLibre puede cambiar y romper los selectores. Verificar con DevTools antes de ejecutar.
- Si aparece un modal de cookies o región que tape el input, el script puede fallar. No se maneja en este Hit.