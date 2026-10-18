import pathlib

import pytest
import yaml

from api.admin_api import AdminApi

pytestmark = [pytest.mark.regression]

# 数据驱动：用例数据外置到 data/product_search.yaml，新增搜索场景零代码改动
DATA_PATH = pathlib.Path(__file__).parent.parent.parent / "data" / "product_search.yaml"
with open(DATA_PATH, encoding="utf-8") as _f:
    _SEARCH_CASES = yaml.safe_load(_f)["cases"]


class TestAdminProduct:
    """商品管理模块：分页、筛选、异常参数。"""

    def test_list_default_pagination(self, admin):
        # Act
        resp = admin.get(AdminApi.PRODUCT_LIST, params={"pageNum": 1, "pageSize": 5})
        # Assert
        body = admin.assert_business_ok(resp)
        assert body["data"]["pageNum"] == 1
        assert len(body["data"]["list"]) <= 5

    def test_list_page_out_of_range_returns_empty(self, admin):
        # Act
        resp = admin.get(AdminApi.PRODUCT_LIST, params={"pageNum": 9999, "pageSize": 5})
        # Assert：页码越界应返回空列表而非报错
        body = admin.assert_business_ok(resp)
        assert body["data"]["list"] == []

    def test_list_negative_page_size(self, admin):
        # Act
        resp = admin.get(AdminApi.PRODUCT_LIST, params={"pageNum": 1, "pageSize": -1})
        # Assert：非法分页参数不应导致 500
        assert resp.status_code == 200, f"非法 pageSize 触发异常响应：{resp.text[:200]}"

    def test_brand_list(self, admin):
        # Act
        resp = admin.get(AdminApi.BRAND_LIST, params={"pageNum": 1, "pageSize": 10})
        # Assert
        body = admin.assert_business_ok(resp)
        assert isinstance(body["data"]["list"], list)


class TestAdminOrder:
    """后台订单模块：查询与状态筛选。"""

    def test_order_list_by_status(self, admin):
        # Arrange：status=0 待支付
        # Act
        resp = admin.get(AdminApi.ORDER_LIST, params={"pageNum": 1, "pageSize": 10, "status": 0})
        # Assert
        body = admin.assert_business_ok(resp)
        assert "list" in body["data"]


@pytest.mark.parametrize(
    "case",
    _SEARCH_CASES,
    ids=[c["name"] for c in _SEARCH_CASES],
)
class TestProductSearchDataDriven:
    """商品搜索数据驱动用例：数据来源于 data/product_search.yaml。

    覆盖正常流 / 边界（单字符、超长串）/ 异常（SQL 注入片段）三类场景，
    断言要点：接口不 500、超长与注入片段不应命中商品（防 LIKE 拼接注入）。
    """

    def test_search_by_keyword(self, admin, case):
        # Arrange：case 参数由 YAML 注入（keyword + expect_empty）
        # Act
        resp = admin.get(AdminApi.PRODUCT_LIST, params={"pageNum": 1, "pageSize": 10, "keyword": case["keyword"]})
        # Assert 1：HTTP 与业务码双通道校验，不允许 500
        body = admin.assert_business_ok(resp)
        items = body["data"]["list"]
        # Assert 2：按数据文件中的预期校验命中结果
        if case["expect_empty"]:
            assert items == [], f"关键词 {case['keyword'][:20]!r} 不应有搜索结果，实际 {len(items)} 条"
        else:
            assert isinstance(items, list), "搜索结果应为列表"

