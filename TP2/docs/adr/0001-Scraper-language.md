# 0001. Elección de Python como lenguaje principal para el Scraper

## Estado

Aceptado

## Contexto

Para el desarrollo del componente de extracción de datos (`scraper.py`), se evaluaron diferentes lenguajes de programación, principalmente Java y Python. Dado que el objetivo es realizar web scraping de forma eficiente, mantenible y con una integración fluida con herramientas de automatización de navegadores, el lenguaje elegido debe ofrecer un ecosistema robusto en esta área específica.

El problema con Java en este contexto es su excesiva verbosidad y la carga administrativa de boilerplate requerida para tareas simples de procesamiento de datos y scripts de automatización, lo que ralentiza el ciclo de desarrollo inicial.

## Decisión

Se elige **Python** como el lenguaje de desarrollo para el scraper por las siguientes razones:

1. **Ecosistema de Scraping**: Python posee las bibliotecas más maduras y utilizadas en la industria para esta tarea, tales como `Selenium` (para interacción dinámica), `BeautifulSoup` (para parseo de HTML) y `Pandas` (para manipulación de los datos extraídos).
2. **Versatilidad y Sintaxis**: La naturaleza concisa de Python permite escribir scripts de scraping potentes con pocas líneas de código, facilitando la lectura y el mantenimiento por parte de otros desarrolladores.
3. **Manejo de Datos**: La facilidad para trabajar con formatos como JSON y la integración nativa con herramientas de ciencia de datos hacen que el procesamiento de los resultados de MercadoLibre sea inmediato.
4. **Comunidad y Documentación**: Existe una vasta cantidad de recursos, ejemplos y soporte comunitario para resolver desafíos comunes en scraping (como manejo de waits, selectores complejos y evasión de bloqueos) específicamente en Python.

## Consecuencias

### Positivas
- **Velocidad de Desarrollo**: Reducción drástica en el tiempo necesario para prototipar y ajustar los selectores del scraper.
- **Ligereza**: El script resultante es liviano y fácil de ejecutar tanto localmente como en contenedores sin la sobrecarga de una JVM completa para una tarea de scripting.
- **Extensibilidad**: Es trivial agregar nuevas capacidades como generación de estadísticas o exportación a diferentes bases de datos gracias a la variedad de librerías disponibles en PyPI.

### Negativas
- **Tipado Dinámico**: Al no ser un lenguaje estrictamente tipado como Java, se requiere mayor disciplina en el uso de Type Hinting y pruebas unitarias para evitar errores en tiempo de ejecución.
- **Rendimiento**: Aunque Python es más lento que Java en ejecución pura, para tareas de scraping el cuello de botella es la latencia de red y el renderizado del navegador, por lo que la diferencia de rendimiento del lenguaje es despreciable.
