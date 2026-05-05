# Hit #6 — Testing y Estandarización de Entorno

Este último Hit consolida el código modular, de logs y reintentos, agregando pruebas automatizadas (unitarias/integración) dentro de un directorio `tests/` y adoptando herramientas modernas como `pyproject.toml`.

## Requisitos previos

- Python 3.10 o superior
- Google Chrome instalado en el sistema
- Selenium 4.6 o superior

## Instalación

Desde la raíz del proyecto (`TP1-Selenium/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r hit6/requirements.txt
```

## Ejecución

Para ejecutar el scraper, con el entorno virtual activo:

```bash
python hit6/scraper.py
```

Para correr las pruebas automatizadas (por ejemplo con `pytest`):

```bash
pytest hit6/tests/
```
*(También se puede revisar la cobertura o los reportes HTML generados dependiendo de las herramientas definidas en `pyproject.toml`).*

## Salida esperada

Al ejecutar las pruebas, se validará el correcto funcionamiento de extractores y fábricas:

```text
============================= test session starts ==============================
...
collected X items

hit6/tests/test_extractors.py .                                          [ 50%]
hit6/tests/test_scraper.py .                                             [100%]

============================== X passed in 1.23s ===============================
```

## Decisiones de diseño

- **Directorio `tests/`**: Facilita la adopción de TDD o testing automatizado sobre las partes modulares (extractores, inicializadores) sin necesidad de levantar siempre el navegador completo.
- **`pyproject.toml`**: Centraliza la configuración de testing, linters o cualquier herramienta del ecosistema moderno de Python en lugar de múltiples archivos sueltos.
