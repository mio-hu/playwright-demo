import allure
import pytest

from pages.community_page import CommunityPage
from playwright.sync_api import Page, expect

@allure.feature("导航到社区页面")
def test_goto_community(page: Page):
    cp = CommunityPage(page)
    cp.navigate()
    expect(cp.nav_menu).to_be_visible(timeout=3000)

@allure.feature("新建文章")
@pytest.mark.skip
def test_create_topic(page: Page):
    cp = CommunityPage(page)
    cp.navigate()
    cp.goto_create_topic_page()
    cp.create_topic()
    expect(cp.tips_for_success).to_be_visible(timeout=3000)

@allure.feature("阅读文章")
def test_read_topic(page: Page):
    cp = CommunityPage(page)
    cp.navigate()
    cp.read_first_topic()
    page.wait_for_selector("#reply-button")
    page.eval_on_selector("#reply-button", "element => element.scrollIntoView()")
    expect(cp.reply_button).to_be_visible(timeout=2000)

