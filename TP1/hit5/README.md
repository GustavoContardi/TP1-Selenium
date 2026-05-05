# Hit #5 — Tolerancia a Fallos, Reintentos y Logging Centralizado

En este avance se integran mecanismos de robustez para un web scraping mucho más estable. Se incluye una configuración centralizada de logs (`logging_setup.py`) y decoradores de reintento (`retry.py`) para lidiar con elementos que tardan en cargar o problemas de conexión intermitentes.

## Requisitos previos

- Python 3.10 o superior
- Google Chrome instalado en el sistema
- Selenium 4.6 o superior

## Instalación

Desde la raíz del proyecto (`TP1-Selenium/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r hit5/requirements.txt
```

## Ejecución

Con el entorno virtual activo:

```bash
python hit5/scraper.py
```

## Salida esperada

La salida en consola contendrá trazas de log estandarizadas mostrando el progreso y las operaciones de reintento automáticas si la página experimenta algún retraso en responder:

```text
[INFO] Iniciando configuración de logs...
[INFO] Instanciando WebDriver...
[INFO] Navegando a MercadoLibre...
[INFO] Extrayendo información de productos...
```

## Decisiones de diseño

- **Decoradores de Reintento (`retry.py`)**: Centraliza la lógica de tolerancia a fallos. Si un selector falla de manera efímera, el sistema esperará y reintentará en vez de arrojar un error y detener el proceso.
- **Logging Desacoplado (`logging_setup.py`)**: Configura el sistema de trazabilidad de forma global y estructurada para todo el proyecto.
