# Hit #3 — Filtros vía DOM y screenshot

Extiende el scraper del Hit #2 aplicando filtros sobre la página de resultados mediante interacción con el DOM (clicks reales, sin modificar la URL). Captura una screenshot del estado filtrado.

## Filtros aplicados

1. **Condición**: `Nuevo`
2. **Tienda oficial**: `Sí`
3. **Ordenar por**: `Más relevantes`

## Requisitos previos

- Python 3.10 o superior
- Google Chrome instalado en el sistema
- Mozilla Firefox instalado en el sistema
- Selenium 4.6 o superior

## Instalación

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r hit3/requeriments.txt
```

## Ejecución

```bash
BROWSER=chrome python hit3/scraper.py
BROWSER=firefox python hit3/scraper.py

# Modo headless
HEADLESS=true BROWSER=chrome python hit3/scraper.py
```

## Salida esperada

- Lista de los primeros 5 títulos filtrados por consola.
- Archivo de imagen en `hit3/screenshots/<producto>_<browser>.png`.

Ejemplo:
```
1. <título producto filtrado 1>
...
5. <título producto filtrado 5>
Screenshot: screenshots/bicicleta_rodado_29_chrome.png
```

## Decisiones de diseño

- **Interacción real con el DOM**: cada filtro se aplica buscando el link o checkbox correspondiente en el sidebar y disparando `click()`. No se modifica la URL ni se usa la API interna del sitio.
- **Localización por texto visible**: los filtros se ubican con XPath sobre `normalize-space()` del texto del link (`Nuevo`, `Sí`). Es resiliente a cambios de clases CSS pero sensible al idioma del sitio.
- **Scroll programático antes del click**: `scrollIntoView({block:'center'})` evita errores `ElementClickInterceptedException` cuando un filtro queda fuera del viewport.
- **Re-espera tras cada filtro**: después de cada click se espera nuevamente la presencia de items en la grilla; MercadoLibre re-renderiza los resultados de forma asíncrona.
- **Ordenamiento por dropdown**: `Más relevantes` se selecciona abriendo el `andes-dropdown__trigger` y haciendo click sobre la opción dentro de la lista emergente.
- **Screenshot tras estabilización**: `driver.save_screenshot()` se ejecuta solo después de que la grilla volvió a renderizar con el último filtro aplicado.
- **Slug del nombre de producto**: el nombre de archivo de la screenshot se normaliza (minúsculas, espacios y caracteres no alfanuméricos a `_`) para evitar problemas de path.

## Diferencias observadas Chrome vs Firefox

- **Velocidad de re-render**: Firefox tarda ligeramente más entre filtro y filtro; el `WebDriverWait` con timeout de 20 s absorbe la diferencia.
- **Captura de screenshot**: ambos browsers entregan PNG con el viewport visible. Para captura full-page se requeriría lógica adicional (no exigida por la consigna).

## Limitaciones conocidas

- Si el grupo de filtro `Tienda oficial` aparece colapsado, requiere expandirlo previamente. El script incluye lógica para detectar el caso, pero ante cambios de UI puede necesitar ajuste.
- Selectores acoplados al idioma `es-AR`. Cambios de localización romperían las búsquedas por texto.
- No hay reintentos ante fallos transitorios; eso se aborda en el Hit #5.