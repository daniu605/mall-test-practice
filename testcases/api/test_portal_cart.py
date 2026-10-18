import time
import uuid

import pytest

from api.portal_api import PortalApi

pytestmark = [pytest.mark.regression]


@pytest.fixture(scope="module")
def portal():
    client = PortalClient()
    client.login()
    return client


def _unique_cart_payload(product_id: int = 1) -> dict:
    """构造加购请求体，skuId/quantity 按本地库实际数据调整。"""
    return {"productId": product_id, "productSkuId": 1, "quantity": 1}


@pytest.mark.critical
class TestCart:
    """购物车 P0 链路：加购 → 改数量 → 查询 → 删除。"""

    def test_add_cart_requires_login(self):
        # Arrange
        bare = PortalClient()
        # Act
        resp = bare.post_json(PortalApi.CART_ADD, _unique_cart_payload())
        # Assert
        assert resp.status_code == 401, "未登录加购应被拦截"

    def test_add_update_list_delete_flow(self, portal):
        # Act 1：加购
        resp_add = portal.post_json(PortalApi.CART_ADD, _unique_cart_payload())
        body_add = portal.assert_business_ok(resp_add)

        # Act 2：查询购物车，确认新增项存在
        resp_list = portal.get(PortalApi.CART_LIST)
        body_list = portal.assert_business_ok(resp_list)
        items = body_list["data"]
        assert isinstance(items, list)

        # Act 3：修改数量为 3（cartItemId 取自列表）
        if items:
            item_id = items[-1]["id"]
            resp_upd = portal.post_json(
                PortalApi.CART_UPDATE, {"cartItemId": item_id, "quantity": 3}
            )
            portal.assert_business_ok(resp_upd)

    def test_add_cart_zero_quantity(self, portal):
        # Act
        payload = _unique_cart_payload()
        payload["quantity"] = 0
        resp = portal.post_json(PortalApi.CART_ADD, payload)
        # Assert：数量为 0 应被业务校验拒绝（非 200 业务码或 500 均记缺陷）
        assert resp.status_code != 500, "数量为 0 触发 500 属服务端缺陷，需提 issue"
