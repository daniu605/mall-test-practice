"""前台会员鉴权专项：注册校验 + 登录异常流 + 会员信息（P0）。"""
import uuid

import pytest

from api.portal_api import PortalApi
from common.http_client import PortalClient

pytestmark = [pytest.mark.regression]


class TestPortalRegister:
    """会员注册：参数校验与重复注册拦截。"""

    def test_register_username_too_short(self):
        # Arrange：用户名仅 2 位（低于最小长度）
        client = PortalClient()
        payload = {"username": "ab", "password": "test123456", "icon": "", "phone": ""}
        # Act
        resp = client.post_json(PortalApi.REGISTER, payload)
        # Assert：应业务报错而非 500
        assert resp.status_code == 200, f"短用户名触发 500：{resp.text[:200]}"
        assert resp.json().get("code") != 200, "过短用户名应被校验拦截"

    def test_register_duplicate_username(self):
        # Arrange：使用配置中已存在的账号名注册
        client = PortalClient()
        existed = client.module_cfg["username"]
        payload = {"username": existed, "password": "test123456", "icon": "", "phone": ""}
        # Act
        resp = client.post_json(PortalApi.REGISTER, payload)
        # Assert：重复用户名应被拦截
        assert resp.json().get("code") != 200, f"重复用户名 {existed} 应注册失败"

    def test_register_new_username_then_not_login(self):
        # Arrange：全新用户名（仅验证注册链路，不验证登录）
        client = PortalClient()
        payload = {"username": f"qa_{uuid.uuid4().hex[:8]}", "password": "test123456", "icon": "", "phone": ""}
        # Act
        resp = client.post_json(PortalApi.REGISTER, payload)
        # Assert：合法注册应成功（业务码 200）
        assert resp.status_code == 200, f"合法注册触发异常：{resp.text[:200]}"


class TestPortalLogin:
    """会员登录异常流。"""

    def test_login_wrong_password(self):
        # Arrange
        client = PortalClient()
        client.module_cfg["password"] = "wrong_password_123"
        # Act / Assert
        with pytest.raises(AssertionError, match="登录失败"):
            client.login()

    def test_login_nonexistent_user(self):
        # Arrange
        client = PortalClient()
        client.module_cfg["username"] = f"no_such_user_{uuid.uuid4().hex[:6]}"
        # Act / Assert
        with pytest.raises(AssertionError, match="登录失败"):
            client.login()


class TestMemberInfo:
    """会员信息接口鉴权。"""

    def test_member_info_after_login(self, portal):
        # Act
        resp = portal.get(PortalApi.MEMBER_INFO)
        # Assert
        body = portal.assert_business_ok(resp)
        assert body["data"].get("username"), "会员信息应包含 username"

    def test_member_info_without_token(self):
        # Arrange
        bare = PortalClient()
        # Act
        resp = bare.get(PortalApi.MEMBER_INFO)
        # Assert
        assert resp.status_code == 401, f"未鉴权应 401，实际 {resp.status_code}"
