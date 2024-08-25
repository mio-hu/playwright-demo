import random

from playwright.sync_api import Page, Locator


class Table:
    def __init__(self, page: Page, unique_text: str, table_index: int):
        self.page = page
        self.page.wait_for_load_state("networkidle")
        self.div = self.page.locator("table").filter(has_text=unique_text).nth(table_index)
        self.header = self.div.locator("//thead/tr")
        self.body = self.div.locator("tbody")

    def get_header_index(self, header_text: str) -> int:
        return self.header.locator("th").all_text_contents().index(header_text)

    def get_row_locator(self, row_locator: Locator) -> Locator:
        return self.div.locator("tr").filter(has=row_locator)

    def get_cell(self, col: str | int, row: str | int | Locator) -> Locator:
        if isinstance(col, str):
            col_index = self.get_header_index(col)
        else:
            col_index = col

        if isinstance(row, Locator):
            row_loc = self.get_row_locator(row)
        elif isinstance(row, str):
            row_loc = self.div.locator("tr").filter(has_text=row)
        else:
            row_loc = self.body.locator("//tr[not(@aria-hidden='true')]").nth(row)

        return row_loc.locator("td").nth(col_index)

    def get_row_dict(self, row: int | Locator = "random") -> dict:
        if isinstance(row, int):
            tr = self.body.locator("tr").locator("visible=true").nth(row)
        elif isinstance(row, Locator):
            tr = self.div.locator("tr").filter(has=row)
        else:
            all_tr = self.body.locator("tr").locator("visible=true").all()
            tr = random.choice(all_tr)

        td_text_list = tr.locator("td").all_text_contents()
        header_text_list = self.header.locator("th").all_text_contents()

        row_dict = dict(zip(header_text_list, td_text_list))
        return row_dict

    def get_col_list(self, header: str) -> list:
        index = self.get_header_index(header)
        all_tr = self.div.locator("tbody").locator("tr").locator("visible=true").all()
        col_list = []
        for tr in all_tr:
            col_list.append(tr.locator("td").nth(index).text_content())
        return col_list

