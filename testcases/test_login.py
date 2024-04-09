import allure
from pages.login_page import LoginPage
from playwright.sync_api import Page, expect
from conf.config import base_config


@allure.feature("测试登录成功")
def test_login(page: Page):
    page.context.clear_cookies()
    page.set_extra_http_headers({})
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login(base_config.get("username"), base_config.get("password"))
    login_page.page.wait_for_timeout(3000)
    expect(login_page.avatar_img).to_be_visible(timeout=3000)


