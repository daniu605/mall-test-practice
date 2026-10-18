import pytest

from api.admin_api import AdminApi
from common.http_client import AdminClient


@pytest.fixture(scope="module")
def admin():
    client = AdminClient()
    client.login()
    return client


@pytest.mark.smoke
@pytest.mark.critical
class TestAdminLogin:
    """后台登录：正常流 + 异常流（鉴权是所有接口的前置，属 P0）。"""

    def test_login_success(self):
        # Arrange
        client = AdminClient()
        # Act
        token = client.login()
        # Assert
        assert token, "登录成功应返回非空 token"

    def test_login_wrong_password(self):
        # Arrange
        client = AdminClient()
        client.module_cfg["password"] = "wrong_password_123"
        # Act / Assert
        with pytest.raises(AssertionError, match="登录失败"):
            client.login()

    def test_login_empty_username(self):
        # Arrange
        client = AdminClient()
        client.module_cfg["username"] = ""
        # Act / Assert
        with pytest.raises(AssertionError, match="登录失败"):
            client.login()


@pytest.mark.regression
class TestAdminProtectedApi:
    """未携带/携带非法 token 访问受保护接口，应被网关拦截。"""

    def test_access_without_token(self, admin):
        # Arrange
        bare = AdminClient()  # 不登录
        # Act
        resp = bare.get(AdminApi.PRODUCT_LIST, params={"pageNum": 1, "pageSize": 5})
        # Assert：mall 未鉴权返回 401
        assert resp.status_code == 401, f"未携带 token 应返回 401，实际 {resp.status_code}"

    def test_access_with_valid_token(self, admin):
        # Act
        resp = admin.get(AdminApi.PRODUCT_LIST, params={"pageNum": 1, "pageSize": 5})
        # Assert
        admin.assert_business_ok(resp)
