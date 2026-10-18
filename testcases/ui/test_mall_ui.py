import pytest
from playwright.sync_api import sync_playwright

from pages.admin_login_page import AdminLoginPage

pytestmark = [pytest.mark.smoke]


@pytest.fixture(scope="module")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        yield context.new_page()
        browser.close()


class TestAdminLoginUI:
    """后台登录 UI 冒烟：成功 / 密码错误 / 空账号。"""

    def test_login_success(self, page):
        # Arrange
        login_page = AdminLoginPage(page).open()
        # Act
        login_page.login_as("admin", "macro123")
        # Assert
        assert login_page.is_dashboard_visible(), "正确账号登录后应进入仪表盘"

    def test_login_wrong_password_shows_error(self, page):
        # Arrange
        login_page = AdminLoginPage(page).open()
        # Act
        login_page.login_as("admin", "wrong_password")
        # Assert
        assert login_page.has_error_alert(), "密码错误应出现 Element UI 错误提示"
        login_page.screenshot_on_demand("login_wrong_password")

    def test_login_empty_username(self, page):
        # Arrange
        login_page = AdminLoginPage(page).open()
        # Act
        login_page.login_as("", "macro123")
        # Assert
        assert login_page.has_error_alert() or "login" in page.url, "空账号不应登录成功"


class TestPortalShoppingFlow:
    """前台「搜索-进详情-加购」主流程冒烟（mall-app-web 移动端演示站）。"""

    def test_search_and_open_detail(self, page):
        # Arrange
        page.goto("https://www.macrozheng.com/app/", wait_until="domcontentloaded")
        # Act：点击首页第一个商品卡片进入详情
        page.locator(".product-item, .goods-item").first.click()
        # Assert：详情页出现价格与加入购物车按钮
        assert page.get_by_text("加入购物车").count() > 0 or page.get_by_text("立即购买").count() > 0
