from playwright.sync_api import Page, expect, BrowserContext
from pages.login_page import LoginPage
from pages.community_page import CommunityPage


class PageInstance:
    def __init__(self, page: Page):
        self.page = page
        self.login_page = LoginPage(self.page)
        self.community_page = CommunityPage(self.page)
