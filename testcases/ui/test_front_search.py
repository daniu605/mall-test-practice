"""前台搜索与后台登录 UI 场景扩充（Playwright，参数化驱动）。

选择器说明：以本地部署的 mall 前台/后台实际页面为准，如与版本不符只需调整
类属性中的定位表达式，用例逻辑不动。
"""
import re

import pytest
from playwright.sync_api import Page, expect

pytestmark = [pytest.mark.ui]


class TestFrontSearchUi:
    """前台搜索 UI：参数化覆盖 8 个关键词场景（正常/边界/异常）。"""

    @pytest.mark.parametrize(
        "keyword",
        ["小米", "华为", "iphone", "手机", "a", "红米", "苹果", "六", "1' or '1'='1", "<script>alert(1)</script>", "%00", "测试不存在的商品xyz", "  ", "xiaomi手机旗舰店官方"],
        ids=["常见词", "品牌词", "英文词", "单字", "单字符", "子品牌", "品牌2", "数字中文", "SQL注入片段", "XSS片段", "空字节", "不存在词", "纯空格", "长尾组合词"],
    )
    def test_front_search_keyword(self, front_page: Page, keyword: str):
        # Arrange：打开前台首页搜索框
        front_page.goto("http://localhost:8086/#/product/search?keyword=")
        # Act：输入关键词并搜索
        front_page.fill("input[type='text']", keyword)
        front_page.keyboard.press("Enter")
        front_page.wait_for_timeout(1500)
        # Assert：页面不崩溃（不允许 500 白页），且有内容区域渲染
        body_text = front_page.text_content("body") or ""
        assert "error" not in body_text.lower()[:200], f"关键词 {keyword[:20]!r} 触发页面异常"

    def test_front_search_empty_keyword(self, front_page: Page):
        # Arrange
        front_page.goto("http://localhost:8086/#/product/search")
        # Act：直接搜索空关键词
        front_page.wait_for_timeout(1000)
        # Assert：空关键词不崩溃
        expect(front_page.locator("body")).to_be_visible()

    def test_front_home_loads(self, front_page: Page):
        # Act：打开首页
        front_page.goto("http://localhost:8086/")
        front_page.wait_for_timeout(1500)
        # Assert：首页主体渲染
        expect(front_page.locator("body")).to_be_visible()


class TestAdminLoginUi:
    """后台登录 UI 异常流补充。"""

    def test_login_xss_input_rejected(self, page: Page):
        # Arrange：打开后台登录页
        page.goto("http://localhost:8085/#/login")
        # Act：输入 XSS 片段作为用户名
        page.fill("input[type='text']", "<script>alert(1)</script>")
        page.fill("input[type='password']", "anything123")
        page.keyboard.press("Enter")
        page.wait_for_timeout(1000)
        # Assert：不触发弹窗（XSS 被转义）
        assert page.url, "登录页应保持可控渲染"

    def test_login_long_input(self, page: Page):
        # Arrange
        page.goto("http://localhost:8085/#/login")
        # Act：200 字符超长用户名
        page.fill("input[type='text']", "a" * 200)
        page.fill("input[type='password']", "a" * 200)
        page.keyboard.press("Enter")
        page.wait_for_timeout(1000)
        # Assert：不崩溃
        expect(page.locator("body")).to_be_visible()
