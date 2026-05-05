from unittest.mock import MagicMock, patch
from selenium.common.exceptions import TimeoutException, WebDriverException
from retry import with_backoff
import pytest

class TestWithBackoff:
    def test_exito_primer_intento(self):
        fn = MagicMock(return_value="ok")
        decorated = with_backoff(max_attempts=3, base_delay=0)(fn)
        assert decorated() == "ok"
        assert fn.call_count == 1

    def test_retry_tras_timeout_y_exito_en_segundo(self):
        fn = MagicMock(side_effect=[TimeoutException(), "ok"])
        with patch("retry.time.sleep"):   # no esperar en tests
            decorated = with_backoff(max_attempts=3, base_delay=0)(fn)
            assert decorated() == "ok"
        assert fn.call_count == 2

    def test_retry_dispara_exactamente_3_veces(self):
        fn = MagicMock(side_effect=TimeoutException())
        with patch("retry.time.sleep"):
            decorated = with_backoff(max_attempts=3, base_delay=0)(fn)
            with pytest.raises(TimeoutException):
                decorated()
        assert fn.call_count == 3

    def test_excepcion_no_contemplada_propaga_inmediatamente(self):
        fn = MagicMock(side_effect=ValueError("inesperado"))
        decorated = with_backoff(max_attempts=3, base_delay=0, exceptions=(TimeoutException,))(fn)
        with pytest.raises(ValueError):
            decorated()
        assert fn.call_count == 1   # no reintenta

    def test_backoff_delay_crece_exponencialmente(self):
        fn = MagicMock(side_effect=[TimeoutException(), TimeoutException(), "ok"])
        sleep_calls = []
        with patch("retry.time.sleep", side_effect=lambda d: sleep_calls.append(d)):
            decorated = with_backoff(max_attempts=3, base_delay=2.0, jitter=False)(fn)
            decorated()
        assert sleep_calls[0] == pytest.approx(2.0)
        assert sleep_calls[1] == pytest.approx(4.0)

    def test_wraps_preserva_nombre_funcion(self):
        def mi_funcion(): pass
        decorated = with_backoff()(mi_funcion)
        assert decorated.__name__ == "mi_funcion"

    def test_webdriver_exception_tambien_reintenta(self):
        fn = MagicMock(side_effect=[WebDriverException(), "ok"])
        with patch("retry.time.sleep"):
            decorated = with_backoff(max_attempts=3, base_delay=0)(fn)
            assert decorated() == "ok"
