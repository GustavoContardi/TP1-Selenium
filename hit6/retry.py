import time
import random
import logging
import functools
from selenium.common.exceptions import TimeoutException, WebDriverException

logger = logging.getLogger(__name__)

def with_backoff(
    max_attempts: int = 3,
    base_delay: float = 2.0,
    exceptions: tuple = (TimeoutException, WebDriverException),
    jitter: bool = True,
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener el producto/browser del contexto (kwargs) si está disponible, sino string vacío
            # Si no hay contexto, simplemente usamos el log sin ese detalle extra.
            for intento in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if intento == max_attempts:
                        logger.error(
                            "Fallo total tras agotar reintentos | función=%s | intentos=%d",
                            getattr(func, '__name__', str(func)), max_attempts, exc_info=True
                        )
                        raise e
                    
                    delay = base_delay * (2 ** (intento - 1))
                    if jitter:
                        delay += random.uniform(0, 1)
                        
                    # Extraer un string descriptivo de args/kwargs si se desea para el contexto
                    # Vamos a loggear lo especificado en la especificación:
                    # "Retry intento {n}/{max_attempts} | delay={delay:.1f}s | excepción={type(e).__name__} | {context}"
                    # No tenemos el context explícito siempre en el scope del decorator a menos que armemos uno.
                    # Armamos un mini context del nombre de la función y args.
                    context_str = f"func={getattr(func, '__name__', str(func))}"
                    logger.warning(
                        "Retry intento %d/%d | delay=%.1fs | excepción=%s | %s",
                        intento, max_attempts, delay, type(e).__name__, context_str
                    )
                    time.sleep(delay)
                # Si lanza una excepción no contemplada en `exceptions`, se propaga inmediatamente sin ser capturada
        return wrapper
    return decorator
