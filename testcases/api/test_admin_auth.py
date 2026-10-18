"""后台鉴权专项：admin/info 与 token 有效性（P0，所有后台接口的前置）。"""
import pytest

from api.admin_api import AdminApi
from common.http_client import AdminClient

pytestmark = [pytest.mark.regression]


class TestAdminAuth:
    """登录态与 token 校验：伪造/缺失/篡改 token 必须被拦截。"""

    def test_admin_info_after_login(self, admin):
        # Act
        resp = admin.get(AdminApi.ADMIN_INFO)
        # Assert：登录态下能拿到当前管理员信息
        body = admin.assert_business_ok(resp)
        assert body["data"].get("username"), "管理员信息应包含 username"

    def test_admin_info_without_token(self):
        # Arrange：不登录的裸客户端
        bare = AdminClient()
        # Act
        resp = bare.get(AdminApi.ADMIN_INFO)
        # Assert：未携带 token 应返回 401
        assert resp.status_code == 401, f"未鉴权应 401，实际 {resp.status_code}"

    def test_admin_info_with_fake_token(self):
        # Arrange：伪造 token
        fake = AdminClient()
        fake.token = "eyJhbGciOiJIUzI1NiJ9.faked.faked"
        fake.session.headers.update(fake._auth_header())
        # Act
        resp = fake.get(AdminApi.ADMIN_INFO)
        # Assert：伪造 token 必须被拦截，不允许 500
        assert resp.status_code == 401, f"伪造 token 应 401，实际 {resp.status_code}"

    def test_admin_info_with_tampered_token(self, admin):
        # Arrange：取真实 token 篡改末位字符
        tampered = AdminClient()
        tampered.token = admin.token[:-1] + ("0" if admin.token[-1] != "0" else "1")
        tampered.session.headers.update(tampered._auth_header())
        # Act
        resp = tampered.get(AdminApi.ADMIN_INFO)
        # Assert：篡改后的 token 应失效（JWT 签名校验）
        assert resp.status_code == 401, f"篡改 token 应 401，实际 {resp.status_code}"
