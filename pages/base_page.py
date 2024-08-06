import os.path
from filelock import FileLock
from utils.global_map import GlobalMap
from conf.config import base_config
from utils.path import get_path
from playwright.sync_api import Page, expect, BrowserContext


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

def instance_all_pages(new_context):
    env = GlobalMap.get("env")
    user_name = base_config.get("username")
    password = base_config.get("password")
    auth_file_path = get_path(f".temp/{env}-{user_name}.json")
    with FileLock(get_path(f".temp/{env}-{user_name}.lock")):
        from pages.page_instance import PageInstance
        if os.path.exists(auth_file_path):
            context: BrowserContext = new_context(storage_state=auth_file_path)
            page = context.new_page()
            page_ins = PageInstance(page)
            page_ins.community_page.navigate()
            # expect(page_ins.login_page.avatar_img).to_be_visible(timeout=3_000)
            if not page_ins.login_page.avatar_img.count():
                page_ins.login_page.navigate()
                page_ins.login_page.login(user_name, password)
                page_ins.login_page.page.context.storage_state(path=auth_file_path)
        else:
            context: BrowserContext = new_context()
            page = context.new_page()
            page_ins = PageInstance(page)
            page_ins.login_page.navigate()
            page_ins.login_page.login(user_name, password)
            page_ins.login_page.page.context.storage_state(path=auth_file_path)
    return page_ins





