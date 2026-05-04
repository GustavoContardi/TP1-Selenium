# Hit #4 — Modularización y Patrones de Diseño

Este script evoluciona el scraper original separando las responsabilidades en múltiples módulos. Se introducen patrones como Factory para inicializar el navegador (`browser_factory.py`), separación de selectores del DOM (`dom_selectors.py`), y extracción de datos (`extractors.py`).

## Requisitos previos

- Python 3.10 o superior
- Google Chrome instalado en el sistema
- Selenium 4.6 o superior

## Instalación

Desde la raíz del proyecto (`TP1-Selenium/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r hit4/requirements.txt
```

## Ejecución

Con el entorno virtual activo:

```bash
python hit4/scraper.py
```

## Salida esperada

El comportamiento del scraper a nivel usuario es similar a los hits anteriores, mostrando los resultados en consola, pero con una ejecución estructurada bajo los nuevos módulos.

```text
1. <título producto 1>
2. <título producto 2>
...
```

## Decisiones de diseño

- **Separación de responsabilidades (SRP)**: La lógica se divide en archivos específicos para selectores, inicialización del driver y manipulación de datos, mejorando la mantenibilidad.
- **Patrón Factory**: Abstrae la inicialización del WebDriver permitiendo cambiar configuraciones de Chrome fácilmente en un solo lugar.
