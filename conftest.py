"""pytest 根配置：项目根目录加入 sys.path + 全局共享 fixture。

设计意图：
1. admin/portal 客户端 fixture 收敛到根 conftest，所有测试模块直接引用，避免重复代码；
2. scope=module：同一模块内复用一次登录会话，跑批更快；
3. fixture 只负责「给一个已登录的客户端」，断言逻辑全部留在用例里。
"""
import sys
import pathlib

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from common.http_client import AdminClient, PortalClient  # noqa: E402


@pytest.fixture(scope="module")
def admin():
    """已登录的后台管理端客户端。"""
    client = AdminClient()
    client.login()
    return client


@pytest.fixture(scope="module")
def portal():
    """已登录的前台商城端（会员）客户端。"""
    client = PortalClient()
    client.login()
    return client


@pytest.fixture(scope="module")
def front_page():
    """前台商城 UI 独立浏览器会话（模块级复用）。"""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        yield page
        browser.close()
