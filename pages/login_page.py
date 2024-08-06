from pages import *


class LoginPage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = "/account/sign_in"
        self._username_input = page.get_by_placeholder("用户名 / Email")
        self._password_input = page.get_by_placeholder("密码")
        self._login_button = page.locator('//*[@value="登录"]')
        self.avatar_img = page.locator('.avatar-32')

    @allure.step("导航到登录页面")
    def navigate(self):
        self.page.goto(self.url)

    @allure.step("输入账号密码并提交")
    def login(self, username: str, password: str):
        self._username_input.fill(username)
        self._password_input.fill(password)
        self.click_button("登录")
        # self._login_button.click()
