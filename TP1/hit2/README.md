# Hit #2 — Browser Factory (Chrome y Firefox)

Refactor del Hit #1 que introduce una **Browser Factory**: un módulo que recibe el nombre del navegador (`chrome` o `firefox`) y devuelve una instancia de `WebDriver` configurada. El navegador se selecciona por argumento de línea de comandos o por variable de entorno.

## Requisitos previos

- Python 3.10 o superior
- Google Chrome instalado en el sistema
- Mozilla Firefox instalado en el sistema
- Selenium 4.6 o superior (Selenium Manager descarga `chromedriver` y `geckodriver` automáticamente)

## Instalación

Desde la raíz del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r hit2/requirements.txt
```

## Ejecución

Con el entorno virtual activo, desde la raíz o desde `hit2/`:

```bash
# Por variable de entorno
BROWSER=chrome python hit2/scraper.py
BROWSER=firefox python hit2/scraper.py

# Por argumento de línea de comandos
python hit2/scraper.py chrome
python hit2/scraper.py firefox

# Modo headless (no abre ventana)
HEADLESS=true BROWSER=firefox python hit2/scraper.py
```

Si no se especifica nada, se usa `chrome` por defecto.

## Salida esperada

```
1. <título producto 1>
2. <título producto 2>
3. <título producto 3>
4. <título producto 4>
5. <título producto 5>
```

El comportamiento debe ser idéntico contra ambos navegadores.

## Decisiones de diseño

- **Browser Factory** (`browser_factory.py`): aísla la configuración de cada driver en una función `build_driver(name)`. El resto del código depende solo de la interfaz `WebDriver`, no del browser concreto.
- **Resolución del browser**: precedencia argumento CLI → variable de entorno `BROWSER` → default `chrome`.
- **Modo headless por variable de entorno**: `HEADLESS=true` activa headless en ambos browsers (`--headless=new` en Chrome, `-headless` en Firefox).
- **Tamaño de ventana fijo (1440x900)**: garantiza que los selectores responsivos se comporten igual entre ejecuciones y entre browsers.
- **Selectores compartidos**: los mismos selectores funcionan en ambos browsers; se usan CSS estándar y atributos estables (`name="as_word"`, clases `ui-search-layout`).

## Diferencias observadas Chrome vs Firefox

- **Velocidad de arranque**: Firefox tarda algo más en inicializar el primer driver tras instalación.
- **Headless**: Chrome usa `--headless=new`; Firefox usa `-headless` (un solo guion).
- **Comportamiento del input**: en Firefox el `send_keys` puede llegar antes de que el campo enfoque; el `element_to_be_clickable` resuelve ese caso.
- **Selectores**: en este Hit no se observaron diferencias; ambos resuelven la misma estructura DOM.

## Limitaciones conocidas

- Requiere ambos browsers instalados localmente para probar la matriz completa.
- No maneja modales de cookies ni redirecciones regionales.