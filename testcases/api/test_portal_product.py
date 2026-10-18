"""前台商品搜索与详情：数据驱动 + 边界（复用 data/product_search.yaml 数据集）。"""
import pathlib

import pytest
import yaml

from api.portal_api import PortalApi

pytestmark = [pytest.mark.regression]

# 数据驱动：与后台商品搜索共用同一份 YAML 数据集，新增场景零代码改动
DATA_PATH = pathlib.Path(__file__).parent.parent.parent / "data" / "product_search.yaml"
with open(DATA_PATH, encoding="utf-8") as _f:
    _SEARCH_CASES = yaml.safe_load(_f)["cases"]


@pytest.mark.parametrize(
    "case",
    _SEARCH_CASES,
    ids=[c["name"] for c in _SEARCH_CASES],
)
class TestPortalSearchDataDriven:
    """前台搜索数据驱动：与后台共用数据集，交叉验证搜索链路一致性。"""

    def test_search_by_keyword(self, portal, case):
        # Arrange：case 由 YAML 注入
        # Act
        resp = portal.get(PortalApi.PRODUCT_SEARCH, params={"pageNum": 1, "pageSize": 10, "keyword": case["keyword"]})
        # Assert 1：双通道断言
        body = portal.assert_business_ok(resp)
        items = body["data"].get("productList", body["data"].get("list", []))
        # Assert 2：注入片段不应命中商品
        if case["expect_empty"]:
            assert items == [], f"关键词 {case['keyword'][:20]!r} 不应有搜索结果"
        else:
            assert isinstance(items, list), "搜索结果应为列表"


class TestPortalProductDetail:
    """商品详情：正常 id + 异常 id。"""

    def test_detail_by_search_first_item(self, portal):
        # Arrange：搜索拿真实商品 id
        resp = portal.get(PortalApi.PRODUCT_SEARCH, params={"pageNum": 1, "pageSize": 1, "keyword": "小米"})
        body = portal.assert_business_ok(resp)
        items = body["data"].get("productList", body["data"].get("list", []))
        if not items:
            pytest.skip("搜索无结果，跳过详情用例")
        product_id = items[0]["id"]
        # Act
        resp = portal.get(PortalApi.PRODUCT_DETAIL.format(id=product_id))
        # Assert：详情应包含商品名
        detail = portal.assert_business_ok(resp)
        assert detail["data"].get("name"), "商品详情应包含 name"

    def test_detail_nonexistent_id(self, portal):
        # Act
        resp = portal.get(PortalApi.PRODUCT_DETAIL.format(id=0))
        # Assert：不应 500
        assert resp.status_code == 200, f"不存在商品触发 500：{resp.text[:200]}"

    def test_detail_id_injection(self, portal):
        # Act：路径参数注入片段
        resp = portal.get(PortalApi.PRODUCT_DETAIL.format(id="1%20or%201=1"))
        # Assert：注入片段应被参数校验拦截（400/404/业务错误均可，绝不允许 500）
        assert resp.status_code != 500, f"路径注入触发 500：{resp.text[:200]}"

    def test_category_tree(self, portal):
        # Act：商品分类树（parentId=0 顶层）
        resp = portal.get(PortalApi.PRODUCT_CATEGORY, params={"parentId": 0})
        # Assert
        body = portal.assert_business_ok(resp)
        assert isinstance(body["data"], list) and len(body["data"]) > 0, "顶层分类不应为空"
