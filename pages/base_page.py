from pages import *


class PageObject:
    def __init__(self, page: Page):
        self.page = page
        self.url = ""

    def navigate(self):
        self.page.goto(self.url)

    def click_button(self, button_name, timeout=30_000):
        button_loc = self.page.get_by_role("button")
        for i in button_name:
            button_loc = button_loc.filter(has_text=i)
        button_loc.click(timeout=timeout)

    def search(self):
        # 可以尝试将你整个项目的搜索功能封装到这里
        ...







