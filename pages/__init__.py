import os
import allure
from playwright.sync_api import Page, expect, BrowserContext, Locator
from pages.base_page import PageObject
from pages.login_page import LoginPage
from pages.community_page import CommunityPage
from utils.global_map import GlobalMap
from components.table import Table
from conf.config import base_config
from utils.path import get_path
from filelock import FileLock


class PageInstance:
    def __init__(self, page: Page):
        self.page = page
        self.login_page = LoginPage(self.page)
        self.community_page = CommunityPage(self.page)

    @staticmethod
    def instance_all_pages(new_context):
        env = GlobalMap.get("env")
        user_name = base_config.get("username")
        password = base_config.get("password")
        auth_file_path = get_path(f".temp/{env}-{user_name}.json")
        with FileLock(get_path(f".temp/{env}-{user_name}.lock")):
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
