import pytest

from api.portal_api import PortalApi

pytestmark = [pytest.mark.regression]


@pytest.fixture(scope="module")
def portal():
    client = PortalClient()
    client.login()
    return client


class TestProduct:
    """商品模块：详情、搜索、异常输入。"""

    def test_product_detail_normal(self, portal):
        # Act
        resp = portal.get(PortalApi.PRODUCT_DETAIL.format(id=1))
        # Assert
        body = portal.assert_business_ok(resp)
        assert body["data"]["id"] == 1 or body["data"] is not None

    def test_product_detail_not_exist(self, portal):
        # Act
        resp = portal.get(PortalApi.PRODUCT_DETAIL.format(id=99999999))
        # Assert：不存在商品应返回业务错误或空 data，不应 500
        assert resp.status_code != 500, "查询不存在商品触发 500 属缺陷"

    def test_search_keyword_normal(self, portal):
        # Act
        resp = portal.post_json(PortalApi.PRODUCT_SEARCH, {"keyword": "手机", "pageNum": 1, "pageSize": 5})
        # Assert
        portal.assert_business_ok(resp)

    def test_search_keyword_overlong(self, portal):
        # Arrange：超长关键字是经典健壮性用例
        keyword = "机" * 500
        # Act
        resp = portal.post_json(PortalApi.PRODUCT_SEARCH, {"keyword": keyword, "pageNum": 1, "pageSize": 5})
        # Assert
        assert resp.status_code != 500, "超长关键字触发 500 属缺陷，建议限制入参长度"

    def test_search_sql_injection_probe(self, portal):
        # Arrange：单引号探测（只验证不 500，不属于安全渗透）
        # Act
        resp = portal.post_json(PortalApi.PRODUCT_SEARCH, {"keyword": "a'b''c", "pageNum": 1, "pageSize": 5})
        # Assert
        assert resp.status_code != 500, "特殊字符触发 500 需排查 SQL 拼接"


class TestOrder:
    """下单 P0 链路：生成订单 → 订单列表 → 取消订单。"""

    def test_generate_order_requires_login(self):
        # Arrange
        bare = PortalClient()
        payload = {"cartItemIds": [1], "memberReceiveAddressId": 1}
        # Act
        resp = bare.post_json(PortalApi.ORDER_GENERATE, payload)
        # Assert
        assert resp.status_code == 401, "未登录下单应被拦截"

    def test_generate_order_empty_cart_items(self, portal):
        # Act
        resp = portal.post_json(PortalApi.ORDER_GENERATE, {"cartItemIds": [], "memberReceiveAddressId": 1})
        # Assert：空购物车下单应返回业务错误，不应 500
        assert resp.status_code != 500, "空购物车下单触发 500 属缺陷"
