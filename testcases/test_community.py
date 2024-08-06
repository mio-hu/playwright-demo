import pytest

from testcases import *

@allure.feature("导航到社区页面")
def test_goto_community(new_context):
    page_ins = instance_all_pages(new_context)
    page_ins.community_page.navigate()
    expect(page_ins.community_page.nav_menu).to_be_visible(timeout=3000)

@allure.feature("新建文章")
@pytest.mark.skip
def test_create_topic(new_context):
    page_ins = instance_all_pages(new_context)
    page_ins.community_page.navigate()
    page_ins.community_page.goto_create_topic_page()
    page_ins.community_page.create_topic()
    expect(page_ins.community_page.tips_for_success).to_be_visible(timeout=3_000)

@allure.feature("阅读文章")
def test_read_topic(new_context):
    page_ins = instance_all_pages(new_context)
    page_ins.community_page.navigate()
    page_ins.community_page.read_first_topic()
    page_ins.page.wait_for_selector("#reply-button")
    page_ins.page.eval_on_selector("#reply-button", "element => element.scrollIntoView()")
    expect(page_ins.community_page.reply_button).to_be_visible(timeout=2_000)

@pytest.fixture()
def teardown_01():
    yield
    print("这里可以写一些环境清理的代码")