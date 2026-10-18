"""Playwright PO 模式：基类封装公共操作与等待策略。"""


class BasePage:
    def __init__(self, page):
        self.page = page

    def goto(self, url: str):
        self.page.goto(url, wait_until="networkidle")

    def fill(self, selector: str, text: str):
        self.page.locator(selector).fill(text)

    def click(self, selector: str):
        self.page.locator(selector).click()

    def text_of(self, selector: str) -> str:
        return self.page.locator(selector).inner_text()

    def screenshot_on_demand(self, name: str):
        self.page.screenshot(path=f"test-results/screenshots/{name}.png", full_page=True)
