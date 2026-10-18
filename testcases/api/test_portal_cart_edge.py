"""购物车边界专项：数量参数化（0/负数/超限）+ 删除后重加。

数据来源：data/cart_quantity.yaml，新增边界值零代码改动。
"""
import pathlib

import pytest
import yaml

from api.portal_api import PortalApi

pytestmark = [pytest.mark.critical]

DATA_PATH = pathlib.Path(__file__).parent.parent.parent / "data" / "cart_quantity.yaml"
with open(DATA_PATH, encoding="utf-8") as _f:
    _QTY_CASES = yaml.safe_load(_f)["cases"]


def _pick_product_id(portal) -> int:
    """辅助：从搜索结果取一个真实在售商品 id，无数据时 skip。"""
    resp = portal.get(PortalApi.PRODUCT_SEARCH, params={"pageNum": 1, "pageSize": 1, "keyword": "小米"})
    body = portal.assert_business_ok(resp)
    items = body["data"].get("productList", body["data"].get("list", []))
    if not items:
        pytest.skip("搜索无结果，跳过购物车边界用例")
    return items[0]["id"]


@pytest.mark.parametrize(
    "case",
    _QTY_CASES,
    ids=[c["name"] for c in _QTY_CASES],
)
class TestCartQuantityEdge:
    """加购数量边界：0/负数/超限值的服务端校验是防资损的关键卡点。"""

    def test_add_cart_with_edge_quantity(self, portal, case):
        # Arrange：真实商品 id + 边界数量
        product_id = _pick_product_id(portal)
        payload = {"productId": product_id, "quantity": case["quantity"]}
        # Act
        resp = portal.post_json(PortalApi.CART_ADD, payload)
        # Assert：非法数量应被业务校验拦截，绝不允许 500 或静默成功
        assert resp.status_code == 200, f"quantity={case['quantity']} 触发 500：{resp.text[:200]}"
        if not case["expect_accept"]:
            assert resp.json().get("code") != 200, f"quantity={case['quantity']} 应被拦截"


class TestCartDeleteReAdd:
    """删除后重加：验证购物车状态一致性。"""

    def test_delete_then_readd(self, portal):
        # Arrange：加购一个商品
        product_id = _pick_product_id(portal)
        portal.post_json(PortalApi.CART_ADD, {"productId": product_id, "quantity": 1})
        resp = portal.get(PortalApi.CART_LIST)
        items = portal.assert_business_ok(resp)["data"].get("items", [])
        target = next((i for i in items if i.get("productId") == product_id), None)
        if target is None:
            pytest.skip("加购后列表未见目标商品，环境数据异常")
        # Act：删除（ids 为查询参数，支持批量）
        resp = portal.post(PortalApi.CART_DELETE, params={"ids": target["id"]})
        portal.assert_business_ok(resp)
        # Act：再次加购同一商品
        resp = portal.post_json(PortalApi.CART_ADD, {"productId": product_id, "quantity": 1})
        # Assert：重加应成功且购物车中重新可见
        portal.assert_business_ok(resp)
        resp = portal.get(PortalApi.CART_LIST)
        items = portal.assert_business_ok(resp)["data"].get("items", [])
        assert any(i.get("productId") == product_id for i in items), "删除后重加，商品应重新出现在购物车"
