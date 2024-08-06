from pages import *


class CommunityPage(PageObject):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.url = "/topics"
        self.avatar_img = page.locator('.avatar-32')
        self.nav_menu = page.locator('.nav-pills')
        self.create_topic_button = page.locator('.btn-primary')
        self.node_selector_button = page.locator('#node-selector-button')
        self.test_base = page.locator('//a[@data-id="33"]')
        self.input_title = page.get_by_placeholder('在这里填写标题')
        self.input_body = page.locator('#topic_body')
        self.save_draft_button = page.locator("#save_as_draft")
        self.tips_for_success = page.get_by_text("话题创建成功。")
        self.first_topic = page.locator(".topic").first
        self.reply_button = page.locator("#reply-button")

    @allure.step("导航到社区页面")
    def navigate(self):
        self.page.goto(self.url)

    @allure.step("点击新建文章按钮")
    def goto_create_topic_page(self):
        self.create_topic_button.click()

    @allure.step("输入文章的信息")
    def create_topic(self):
        self.node_selector_button.click()
        self.test_base.click()
        self.input_title.fill("测试文章标题")
        self.input_body.fill("测试文章正文")
        self.save_draft_button.click()

    @allure.step("打开第一篇文章")
    def read_first_topic(self):
        self.first_topic.click()







