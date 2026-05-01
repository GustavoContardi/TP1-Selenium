from unittest.mock import patch, MagicMock
from driver_factory import build_driver

class TestBuildDriver:
    def test_chrome_headless_agrega_argumento(self):
        with patch("driver_factory.webdriver.Chrome") as mock_chrome:
            mock_chrome.return_value = MagicMock()
            build_driver("chrome", headless=True)
            args, kwargs = mock_chrome.call_args
            options = kwargs.get("options") or args[0]
            assert any("headless" in arg for arg in options.arguments)

    def test_firefox_headless_agrega_argumento(self):
        with patch("driver_factory.webdriver.Firefox") as mock_firefox:
            mock_firefox.return_value = MagicMock()
            build_driver("firefox", headless=True)
            args, kwargs = mock_firefox.call_args
            options = kwargs.get("options") or args[0]
            assert any("headless" in arg for arg in options.arguments)

    def test_browser_invalido_lanza_valueerror(self):
        import pytest
        with pytest.raises(ValueError, match="browser"):
            build_driver("safari", headless=False)

    def test_user_agent_siempre_presente(self):
        with patch("driver_factory.webdriver.Chrome") as mock_chrome:
            mock_chrome.return_value = MagicMock()
            build_driver("chrome", headless=False)
            args, kwargs = mock_chrome.call_args
            options = kwargs.get("options") or args[0]
            assert any("user-agent" in arg for arg in options.arguments)
