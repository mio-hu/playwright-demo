import pytest
from utils.cookie import get_cookies
from conf.config import base_config


@pytest.fixture()
def page(page, pytestconfig):
    page.set_viewport_size({"width": 1920, "height": 1080})
    cookies = get_cookies(page, base_config.get("username"), base_config.get("password"))
    cookies = {"Cookie": "; ".join(f"{cookie['name']}={cookie['value']}" for cookie in cookies)}
    page.set_extra_http_headers(cookies)
    yield page