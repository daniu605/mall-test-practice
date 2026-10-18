"""mall 后台管理登录页对象（mall-admin-web，Element UI）。

选择器按 mall-admin-web 实际 DOM 调整：登录按钮为 .el-button--primary，
输入框使用 placeholder 定位比 class 更稳。
"""
from pages.base_page import BasePage


class AdminLoginPage(BasePage):
    URL = "http://localhost:8090/#/login"

    # ---------- 定位器 ----------
    USERNAME = 'input[placeholder*="账号"], input[name="username"]'
    PASSWORD = 'input[type="password"]'
    LOGIN_BTN = "button"

    # ---------- 操作 ----------
    def open(self):
        self.goto(self.URL)
        return self

    def login_as(self, username: str, password: str):
        self.fill(self.USERNAME, username)
        self.fill(self.PASSWORD, password)
        self.click(self.LOGIN_BTN)
        return self

    # ---------- 断言支撑 ----------
    def is_dashboard_visible(self) -> bool:
        """登录成功后跳转仪表盘，出现 shouye 文本或路由变化。"""
        self.page.wait_for_timeout(2000)
        return "dashboard" in self.page.url or "首页" in self.page.content()

    def has_error_alert(self) -> bool:
        """Element UI 错误提示（el-message--error）。"""
        return self.page.locator(".el-message--error").count() > 0
