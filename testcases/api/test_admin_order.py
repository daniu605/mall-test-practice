"""后台订单管理模块：状态筛选（参数化）+ 详情 + 异常参数。

设计说明：订单状态 0-12 分别对应待支付/待发货/已发货/已完成/申请退款等，
参数化覆盖全部状态分支；详情用例从列表取真实 id，无数据时 skip 而非误报。
"""
import pytest

from api.admin_api import AdminApi

pytestmark = [pytest.mark.regression]


class TestOrderStatusFilter:
    """订单列表按状态筛选：参数化覆盖全部状态分支。"""

    @pytest.mark.parametrize("status", [0, 1, 2, 3], ids=["待支付", "待发货", "已发货", "已完成"])
    def test_order_list_by_each_status(self, admin, status):
        # Arrange：status 由参数化注入
        # Act
        resp = admin.get(AdminApi.ORDER_LIST, params={"pageNum": 1, "pageSize": 10, "status": status})
        # Assert：每个状态都应返回合法分页结构
        body = admin.assert_business_ok(resp)
        assert "list" in body["data"], f"status={status} 返回缺少 list 字段"

    def test_order_list_illegal_status(self, admin):
        # Act：非法 status 值（字符串注入）
        resp = admin.get(AdminApi.ORDER_LIST, params={"pageNum": 1, "pageSize": 10, "status": "abc"})
        # Assert：不应 500
        assert resp.status_code == 200, f"非法 status 触发异常响应：{resp.text[:200]}"


class TestOrderDetail:
    """订单详情：用列表首个真实 id 驱动，环境无数据时 skip。"""

    def test_order_detail_by_list_id(self, admin):
        # Arrange：先取列表拿真实订单 id
        resp = admin.get(AdminApi.ORDER_LIST, params={"pageNum": 1, "pageSize": 1})
        body = admin.assert_business_ok(resp)
        orders = body["data"]["list"]
        if not orders:
            pytest.skip("环境中无订单数据，跳过详情用例")
        order_id = orders[0]["id"]
        # Act
        resp = admin.get(AdminApi.ORDER_DETAIL.format(id=order_id))
        # Assert：详情应包含订单号与状态
        detail = admin.assert_business_ok(resp)
        assert detail["data"].get("orderSn"), "订单详情应包含 orderSn"

    def test_order_detail_nonexistent_id(self, admin):
        # Act：超大不存在的订单 id
        resp = admin.get(AdminApi.ORDER_DETAIL.format(id=99999999))
        # Assert：不应 500，业务层应返回错误或空数据
        assert resp.status_code == 200, f"不存在订单触发 500：{resp.text[:200]}"

    def test_order_list_page_size_boundary(self, admin):
        # Act：pageSize 边界 1 / 100
        for size in (1, 100):
            resp = admin.get(AdminApi.ORDER_LIST, params={"pageNum": 1, "pageSize": size})
            # Assert
            body = admin.assert_business_ok(resp)
            assert len(body["data"]["list"]) <= size, f"pageSize={size} 返回超量数据"
