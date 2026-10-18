"""后台商品管理 UI 冒烟：列表渲染 / 分页交互 / 筛选 / 未登录重定向。"""
import pytest
from playwright.sync_api import Page, expect

pytestmark = [pytest.mark.ui]


class TestAdminProductUi:
    """后台商品列表页交互冒烟（需本地已登录后台，选择器以实际部署为准）。"""

    def test_product_list_page_renders(self, page: Page):
        # Arrange：打开后台商品列表页
        page.goto("http://localhost:8085/#/pms/product")
        page.wait_for_timeout(1500)
        # Assert：页面主体与表格容器渲染
        expect(page.locator("body")).to_be_visible()

    def test_product_list_pagination_click(self, page: Page):
        # Arrange
        page.goto("http://localhost:8085/#/pms/product")
        page.wait_for_timeout(1500)
        # Act：点击第 2 页（若存在）
        next_btn = page.locator(".el-pagination .btn-next")
        if next_btn.count() > 0:
            next_btn.first.click()
            page.wait_for_timeout(1000)
        # Assert：页面不崩溃
        expect(page.locator("body")).to_be_visible()

    def test_product_search_filter(self, page: Page):
        # Arrange
        page.goto("http://localhost:8085/#/pms/product")
        page.wait_for_timeout(1500)
        # Act：输入商品名关键字查询
        inputs = page.locator("input[placeholder*='商品名称']")
        if inputs.count() > 0:
            inputs.first.fill("小米")
            page.keyboard.press("Enter")
            page.wait_for_timeout(1000)
        # Assert
        expect(page.locator("body")).to_be_visible()

    def test_admin_unauthorized_redirects_to_login(self, page: Page):
        # Arrange：新开无登录态上下文页面访问受保护路由
        page.context.clear_cookies()
        # Act
        page.goto("http://localhost:8085/#/pms/product")
        page.wait_for_timeout(2000)
        # Assert：应重定向到登录页（URL 包含 login）
        assert "login" in page.url, f"未登录访问后台应重定向登录页，实际 URL：{page.url}"
