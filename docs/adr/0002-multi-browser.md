# 0002. Soporte simultáneo de múltiples navegadores (Chrome y Firefox)

## Estado

Aceptado

## Contexto

El proyecto utiliza Selenium para realizar web scraping sobre el sitio de MercadoLibre. Originalmente, el desarrollo se centró en un único navegador (Chrome), pero surgió la necesidad de robustecer la solución frente a diversos entornos de ejecución y posibles restricciones técnicas.

Los motivos principales que motivan esta decisión son:
1. **Detección de Bots**: Algunos sitios web aplican técnicas de detección que varían según el motor de renderizado o las huellas digitales (fingerprinting) del navegador. Tener la capacidad de alternar entre Chrome (Chromium) y Firefox (Gecko) permite evadir bloqueos específicos.
2. **Compatibilidad de Entornos**: En entornos de CI/CD o contenedores (Docker/Kubernetes), puede ser más sencillo o eficiente instalar una versión específica de un navegador sobre otro según la imagen base utilizada.
3. **Resiliencia**: Si una actualización de un driver (ChromeDriver o GeckoDriver) introduce un bug o incompatibilidad, el sistema puede seguir operando simplemente cambiando una variable de entorno.

## Decisión

Se decide implementar una abstracción en la inicialización del WebDriver que permita seleccionar entre `chrome` y `firefox` mediante la variable de entorno `BROWSER`.

- Por defecto se utilizará `chrome`.
- Ambas implementaciones deben soportar el modo `headless` (sin interfaz gráfica) controlado por la variable `HEADLESS`.
- El código debe manejar las configuraciones específicas de cada navegador (Arguments, Options) de manera aislada.

## Consecuencias

### Positivas
- **Flexibilidad**: El usuario puede elegir el navegador que mejor se adapte a su infraestructura.
- **Robustez**: Mayor capacidad de respuesta ante fallos específicos de un motor de navegación.
- **Portabilidad**: Facilita la ejecución en diversos sistemas operativos donde uno de los navegadores podría no estar disponible o ser inestable.

### Negativas
- **Mantenimiento**: El equipo debe asegurar que las funcionalidades de scraping operen correctamente en ambos motores.
- **Complejidad de Testing**: Se duplica la superficie de pruebas si se desea garantizar compatibilidad total en cada release.
- **Dependencias**: Se requiere la presencia de ambos binarios (o la configuración correcta para el elegido) en el entorno de ejecución/Docker.
