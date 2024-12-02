import pytest
import time

from pages import *
from utils.my_date import *


class Locators:
    def __init__(self, page: Page):
        self.page = page

    def button(self, text, nth=-1) -> Locator:
        buttons = self.page.locator("button")
        for word in text:
            buttons = buttons.filter(has_text=word)
        return buttons.locator("visible=true").nth(nth)

    def get_below_element(self, element_type="*"):
        return self.page.locator(f'xpath=/following::{element_type}[position()=1]')

    def get_top_div_in_form(self, field_name: str) -> Locator:
        top_div_locator = self.page.locator("label").locator("visible=true").filter(has=self.page.get_by_text(field_name)).locator(self.get_below_element())
        return top_div_locator

class PageObject:
    def __init__(self, page: Page):
        self.page = page
        self.url = ""
        self.locators = Locators(self.page)

    def navigate(self):
        self.page.goto(self.url)

    def base_table(self, unique_text: str, table_index: int = -1):
        return Table(self.page, unique_text, table_index)

    def click_button(self, button_name, timeout=30_000, nth=-1):
        button_loc = self.page.get_by_role("button")
        for i in button_name:
            button_loc = button_loc.filter(has_text=i)
        button_loc.nth(nth).click(timeout=timeout)

    def search(self):
        # 可以尝试将你整个项目的搜索功能封装到这里
        ...

    def hover_retry(self, hover_object: Locator, next_click_object: Locator, first_action="hover", second_action="click",
                    timeout=30_000):
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout / 1000:
                pytest.fail(f"hover重试{hover_object.__str__()}在{timeout / 1000}秒内未成功")
            try:
                self.page.mouse.move(x=1, y=1)
                self.page.wait_for_timeout(1_000)
                if first_action == "hover":
                    hover_object.last.hover()
                else:
                    hover_object.last.click()
                self.page.wait_for_timeout(3_000)
                if second_action == "click":
                    next_click_object.last.click(timeout=3000)
                else:
                    next_click_object.last.wait_for(state="visible", timeout=3000)
                break
            except:
                continue

    def input_in_form(self, form_item_name: str, input_text: str, form_locator: Locator = None, timeout: float = None):
        if form_locator:
            form_locator.locator(self.locators.get_top_div_in_form(form_item_name)).locator("input, textarea").locator("visible=true").last.fill(input_text, timeout=timeout)
        else:
            self.locators.get_top_div_in_form(form_item_name).locator("input, textarea").locator("visible=true").last.fill(input_text, timeout=timeout)

    def dropdown_in_form(self, form_item_name: str, select_item: str, form_locator: Locator = None, timeout: float = None):
        if form_locator:
            form_locator.locator(self.locators.get_top_div_in_form(form_item_name)).locator("visible=true").click(timeout=timeout)
            if form_locator.locator(self.locators.get_top_div_in_form(form_item_name)).locator('//input[@type="search"]').count():
                form_locator.locator(self.locators.get_top_div_in_form(form_item_name)).locator('//input[@type="search"]').fill(select_item, timeout=timeout)
        else:
            self.locators.get_top_div_in_form(form_item_name).locator("visible=true").click(timeout=timeout)
            if self.locators.get_top_div_in_form(form_item_name).locator('//input[@type="search"]').count():
                self.locators.get_top_div_in_form(form_item_name).locator('//input[@type="search"]').fill(select_item, timeout=timeout)
        self.page.locator(".ant-select-dropdown").locator("visible=true").get_by_text(select_item).click(timeout=timeout)
        expect(self.page.locator(".ant-select-dropdown")).to_be_hidden(timeout=timeout)

    def radio_in_form(self, form_item_name: str, select_item: str, form_locator: Locator = None, timeout: float = None):
        if form_locator:
            form_locator.locator(self.locators.get_top_div_in_form(form_item_name)).locator("label").locator("visible=true").filter(has_text=select_item).locator("input").check(timeout=timeout)
        else:
            self.locators.get_top_div_in_form(form_item_name).locator("label").locator("visible=true").filter(has_text=select_item).locator("input").check(timeout=timeout)

    def switch_in_form(self, form_item_name: str, switch_status: str, form_locator: Locator = None, timeout: float = None):
        if "开" in switch_status or "是" in switch_status:
            _switch_status = True
        else:
            _switch_status = False

        if  form_locator:
            form_locator.locator(self.locators.get_top_div_in_form(form_item_name)).get_by_role("switch").set_checked(_switch_status, timeout=timeout)
        else:
            self.locators.get_top_div_in_form(form_item_name).get_by_role("switch").set_checked(_switch_status, timeout=timeout)

    def datetime_in_form(self, form_item_name: str, date: str, form_locator: Locator = None, timeout: float = None):
        if form_locator:
            date_locator = form_locator.locator(self.locators.get_top_div_in_form(form_item_name))
        else:
            date_locator = self.locators.get_top_div_in_form(form_item_name)

        date_list = date.split(",")
        for index, date_item in enumerate(date_list):
            try:
                format_datetime = get_datetime(int(date_item))
            except:
                format_datetime = date_item

            date_locator.locator("input").nth(index).click(timeout=timeout)
            date_locator.locator("input").nth(index).fill(format_datetime, timeout=timeout)
            date_locator.locator("input").nth(index).blur(timeout=timeout)

    def fill_form_quickly(self, form_locator: Locator = None, timeout: float = None, **kwargs):
        for form_item, content in kwargs.items():
            if not content:
                continue
            elif self.locators.get_top_div_in_form(form_item).locator(".ant-input").count():
                self.input_in_form(form_item_name=form_item, input_text=content, form_locator=form_locator, timeout=timeout)
            elif self.locators.get_top_div_in_form(form_item).locator(".ant-select-selector").count():
                self.dropdown_in_form(form_item_name=form_item, select_item=content, form_locator=form_locator, timeout=timeout)
            elif self.locators.get_top_div_in_form(form_item).locator(".ant-radio-group").count():
                self.radio_in_form(form_item_name=form_item, select_item=content, form_locator=form_locator, timeout=timeout)
            elif self.locators.get_top_div_in_form(form_item).get_by_role("switch").count():
                self.switch_in_form(form_item_name=form_item, switch_status=content, form_locator=form_locator, timeout=timeout)
            elif self.locators.get_top_div_in_form(form_item).locator(".ant-picker").count():
                self.datetime_in_form(form_item_name=form_item, date=content, form_locator=form_locator, timeout=timeout)
            else:
                pytest.fail(f'不支持的快捷表单 \n{form_item}:{content}')

    def fill_form_quickly_when_more_forms(self, form_locator: Locator = None, timeout: float = None, **kwargs):
        existed_form_item_list = []
        unique_form_item = False
        if form_locator:
            _form_locator = form_locator
        else:
            for index, item in enumerate(kwargs.keys()):
                if index == 0:
                    try:
                        self.locators.get_top_div_in_form(item).last.wait_for(timeout=timeout)
                    except:
                        pass

                if self.locators.get_top_div_in_form(item).count() == 0:
                    continue
                else:
                    if self.locators.get_top_div_in_form(item) == 1:
                        unique_form_item = True
                    existed_form_item_list.append(self.locators.get_top_div_in_form(item))
                if unique_form_item and len(existed_form_item_list) >= 2:
                    break

            contain_all_existed_form_items_loc = self.page.locator("*")
            for item_loc in existed_form_item_list:
                contain_all_existed_form_items_loc = contain_all_existed_form_items_loc.filter(has=item_loc)
            if unique_form_item:
                _form_locator = contain_all_existed_form_items_loc.last
            else:
                _form_locator = min(contain_all_existed_form_items_loc.all(), key=lambda loc: len(loc.text_content()))

        self.fill_form_quickly(_form_locator, timeout=timeout, **kwargs)

    @allure.step("重试")
    def retry(self, *args, retry_numbers=10):
        """
        重试一系列步骤
        @param args:
        1. 第一个传的是子步骤的指针,比如locator.click, locator.hover
        2. 如果只传子步骤指针,则默认执行时的timeout为3_000
        3. 如果需要传参,则需要使用(子步骤指针, 位置参数1, 位置参数2, {"命名参数名称1": 命名参数值1, "命名参数名称2": 命名参数值2})
        @param retry_numbers:
        @return:
        """
        for _ in range(retry_numbers):
            try:
                for arg in args:
                    if isinstance(arg, tuple):
                        with allure.step(f"{arg[0].__name__} 参数:{arg[1:]}"):
                            func = arg[0]
                            param = arg[1:]
                            named_params = {}
                            positional_params = []
                            for in_param in param:
                                if isinstance(in_param, dict):
                                    named_params.update(in_param)
                                else:
                                    positional_params.append(in_param)
                            func(*positional_params, **named_params)
                    else:
                        with allure.step(arg.__name__):
                            arg(timeout=3000)
                break
            except Exception as e:
                if _ == retry_numbers - 1:
                    print(f"已经重试{retry_numbers}次，但仍然失败，错误信息：", e)
                    raise e

