from playwright.sync_api import expect, Page
import os
from pages.login_page import LoginPage


def get_cookies(page: Page, username: str, password: str):
    """
    通过页面进行登录
    :param page: page对象
    :param username:
    :param password:
    :return:
    """
    if os.environ.get("COOKIES"):
        page.context.clear_cookies()
        cookies = eval(os.environ["COOKIES"])
        return cookies
    else:
        lp = LoginPage(page)
        page.context.clear_cookies()
        lp.navigate()
        lp.login(username, password)
        expect(lp.avatar_img).to_be_visible(timeout=3000)
        cookies = page.context.cookies()
        os.environ["COOKIES"] = str(cookies)
        return cookies